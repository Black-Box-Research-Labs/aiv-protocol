"""
aiv/cli/main.py

CLI application entry point.
"""

from __future__ import annotations

import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from aiv.lib.config import AIVConfig
from aiv.lib.models import ValidationFinding, ValidationStatus
from aiv.lib.validators.pipeline import ValidationPipeline
from aiv.svp.cli.main import svp_app

app = typer.Typer(
    name="aiv",
    help="AIV Protocol Suite - Evidence-based engineering verification",
    no_args_is_help=True,
)
app.add_typer(svp_app, name="svp")
console = Console()


@app.command()
def check(
    body: str | None = typer.Argument(None, help="PR body text or path to file containing it"),
    diff: Path | None = typer.Option(None, "--diff", "-d", help="Path to diff file for anti-cheat scanning"),
    strict: bool = typer.Option(True, "--strict/--no-strict", help="Treat warnings as errors"),
    config: Path | None = typer.Option(None, "--config", "-c", help="Path to .aiv.yml configuration file"),
    audit_links: bool = typer.Option(False, "--audit-links", help="Verify evidence URLs are reachable via HTTP HEAD"),
) -> None:
    """
    Validate a Verification Packet locally.

    Examples:
        aiv check "# AIV Verification Packet..."
        aiv check pr_body.md --diff changes.diff
        cat pr.md | aiv check -
    """
    # Load configuration
    if config:
        cfg = AIVConfig.from_file(config).model_copy(update={"strict_mode": strict})
    else:
        cfg = AIVConfig(strict_mode=strict)

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
    pipeline = ValidationPipeline(cfg, audit_links=audit_links)
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
        console.print(
            Panel(
                f"[red]Validation Failed[/red]\n"
                f"{len(result.errors)} blocking error(s), {len(result.warnings)} warning(s)",
                title="[X] Result",
                border_style="red",
            )
        )
        raise typer.Exit(1)
    else:
        packet = result.packet
        claims_count = len(packet.claims) if packet else 0
        version = packet.version if packet else "?"
        console.print(
            Panel(
                f"[green]Validation Passed[/green]\nPacket version: {version}\nClaims: {claims_count}",
                title="[OK] Result",
                border_style="green",
            )
        )


@app.command()
def init(
    path: Path = typer.Argument(Path("."), help="Repository path to initialize"),
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
            'version: "1.0"\n'
            "strict_mode: true\n",
            encoding="utf-8",
        )
        console.print(f"[green]Created:[/green] {aiv_yml}")

    console.print(f"[green][OK] AIV Protocol initialized in {path}[/green]")
    console.print("[dim]Tip: Use [bold]aiv generate <name>[/bold] to create a verification packet.[/dim]")


@app.command()
def audit(
    packets_dir: Path = typer.Argument(Path(".github/aiv-packets"), help="Directory containing verification packets"),
    fix: bool = typer.Option(False, "--fix", help="Auto-fix COMMIT_PENDING and CLASS_E_NO_URL where possible"),
) -> None:
    """
    Audit all verification packets for quality issues.

    Checks for problems the validation pipeline does not catch:
    commit SHA traceability, Class E link immutability, TODO remnants,
    missing Class F for bug-fix claims, and more.

    Examples:
        aiv audit
        aiv audit --fix
        aiv audit .github/aiv-packets --fix
    """
    from aiv.lib.auditor import AuditSeverity, PacketAuditor

    auditor = PacketAuditor()
    result = auditor.audit(packets_dir, fix=fix)

    if not result.findings:
        console.print(
            Panel(
                f"[green]All {result.packets_scanned} packets clean[/green]",
                title="[OK] Audit",
                border_style="green",
            )
        )
        return

    # Build findings table
    table = Table(title="Audit Findings", show_lines=True)
    table.add_column("Severity", style="bold", width=8)
    table.add_column("Packet", width=30)
    table.add_column("Finding", width=20)
    table.add_column("Message", width=50)

    severity_styles = {
        AuditSeverity.ERROR: "[red]ERROR[/red]",
        AuditSeverity.WARNING: "[yellow]WARN[/yellow]",
        AuditSeverity.INFO: "[blue]INFO[/blue]",
    }

    for f in result.findings:
        sev_text = severity_styles.get(f.severity, str(f.severity))
        short_name = f.packet_name.replace("VERIFICATION_PACKET_", "").replace(".md", "")
        table.add_row(sev_text, short_name, f.finding_type, f.message[:80])

    console.print(table)

    # Summary
    if fix and result.fixed:
        console.print(f"\n[green]Auto-fixed {len(result.fixed)} packet(s).[/green]")

    console.print(
        Panel(
            f"Scanned: {result.packets_scanned} | "
            f"Issues: {result.packets_with_issues} | "
            f"Errors: {result.error_count} | "
            f"Warnings: {result.warning_count}" + (f" | Fixed: {len(result.fixed)}" if fix else ""),
            title="[X] Audit Summary" if result.error_count > 0 else "[!] Audit Summary",
            border_style="red" if result.error_count > 0 else "yellow",
        )
    )

    if result.error_count > 0:
        raise typer.Exit(1)


