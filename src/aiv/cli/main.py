"""
aiv/cli/main.py

CLI application entry point.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from aiv.lib.models import ValidationStatus, ValidationFinding
from aiv.lib.validators.pipeline import ValidationPipeline
from aiv.lib.config import AIVConfig

app = typer.Typer(
    name="aiv",
    help="AIV Protocol Suite - Evidence-based engineering verification",
    no_args_is_help=True,
)
console = Console()


@app.command()
def check(
    body: Optional[str] = typer.Argument(
        None,
        help="PR body text or path to file containing it"
    ),
    diff: Optional[Path] = typer.Option(
        None,
        "--diff", "-d",
        help="Path to diff file for anti-cheat scanning"
    ),
    strict: bool = typer.Option(
        True,
        "--strict/--no-strict",
        help="Treat warnings as errors"
    ),
    config: Optional[Path] = typer.Option(
        None,
        "--config", "-c",
        help="Path to .aiv.yml configuration file"
    ),
) -> None:
    """
    Validate a Verification Packet locally.

    Examples:
        aiv check "# AIV Verification Packet..."
        aiv check pr_body.md --diff changes.diff
        cat pr.md | aiv check -
    """
    # Load configuration
    cfg = AIVConfig.from_file(config) if config else AIVConfig()
    cfg.strict_mode = strict

    # Read body from argument, file, or stdin
    if body == "-":
        body_text = sys.stdin.read()
    elif body and Path(body).exists():
        body_text = Path(body).read_text(encoding="utf-8")
    elif body:
        body_text = body
    else:
        console.print("[red]Error:[/red] No packet body provided")
        raise typer.Exit(1)

    # Run full pipeline
    pipeline = ValidationPipeline(cfg)
    diff_text = diff.read_text(encoding="utf-8") if diff and diff.exists() else None
    result = pipeline.validate(body_text, diff=diff_text)

    # Display results
    if result.errors:
        _display_findings(result.errors, "Blocking Errors", "red")

    if result.warnings:
        _display_findings(result.warnings, "Warnings", "yellow")

    if result.info:
        _display_findings(result.info, "Info", "blue")

    # Summary
    if result.status == ValidationStatus.FAIL:
        console.print(Panel(
            f"[red]Validation Failed[/red]\n"
            f"{len(result.errors)} blocking error(s), {len(result.warnings)} warning(s)",
            title="[X] Result",
            border_style="red"
        ))
        raise typer.Exit(1)
    else:
        packet = result.packet
        claims_count = len(packet.claims) if packet else 0
        version = packet.version if packet else "?"
        console.print(Panel(
            f"[green]Validation Passed[/green]\n"
            f"Packet version: {version}\n"
            f"Claims: {claims_count}",
            title="[OK] Result",
            border_style="green"
        ))


@app.command()
def init(
    path: Path = typer.Argument(
        Path("."),
        help="Repository path to initialize"
    ),
) -> None:
    """
    Initialize AIV Protocol in a repository.

    Creates:
    - .aiv.yml configuration file
    """
    aiv_yml = path / ".aiv.yml"
    if aiv_yml.exists():
        console.print(f"[yellow]Warning:[/yellow] {aiv_yml} already exists, skipping.")
    else:
        aiv_yml.write_text(
            "# AIV Protocol Configuration\n"
            "# See: https://github.com/ImmortalDemonGod/aiv-protocol\n"
            "\n"
            "version: \"1.0\"\n"
            "strict_mode: true\n",
            encoding="utf-8",
        )
        console.print(f"[green]Created:[/green] {aiv_yml}")

    console.print(f"[green][OK] AIV Protocol initialized in {path}[/green]")


@app.command()
def generate(
    name: str = typer.Argument(
        ...,
        help="Short name for the packet (used in filename, e.g. 'auth-fix')"
    ),
    tier: str = typer.Option(
        "R1",
        "--tier", "-t",
        help="Risk tier: R0, R1, R2, R3"
    ),
    output_dir: Path = typer.Option(
        Path(".github/aiv-packets"),
        "--output", "-o",
        help="Directory to write the packet file"
    ),
    rationale: str = typer.Option(
        "",
        "--rationale", "-r",
        help="Classification rationale"
    ),
) -> None:
    """
    Generate a verification packet scaffold.

    Creates a pre-filled packet file with classification, claim stubs,
    and evidence section headers appropriate for the chosen risk tier.

    Examples:
        aiv generate auth-fix --tier R2
        aiv generate cleanup --tier R0 --rationale "Remove dead code"
    """
    from datetime import datetime, timezone

    # Normalize name for filename
    safe_name = name.upper().replace("-", "_").replace(" ", "_")
    filename = f"VERIFICATION_PACKET_{safe_name}.md"
    filepath = output_dir / filename

    if filepath.exists():
        console.print(f"[yellow]Warning:[/yellow] {filepath} already exists.")
        overwrite = typer.confirm("Overwrite?", default=False)
        if not overwrite:
            raise typer.Exit(0)

    # Validate tier
    tier_upper = tier.upper().strip()
    if tier_upper not in ("R0", "R1", "R2", "R3"):
        console.print(f"[red]Error:[/red] Invalid tier '{tier}'. Use R0, R1, R2, or R3.")
        raise typer.Exit(1)

    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    # Detect changed files via git (best-effort)
    scope_lines = _detect_git_scope()

    # Build evidence sections based on tier
    evidence_sections = _build_evidence_sections(tier_upper, scope_lines)

    # SoD mode
    sod = "S0" if tier_upper in ("R0", "R1") else "S1"

    packet = f"""# AIV Verification Packet (v2.1)

