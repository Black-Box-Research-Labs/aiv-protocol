"""
aiv/svp/cli/main.py

SVP CLI commands integrated into the main ``aiv`` CLI via Typer.
Provides: svp status, svp predict, svp trace, svp probe, svp ownership, svp validate.
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
        mark = "[PASS]" if done else "[FAIL]"
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
    typer.echo(f"[OK] Prediction recorded for PR #{pr}")
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
    typer.echo(f"[OK] Trace recorded for {function}")
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
    falsify_claim: list[str] = typer.Option([], help="Claim ID for falsification scenario (repeatable)"),
    falsify_scenario: list[str] = typer.Option([], help="Falsification evidence, paired with --falsify-claim (repeatable)"),
) -> None:
    """Submit an Adversarial Probe checklist (Phase 3).

    Supports multiple falsification scenarios via repeated options:
        --falsify-claim C-001 --falsify-scenario "If X then false"
        --falsify-claim C-002 --falsify-scenario "If Y then false"

    If a probe already exists, new scenarios are merged into it.
    """
    session = _load_session(pr)
    if session is None:
        session = SVPSession(
            pr_number=pr,
            repository=repo,
            verifier_id=verifier,
            aiv_guard_passed=True,
        )

    # Build new scenarios from paired --falsify-claim / --falsify-scenario
    new_scenarios: list[FalsificationScenario] = []
    for claim_id, scenario_text in zip(falsify_claim, falsify_scenario):
        if claim_id and scenario_text:
            new_scenarios.append(FalsificationScenario(
                claim_id=claim_id,
                scenario=scenario_text,
            ))

    # Merge into existing probe if one exists (resume support)
    if session.probe is not None:
        existing_scenarios = list(session.probe.falsification_scenarios)
        existing_claim_ids = {s.claim_id for s in existing_scenarios}
        for s in new_scenarios:
            if s.claim_id not in existing_claim_ids:
                existing_scenarios.append(s)
                existing_claim_ids.add(s.claim_id)
        pr_record = session.probe.model_copy(update={
            "falsification_scenarios": existing_scenarios,
            "overall_assessment": assessment or session.probe.overall_assessment,
        })
    else:
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
            falsification_scenarios=new_scenarios,
            overall_assessment=assessment,
        )

    session.probe = pr_record
    _save_session(session)
    total = len(pr_record.falsification_scenarios)
    typer.echo(f"[OK] Adversarial probe recorded for PR #{pr}")
    typer.echo(f"   Checklist: complete")
    typer.echo(f"   Why questions: {len(pr_record.why_questions)}")
    typer.echo(f"   Falsification scenarios: {total}")


# ------------------------------------------------------------------ #
# svp ownership
# ------------------------------------------------------------------ #

@svp_app.command()
def ownership(
    pr: int = typer.Argument(..., help="PR number"),
    repo: str = typer.Option("owner/repo", help="Repository"),
    verifier: str = typer.Option(..., help="Verifier GitHub ID"),
    commit_sha: str = typer.Option(..., help="Ownership commit SHA"),
    message: str = typer.Option(..., help="Commit message (should start with 'ownership:')"),
    rename_file: str = typer.Option("", help="File path of rename"),
    rename_from: str = typer.Option("", help="Original name"),
    rename_to: str = typer.Option("", help="New name"),
    rename_type: str = typer.Option("function", help="Change type: variable/function/class/parameter"),
    rename_reason: str = typer.Option("", help="Justification for rename (≥10 chars)"),
) -> None:
    """Record an Ownership Lock commit (Phase 4).

    The verifier must push a commit with semantic renames or docstrings
    to prove cognitive ownership of the code.
    """
    session = _load_session(pr)
    if session is None:
        session = SVPSession(
            pr_number=pr,
            repository=repo,
            verifier_id=verifier,
            aiv_guard_passed=True,
        )

    renames: list[RenameChange] = []
    if rename_file and rename_from and rename_to and rename_reason:
        renames.append(RenameChange(
            file_path=rename_file,
            original_name=rename_from,
            new_name=rename_to,
            change_type=rename_type,
            justification=rename_reason,
        ))

    oc = OwnershipCommit(
        pr_number=pr,
        repository=repo,
        commit_sha=commit_sha,
        author_github_id=verifier,
        commit_message=message,
        committed_at=datetime.now(timezone.utc),
        renames=renames,
    )

    session.ownership_commit = oc
    _save_session(session)
    typer.echo(f"[OK] Ownership commit recorded for PR #{pr}")
    typer.echo(f"   SHA: {commit_sha[:12]}")
    typer.echo(f"   Renames: {len(renames)}")
    typer.echo(f"   Message: {message[:60]}")


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