@app.command()
def generate(
    name: str = typer.Argument(..., help="Short name for the packet (used in filename, e.g. 'auth-fix')"),
    tier: str = typer.Option("R1", "--tier", "-t", help="Risk tier: R0, R1, R2, R3"),
    output_dir: Path = typer.Option(
        Path(".github/aiv-packets"), "--output", "-o", help="Directory to write the packet file"
    ),
    rationale: str = typer.Option("", "--rationale", "-r", help="Classification rationale"),
    skip_checks: bool = typer.Option(False, "--skip-checks", help="Skip running local checks (pytest/ruff/mypy)"),
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

    # Detect git context for auto-population
    git_ctx: dict[str, str] = {}
    local_results = ""

    if not skip_checks:
        git_ctx = _detect_git_context()
        console.print("[dim]Auto-detecting git context...[/dim]")
        if git_ctx.get("owner") and git_ctx.get("repo"):
            console.print(f"  Repo: [bold]{git_ctx['owner']}/{git_ctx['repo']}[/bold]")
        if git_ctx.get("branch"):
            console.print(f"  Branch: [bold]{git_ctx['branch']}[/bold]")
        if git_ctx.get("issue_number"):
            console.print(f"  Issue: [bold]#{git_ctx['issue_number']}[/bold]")

        # Run local checks to auto-populate Class A
        console.print("[dim]Running local checks (pytest, ruff, mypy)...[/dim]")
        local_results = _run_local_checks()
        console.print("  Done.")

    # Build evidence sections based on tier + auto-populated context
    evidence_sections = _build_evidence_sections(tier_upper, scope_lines, git_ctx, local_results)

    # SoD mode
    sod = "S0" if tier_upper in ("R0", "R1") else "S1"

    # Auto-detect classified_by from git config
    classified_by = "TODO"
    try:
        import subprocess

        r = subprocess.run(
            ["git", "config", "user.name"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if r.returncode == 0 and r.stdout.strip():
            classified_by = r.stdout.strip()
    except Exception:
        pass

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
  classification_rationale: "{rationale or "TODO: Describe why this tier was chosen"}"
  classified_by: "{classified_by}"
  classified_at: "{now}"
```

## Claim(s)

1. [Component/Function] [assertive verb: rejects/returns/ensures/prevents/limits] [result] under [condition].
   - *Example: "The `PacketParser` rejects packets where the version header is missing."*
2. [Component] prevents [unwanted state] during [process/input].
   - *Example: "The `LinkValidator` prevents mutable branch refs from passing E004."*
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
    console.print("  Fill in the TODO sections, then commit with your functional file.")


def _detect_git_scope() -> str:
    """Best-effort detection of changed files via git."""
    import subprocess

    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-status"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode != 0 or not result.stdout.strip():
            # Fallback to unstaged changes
            result = subprocess.run(
                ["git", "diff", "--name-status"],
                capture_output=True,
                text=True,
                timeout=5,
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


def _detect_git_context() -> dict[str, str]:
    """Best-effort detection of git context for auto-populating evidence."""
    import os
    import re
    import subprocess

    ctx: dict[str, str] = {}

    try:
        # Current branch
        branch = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if branch.returncode == 0 and branch.stdout.strip():
            ctx["branch"] = branch.stdout.strip()

        # Remote URL → owner/repo
        remote = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if remote.returncode == 0 and remote.stdout.strip():
            url = remote.stdout.strip()
            # Parse owner/repo from HTTPS or SSH URL
            m = re.search(r"[:/]([^/]+)/([^/.]+?)(?:\.git)?$", url)
            if m:
                ctx["owner"] = m.group(1)
                ctx["repo"] = m.group(2)

        # Current HEAD SHA
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if head.returncode == 0 and head.stdout.strip():
            ctx["head_sha"] = head.stdout.strip()

        # Try to parse issue number from branch name (e.g., fix/42-bug, feat-123)
        if "branch" in ctx:
            issue_match = re.search(r"(?:^|[/\-_])(\d+)", ctx["branch"])
            if issue_match:
                ctx["issue_number"] = issue_match.group(1)

    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass

    # Check for GITHUB_TOKEN
    token = os.environ.get("GITHUB_TOKEN", "")
    if token:
        ctx["has_token"] = "true"

    return ctx


def _fetch_latest_ci_url(owner: str, repo: str) -> str:
    """Fetch the latest successful CI run URL from GitHub API (best-effort)."""
    import json
    import os
    from urllib.request import Request, urlopen

    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        return ""

    try:
        url = f"https://api.github.com/repos/{owner}/{repo}/actions/runs?status=success&per_page=1"
        req = Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
            },
        )
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        runs = data.get("workflow_runs", [])
        if runs:
            return runs[0].get("html_url", "")
    except Exception:
        pass

    return ""


def _fetch_issue_title(owner: str, repo: str, issue_number: str) -> str:
    """Fetch issue title from GitHub API (best-effort)."""
    import json
    import os
    from urllib.request import Request, urlopen

    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        return ""

    try:
        url = f"https://api.github.com/repos/{owner}/{repo}/issues/{issue_number}"
        req = Request(
            url,
            headers={
                "Accept": "application/vnd.github+json",
                "Authorization": f"Bearer {token}",
            },
        )
        with urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        return data.get("title", "")
    except Exception:
        pass

    return ""


def _run_local_checks() -> str:
    """Run local checks (pytest, ruff, mypy) and return results summary."""
    import subprocess

    results = []

    # pytest
    try:
        r = subprocess.run(
            ["python", "-m", "pytest", "--tb=no", "-q"],
            capture_output=True,
            text=True,
            timeout=120,
        )
        last_line = r.stdout.strip().split("\n")[-1] if r.stdout.strip() else ""
        if last_line:
            results.append(f"- pytest: {last_line}")
    except Exception:
        results.append("- pytest: TODO (run manually)")

    # ruff check
    try:
        r = subprocess.run(
            ["python", "-m", "ruff", "check", "src/", "tests/"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if r.returncode == 0:
            results.append("- ruff check: All checks passed")
        else:
            count = r.stdout.strip().count("\n") + 1 if r.stdout.strip() else 0
            results.append(f"- ruff check: {count} error(s)")
    except Exception:
        results.append("- ruff check: TODO (run manually)")

    # mypy
    try:
        r = subprocess.run(
            ["python", "-m", "mypy", "src/aiv/"],
            capture_output=True,
            text=True,
            timeout=60,
        )
        last_line = r.stdout.strip().split("\n")[-1] if r.stdout.strip() else ""
        if last_line:
            results.append(f"- mypy: {last_line}")
    except Exception:
        results.append("- mypy: TODO (run manually)")

    return "\n".join(results) if results else "- TODO: Test results"


def _build_evidence_sections(
    tier: str,
    scope_lines: str,
    git_ctx: dict[str, str] | None = None,
    local_results: str = "",
) -> str:
    """Build evidence section markdown based on risk tier + auto-populated context."""
    sections = []
    ctx = git_ctx or {}
    owner = ctx.get("owner", "")
    repo = ctx.get("repo", "")
    head_sha = ctx.get("head_sha", "")
    issue_number = ctx.get("issue_number", "")

    # Auto-fetch CI URL and issue info if GitHub token available
    ci_url = ""
    issue_link = ""
    if owner and repo:
        ci_url = _fetch_latest_ci_url(owner, repo)
        if issue_number:
            issue_title = _fetch_issue_title(owner, repo, issue_number)
            if issue_title:
                issue_link = (
                    f"[#{issue_number}: {issue_title}](https://github.com/{owner}/{repo}/issues/{issue_number})"
                )
            else:
                issue_link = f"https://github.com/{owner}/{repo}/issues/{issue_number}"

    # Class E — required by parser for all tiers (structurally mandatory)
    if issue_link:
        class_e_link = issue_link
    else:
        class_e_link = "TODO: SHA-pinned link to spec/issue/directive"

    sections.append(f"""### Class E (Intent Alignment)

- **Link:** {class_e_link}
- **Requirements Verified:**
  1. TODO: Requirement 1
  2. TODO: Requirement 2""")

    # Class B — always required
    # Auto-generate SHA-pinned links if we have owner/repo/sha
    if owner and repo and head_sha:
        scope_header = (
            f"**Scope Inventory** (SHA: [`{head_sha[:7]}`](https://github.com/{owner}/{repo}/tree/{head_sha}))"
        )
    else:
        scope_header = "**Scope Inventory (required)**"

    sections.append(f"""### Class B (Referential Evidence)

{scope_header}

- Modified:
{scope_lines}""")

    # Class A — always required
    if ci_url:
        class_a_ci = f"- **CI Run:** [{ci_url.split('/')[-1]}]({ci_url})"
    else:
        class_a_ci = "- CI Run: TODO (set GITHUB_TOKEN to auto-populate)"

    if local_results:
        class_a_local = f"- **Local results:**\n{local_results}"
    else:
        class_a_local = '- TODO: Test results (e.g., "422/422 pytest tests pass")'

    sections.append(f"""### Class A (Execution Evidence)

{class_a_ci}
{class_a_local}""")

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
        sections.append("""### Class F (Provenance Evidence)

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
        table.add_row(finding.rule_id, finding.location or "-", finding.message, finding.suggestion or "-")

    console.print(table)


if __name__ == "__main__":
    app()
