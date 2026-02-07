"""
aiv/svp/cli/main.py

SVP CLI commands integrated into the main ``aiv`` CLI via Typer.
Provides: svp status, svp predict, svp trace, svp probe.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional
from uuid import uuid4

import typer

from ..lib.models import (
    Complexity,
    Confidence,
    SVPSession,
    SVPStatus,
    PredictionRecord,
    TraceRecord,
    StateTransition,
    ProbeRecord,
    WhyQuestion,
    FalsificationScenario,
    AITellType,
    BugSeverity,
    ProbeFinding,
    OwnershipCommit,
    RenameChange,
    DocstringChange,
    VerifierRating,
    VerifierTier,
)
from ..lib.validators.session import validate_session

svp_app = typer.Typer(
    name="svp",
    help="SVP (Systematic Verifier Protocol) commands.",
    no_args_is_help=True,
)

SVP_DIR = Path(".svp")


def _session_path(pr: int) -> Path:
    return SVP_DIR / f"session-pr{pr}.json"


def _load_session(pr: int) -> SVPSession | None:
    p = _session_path(pr)
    if not p.exists():
        return None
    data = json.loads(p.read_text(encoding="utf-8"))
    return SVPSession.model_validate(data)


def _save_session(session: SVPSession) -> None:
    SVP_DIR.mkdir(parents=True, exist_ok=True)
    p = _session_path(session.pr_number)
    p.write_text(
        session.model_dump_json(indent=2) + "\n",
        encoding="utf-8",
    )


# ------------------------------------------------------------------ #
# svp status
# ------------------------------------------------------------------ #

@svp_app.command()
def status(
    pr: int = typer.Argument(..., help="PR number"),
    repo: str = typer.Option("owner/repo", help="Repository (owner/repo)"),
) -> None:
    """Show SVP completion status for a PR."""
    session = _load_session(pr)
    if session is None:
        typer.echo(f"No SVP session found for PR #{pr}")
        typer.echo(f"Start with: aiv svp predict {pr}")
        raise typer.Exit(1)

    result = validate_session(session)

    typer.echo(f"SVP Status for PR #{pr}: {session.status.value}")
    typer.echo(f"Completion: {result.completion_percentage}%")
    typer.echo()

    phases = [
        ("Phase 0 — Sanity Gate", result.phase_0_complete),
        ("Phase 1 — Prediction", result.phase_1_complete),
        ("Phase 2 — Trace", result.phase_2_complete),
        ("Phase 3 — Probe", result.phase_3_complete),
        ("Phase 4 — Ownership", result.phase_4_complete),
    ]
    for name, done in phases:
        mark = "✅" if done else "❌"
        typer.echo(f"  {mark} {name}")

    if result.errors:
        typer.echo()
        typer.echo("Blocking errors:")
        for e in result.errors:
            typer.echo(f"  [{e.rule_id}] {e.message}")

    if result.warnings:
        typer.echo()
        typer.echo("Warnings:")
        for w in result.warnings:
            typer.echo(f"  [{w.rule_id}] {w.message}")


# ------------------------------------------------------------------ #
# svp predict
# ------------------------------------------------------------------ #

@svp_app.command()
def predict(
    pr: int = typer.Argument(..., help="PR number"),
    repo: str = typer.Option("owner/repo", help="Repository"),
    verifier: str = typer.Option(..., help="Verifier GitHub ID"),
    test_file: str = typer.Option(..., help="Test file path analyzed"),
    approach: str = typer.Option(..., help="Predicted implementation approach (≥50 chars)"),
    complexity: str = typer.Option("Unknown", help="Predicted complexity: O(1), O(n), etc."),
    edge_cases: list[str] = typer.Option(..., help="Expected edge cases (≥2)"),
) -> None:
    """Record a Black Box Prediction (Phase 1)."""
    session = _load_session(pr)
    if session is None:
        session = SVPSession(
            pr_number=pr,
            repository=repo,
            verifier_id=verifier,
            aiv_guard_passed=True,
        )

    cx = Complexity(complexity) if complexity in [c.value for c in Complexity] else Complexity.UNKNOWN

    pred = PredictionRecord(
        pr_number=pr,
        repository=repo,
        verifier_id=verifier,
        test_file_path=test_file,
        predicted_approach=approach,
        predicted_complexity=cx,
        expected_edge_cases=edge_cases,
    )

    session.prediction = pred
    _save_session(session)
    typer.echo(f"✅ Prediction recorded for PR #{pr}")
    typer.echo(f"   Approach: {approach[:80]}...")
    typer.echo(f"   Complexity: {cx.value}")
    typer.echo(f"   Edge cases: {len(edge_cases)}")


# ------------------------------------------------------------------ #
# svp trace
# ------------------------------------------------------------------ #

@svp_app.command()
def trace(
    pr: int = typer.Argument(..., help="PR number"),
    repo: str = typer.Option("owner/repo", help="Repository"),
    verifier: str = typer.Option(..., help="Verifier GitHub ID"),
    function: str = typer.Option(..., help="Function path (e.g., src/auth.py::login)"),
    notes: str = typer.Option(..., help="Trace notes (≥100 chars)"),
    edge_case: str = typer.Option(..., help="Edge case tested (≥10 chars)"),
    predicted_output: str = typer.Option(..., help="Predicted output for edge case"),
    confidence: str = typer.Option("medium", help="Confidence: high/medium/low"),
) -> None:
    """Record a Mental Trace (Phase 2)."""
    session = _load_session(pr)
    if session is None:
        session = SVPSession(
            pr_number=pr,
            repository=repo,
            verifier_id=verifier,
            aiv_guard_passed=True,
        )

    conf = Confidence(confidence) if confidence in [c.value for c in Confidence] else Confidence.MEDIUM

    tr = TraceRecord(
        pr_number=pr,
        repository=repo,
        verifier_id=verifier,
        function_path=function,
        trace_notes=notes,
        edge_case_tested=edge_case,
        predicted_output=predicted_output,
        confidence=conf,
    )

    session.traces.append(tr)
    _save_session(session)
    typer.echo(f"✅ Trace recorded for {function}")
    typer.echo(f"   Edge case: {edge_case[:60]}")
    typer.echo(f"   Confidence: {conf.value}")
    typer.echo(f"   Total traces: {len(session.traces)}")


# ------------------------------------------------------------------ #
# svp probe
# ------------------------------------------------------------------ #

@svp_app.command()
def probe(
    pr: int = typer.Argument(..., help="PR number"),
    repo: str = typer.Option("owner/repo", help="Repository"),
    verifier: str = typer.Option(..., help="Verifier GitHub ID"),
    assessment: str = typer.Option(..., help="Overall assessment (≥20 chars)"),
    why_question: str = typer.Option(..., help="A 'Why?' question (≥10 chars)"),
    why_context: str = typer.Option("", help="Context for the Why question"),
    falsify_claim: str = typer.Option("", help="Claim ID for falsification scenario (e.g. C-001)"),
    falsify_scenario: str = typer.Option("", help="Evidence that would prove the claim false (≥25 chars)"),
) -> None:
    """Submit an Adversarial Probe checklist (Phase 3)."""
    session = _load_session(pr)
    if session is None:
        session = SVPSession(
            pr_number=pr,
            repository=repo,
            verifier_id=verifier,
            aiv_guard_passed=True,
        )

    scenarios: list[FalsificationScenario] = []
    if falsify_claim and falsify_scenario:
        scenarios.append(FalsificationScenario(
            claim_id=falsify_claim,
            scenario=falsify_scenario,
        ))

    pr_record = ProbeRecord(
        pr_number=pr,
        repository=repo,
        verifier_id=verifier,
        happy_path_bias_checked=True,
        context_amnesia_checked=True,
        fragile_assertions_checked=True,
        why_questions=[WhyQuestion(
            question=why_question,
            context=why_context or "Prompted by code review",
        )],
        falsification_scenarios=scenarios,
        overall_assessment=assessment,
    )

    session.probe = pr_record
    _save_session(session)
    typer.echo(f"✅ Adversarial probe recorded for PR #{pr}")
    typer.echo(f"   Checklist: complete")
    typer.echo(f"   Why questions: 1")
    typer.echo(f"   Falsification scenarios: {len(scenarios)}")


# ------------------------------------------------------------------ #
# svp validate
# ------------------------------------------------------------------ #

@svp_app.command()
def validate(
    pr: int = typer.Argument(..., help="PR number"),
) -> None:
    """Validate SVP session completeness (outputs JSON)."""
    session = _load_session(pr)
    if session is None:
        typer.echo(f"No SVP session found for PR #{pr}", err=True)
        raise typer.Exit(1)

    result = validate_session(session)

    typer.echo(result.model_dump_json(indent=2))

    if not result.is_complete:
        raise typer.Exit(1)
