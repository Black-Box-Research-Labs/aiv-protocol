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
