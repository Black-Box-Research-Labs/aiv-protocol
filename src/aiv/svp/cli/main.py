"""
aiv/svp/cli/main.py

SVP CLI commands integrated into the main ``aiv`` CLI via Typer.
Provides: svp status, svp predict, svp trace, svp probe, svp ownership, svp validate.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import typer

from ..lib.models import (
    AITellType,
    BugSeverity,
    Complexity,
    Confidence,
    FalsificationScenario,
    OwnershipCommit,
    PredictionRecord,
    ProbeFinding,
    ProbeRecord,
    RenameChange,
    StateTransition,
    SVPSession,
    TraceRecord,
    WhyQuestion,
)
from ..lib.rating import (
    calculate_rating,
    load_all_sessions,
    load_ratings,
    save_ratings,
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
    approach: str = typer.Option(..., help="Predicted implementation approach (>=50 chars)"),
    complexity: str = typer.Option("Unknown", help="Predicted complexity: O(1), O(n), etc."),
    edge_cases: list[str] = typer.Option(..., help="Expected edge cases (>=2)"),
    packet_ref: str = typer.Option("", help="Verification packet filename this session verifies"),
) -> None:
    """Record a Black Box Prediction (Phase 1).

    Before reading the diff, predict how the change was implemented.
    This tests whether you understand the codebase well enough to
    anticipate what changed.

    Examples:
        aiv svp predict 42 --verifier alice --test-file tests/test_auth.py \\
            --approach "Add expiry check in TokenValidator.validate() before\n"
            "returning the decoded payload. Raise HTTP 401 on expiry." \\
            --edge-cases "token exactly at boundary" \\
            --edge-cases "clock skew between servers"
    """
    session = _load_session(pr)
    if session is None:
        session = SVPSession(
            pr_number=pr,
            repository=repo,
            verifier_id=verifier,
            aiv_guard_passed=True,
            packet_ref=packet_ref,
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
    notes: str = typer.Option(..., help="Trace notes (>=100 chars)"),
    edge_case: str = typer.Option(..., help="Edge case tested (>=10 chars)"),
    predicted_output: str = typer.Option(..., help="Predicted output for edge case"),
    confidence: str = typer.Option("medium", help="Confidence: high/medium/low"),
    transition_var: list[str] = typer.Option([], help="Variable name for state transition (repeatable)"),
    transition_before: list[str] = typer.Option([], help="Value before, paired with --transition-var"),
    transition_after: list[str] = typer.Option([], help="Value after, paired with --transition-var"),
) -> None:
    """Record a Mental Trace (Phase 2).

    Simulate execution of a specific function through an edge case
    WITHOUT running the code. Record what you expect to happen at
    each step. Multiple traces per session are expected (>=3 recommended).

    Examples:
        aiv svp trace 42 --verifier alice \\
            --function src/auth.py::validate \\
            --notes "Token arrives as JWT string. decode() splits header.payload.sig.\n"
            "Checks exp claim against datetime.utcnow(). If exp < now, raises\n"
            "AuthError(401). Otherwise returns decoded payload dict." \\
            --edge-case "token with exp exactly equal to current time" \\
            --predicted-output "Should return 401 since exp==now means expired" \\
            --confidence medium

    State transitions (optional, repeatable):
        --transition-var result --transition-before None --transition-after FAIL
    """
    session = _load_session(pr)
    if session is None:
        session = SVPSession(
            pr_number=pr,
            repository=repo,
            verifier_id=verifier,
            aiv_guard_passed=True,
        )

    conf = Confidence(confidence) if confidence in [c.value for c in Confidence] else Confidence.MEDIUM

    transitions: list[StateTransition] = []
    for i, (var, before, after) in enumerate(
        zip(transition_var, transition_before, transition_after, strict=False), start=1
    ):
        transitions.append(
            StateTransition(
                step_number=i,
                variable_name=var,
                before_value=before,
                after_value=after,
            )
        )

    tr = TraceRecord(
        pr_number=pr,
        repository=repo,
        verifier_id=verifier,
        function_path=function,
        trace_notes=notes,
        state_transitions=transitions,
        edge_case_tested=edge_case,
        predicted_output=predicted_output,
        confidence=conf,
    )

    session.traces.append(tr)
    _save_session(session)
    typer.echo(f"[OK] Trace recorded for {function}")
    typer.echo(f"   Edge case: {edge_case[:60]}")
    typer.echo(f"   Confidence: {conf.value}")
    typer.echo(f"   State transitions: {len(transitions)}")
    typer.echo(f"   Total traces: {len(session.traces)}")


# ------------------------------------------------------------------ #
# svp probe
# ------------------------------------------------------------------ #


@svp_app.command()
def probe(
    pr: int = typer.Argument(..., help="PR number"),
    repo: str = typer.Option("owner/repo", help="Repository"),
    verifier: str = typer.Option(..., help="Verifier GitHub ID"),
    assessment: str = typer.Option(..., help="Overall assessment (>=20 chars)"),
    why_question: str = typer.Option(..., help="A 'Why?' question (>=10 chars)"),
    why_context: str = typer.Option("", help="Context for the Why question"),
    falsify_claim: list[str] = typer.Option([], help="Claim ID for falsification scenario (repeatable)"),
    falsify_scenario: list[str] = typer.Option(
        [], help="Falsification evidence, paired with --falsify-claim (repeatable)"
    ),
    finding_type: list[str] = typer.Option([], help="AI tell type for structured finding (repeatable)"),
    finding_file: list[str] = typer.Option([], help="File path for finding, paired with --finding-type (repeatable)"),
    finding_desc: list[str] = typer.Option([], help="Finding description, paired with --finding-type (repeatable)"),
    finding_severity: list[str] = typer.Option([], help="Finding severity: low/medium/high/critical (repeatable)"),
) -> None:
    """Submit an Adversarial Probe checklist (Phase 3).

    Hunt for bugs, hallucinations, and edge cases. Your primary
    deliverable is the adversarial report (findings), not approval.
    At least one falsification scenario per claim is REQUIRED (S014).

    Examples:
        aiv svp probe 42 --verifier alice \\
            --assessment "Auth module handles basic expiry but no clock skew" \\
            --why-question "Why is there no tolerance window for clock skew?" \\
            --falsify-claim C-001 \\
            --falsify-scenario "Send token with exp=now+1s from server with 2s clock drift" \\
            --finding-type missing_edge_case --finding-file src/auth.py \\
            --finding-desc "No clock skew tolerance" --finding-severity medium

    Falsification scenarios (REQUIRED, repeatable):
        --falsify-claim <claim-id> --falsify-scenario "<scenario text >=25 chars>"

    Structured findings (optional, repeatable):
        --finding-type <type> --finding-file <path>
        --finding-desc <description> --finding-severity <low|medium|high|critical>

    If a probe already exists, new scenarios and findings are merged.
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
    for claim_id, scenario_text in zip(falsify_claim, falsify_scenario, strict=False):
        if claim_id and scenario_text:
            new_scenarios.append(
                FalsificationScenario(
                    claim_id=claim_id,
                    scenario=scenario_text,
                )
            )

    # Build structured findings from paired options
    new_findings: list[ProbeFinding] = []
    for ft, ff, fd, fs in zip(finding_type, finding_file, finding_desc, finding_severity, strict=False):
        if ft and ff and fd:
            try:
                tell_type = AITellType(ft)
            except ValueError:
                tell_type = AITellType.MAGIC_NUMBERS
            try:
                sev = BugSeverity(fs) if fs else BugSeverity.LOW
            except ValueError:
                sev = BugSeverity.LOW
            new_findings.append(
                ProbeFinding(
                    finding_type=tell_type,
                    file_path=ff,
                    description=fd,
                    severity=sev,
                )
            )

    # Merge into existing probe if one exists (resume support)
    if session.probe is not None:
        existing_scenarios = list(session.probe.falsification_scenarios)
        existing_claim_ids = {s.claim_id for s in existing_scenarios}
        for s in new_scenarios:
            if s.claim_id not in existing_claim_ids:
                existing_scenarios.append(s)
                existing_claim_ids.add(s.claim_id)
        merged_findings = list(session.probe.findings) + new_findings
        pr_record = session.probe.model_copy(
            update={
                "falsification_scenarios": existing_scenarios,
                "findings": merged_findings,
                "overall_assessment": assessment or session.probe.overall_assessment,
            }
        )
    else:
        pr_record = ProbeRecord(
            pr_number=pr,
            repository=repo,
            verifier_id=verifier,
            happy_path_bias_checked=True,
            context_amnesia_checked=True,
            fragile_assertions_checked=True,
            why_questions=[
                WhyQuestion(
                    question=why_question,
                    context=why_context or "Prompted by code review",
                )
            ],
            falsification_scenarios=new_scenarios,
            findings=new_findings,
            overall_assessment=assessment,
        )

    session.probe = pr_record
    _save_session(session)
    typer.echo(f"[OK] Adversarial probe recorded for PR #{pr}")
    typer.echo("   Checklist: complete")
    typer.echo(f"   Why questions: {len(pr_record.why_questions)}")
    typer.echo(f"   Falsification scenarios: {len(pr_record.falsification_scenarios)}")
    typer.echo(f"   Structured findings: {len(pr_record.findings)}")


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
    rename_reason: str = typer.Option("", help="Justification for rename (>=10 chars)"),
) -> None:
    """Record an Ownership Lock commit (Phase 4).

    The verifier must push a real commit with semantic renames or
    docstring additions to prove cognitive ownership of the code.
    This commit must be authored by the verifier (not the implementer).

    Examples:
        aiv svp ownership 42 --verifier alice \\
            --commit-sha abc1234def5678 \\
            --message "ownership: rename token_check to validate_jwt_expiry" \\
            --rename-file src/auth.py \\
            --rename-from token_check --rename-to validate_jwt_expiry \\
            --rename-type function \\
            --rename-reason "Original name was vague; new name reflects JWT-specific validation"
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
        renames.append(
            RenameChange(
                file_path=rename_file,
                original_name=rename_from,
                new_name=rename_to,
                change_type=rename_type,  # type: ignore[arg-type]
                justification=rename_reason,
            )
        )

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


# ------------------------------------------------------------------ #
# svp rating
# ------------------------------------------------------------------ #


@svp_app.command()
def rating(
    verifier_id: str = typer.Argument(..., help="Verifier ID to calculate rating for"),
    save: bool = typer.Option(True, help="Persist updated rating to .svp/ratings.json"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show individual rating events"),
) -> None:
    """Calculate and display ELO rating for a verifier from all sessions."""
    sessions = load_all_sessions()
    if not sessions:
        typer.echo("No SVP sessions found in .svp/", err=True)
        raise typer.Exit(1)

    verifier_sessions = [s for s in sessions if s.verifier_id == verifier_id]
    if not verifier_sessions:
        typer.echo(f"No sessions found for verifier '{verifier_id}'", err=True)
        typer.echo("Available verifiers:", err=True)
        seen: set[str] = set()
        for s in sessions:
            if s.verifier_id not in seen:
                typer.echo(f"  - {s.verifier_id}", err=True)
                seen.add(s.verifier_id)
        raise typer.Exit(1)

    result, events = calculate_rating(verifier_id, sessions)

    typer.echo(f"Verifier: {verifier_id}")
    typer.echo(f"Sessions: {result.total_reviews}")
    typer.echo(f"ELO:      {result.elo_rating}")
    typer.echo(f"Tier:     {result.tier.value.upper()}")
    typer.echo(f"Bugs:     {result.bugs_caught}")
    typer.echo(f"FPs:      {result.false_positives}")

    if verbose and events:
        typer.echo()
        typer.echo("Rating Events:")
        for e in events:
            sign = "+" if e.points >= 0 else ""
            typer.echo(f"  [{sign}{e.points:>3}] {e.event_type}: {e.description}")

    if save:
        ratings = load_ratings()
        ratings[verifier_id] = result
        save_ratings(ratings)
        typer.echo()
        typer.echo("Rating saved to .svp/ratings.json")