**Commit:** `pending`  
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: {tier_upper}
  sod_mode: {sod}
  critical_surfaces: []
  blast_radius: TODO
  classification_rationale: "{rationale or 'TODO: Describe why this tier was chosen'}"
  classified_by: "TODO"
  classified_at: "{now}"
```

## Claim(s)

1. TODO: Primary claim — what changed and why.
2. TODO: Quality claim — tests pass, no regressions.
3. No existing tests were modified or deleted during this change.

---

## Evidence

{evidence_sections}

---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.

---

## Summary

TODO: One-line summary of the change.
"""

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)
    filepath.write_text(packet, encoding="utf-8")

    console.print(f"[green]Created:[/green] {filepath}")
    console.print(f"  Risk tier: [bold]{tier_upper}[/bold] | SoD: {sod}")
    console.print(f"  Fill in the TODO sections, then commit with your functional file.")


def _detect_git_scope() -> str:
    """Best-effort detection of changed files via git."""
    import subprocess

    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-status"],
            capture_output=True, text=True, timeout=5,
        )
        if result.returncode != 0 or not result.stdout.strip():
            # Fallback to unstaged changes
            result = subprocess.run(
                ["git", "diff", "--name-status"],
                capture_output=True, text=True, timeout=5,
            )
        if result.returncode == 0 and result.stdout.strip():
            lines = []
            for line in result.stdout.strip().split("\n"):
                parts = line.split("\t", 1)
                if len(parts) == 2:
                    status, path = parts
                    if status.startswith("A"):
                        lines.append(f"  - `{path}` (new)")
                    elif status.startswith("M"):
                        lines.append(f"  - `{path}`")
                    elif status.startswith("D"):
                        lines.append(f"  - `{path}` (deleted)")
                    else:
                        lines.append(f"  - `{path}`")
            if lines:
                return "\n".join(lines)
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    return "  - TODO: list modified files"


def _build_evidence_sections(tier: str, scope_lines: str) -> str:
    """Build evidence section markdown based on risk tier."""
    sections = []

    # Class E — required for R1+
    if tier in ("R1", "R2", "R3"):
        sections.append("""### Class E (Intent Alignment)

- **Link:** TODO: SHA-pinned link to spec/issue/directive
- **Requirements Verified:**
  1. TODO: Requirement 1
  2. TODO: Requirement 2""")

    # Class B — always required
    sections.append(f"""### Class B (Referential Evidence)

**Scope Inventory (required)**

- Modified:
{scope_lines}""")

    # Class A — always required
    sections.append("""### Class A (Execution Evidence)

- TODO: Test results (e.g., "84/84 pytest tests pass")""")

    # Class C — required for R2+
    if tier in ("R2", "R3"):
        sections.append("""### Class C (Negative Evidence)

- TODO: No regressions found. Describe search scope and method.""")

    # Class D — required for R3
    if tier == "R3":
        sections.append("""### Class D (Differential Evidence)

- TODO: Before/after diff of critical behavior.""")

    # Class F — required for R3, optional R2
    if tier in ("R2", "R3"):
        sections.append("""### Class F (Conservation Evidence)

**Claim 3: No regressions**
- No test files modified or deleted. Full test suite passes.""")

    return "\n\n".join(sections)


def _display_findings(findings: list[ValidationFinding], title: str, color: str) -> None:
    """Display findings in a formatted table."""
    table = Table(title=title, border_style=color)
    table.add_column("Rule", style="bold")
    table.add_column("Location")
    table.add_column("Message")
    table.add_column("Suggestion", style="dim")

    for finding in findings:
        table.add_row(
            finding.rule_id,
            finding.location or "-",
            finding.message,
            finding.suggestion or "-"
        )

    console.print(table)


if __name__ == "__main__":
    app()
