"""
tests/unit/test_svp.py

Unit tests for the SVP Protocol Suite (§7.5 P4).
"""

from __future__ import annotations

import pytest
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from aiv.svp.lib.models import (
    Complexity,
    Confidence,
    SessionType,
    SVPPhase,
    SVPStatus,
    BugSeverity,
    VerifierTier,
    AITellType,
    ValidationSeverity,
    PredictionRecord,
    PredictionComparison,
    TraceRecord,
    StateTransition,
    ProbeRecord,
    ProbeFinding,
    WhyQuestion,
    FalsificationScenario,
    OwnershipCommit,
    RenameChange,
    DocstringChange,
    SVPSession,
    BugReport,
    RatingEvent,
    VerifierRating,
    SVPValidationError,
    SVPValidationResult,
    RATING_POINTS,
)
from aiv.svp.lib.validators.session import validate_session


# ------------------------------------------------------------------ #
# Fixtures
# ------------------------------------------------------------------ #

def _now() -> datetime:
    return datetime.now(timezone.utc)


def _make_prediction(**kwargs) -> PredictionRecord:
    defaults = dict(
        pr_number=1,
        repository="owner/repo",
        verifier_id="verifier",
        test_file_path="tests/test_auth.py",
        predicted_approach="x" * 50,
        predicted_complexity=Complexity.LINEAR,
        expected_edge_cases=["empty input", "null token"],
    )
    defaults.update(kwargs)
    return PredictionRecord(**defaults)


def _make_trace(**kwargs) -> TraceRecord:
    defaults = dict(
        pr_number=1,
        repository="owner/repo",
        verifier_id="verifier",
        function_path="src/auth.py::login",
        trace_notes="x" * 100,
        edge_case_tested="empty password input handling",
        predicted_output="raise ValueError",
        confidence=Confidence.MEDIUM,
    )
    defaults.update(kwargs)
    return TraceRecord(**defaults)


def _make_probe(**kwargs) -> ProbeRecord:
    defaults = dict(
        pr_number=1,
        repository="owner/repo",
        verifier_id="verifier",
        happy_path_bias_checked=True,
        context_amnesia_checked=True,
        fragile_assertions_checked=True,
        why_questions=[WhyQuestion(
            question="Why was this approach chosen over X?",
            context="reviewing auth flow",
        )],
        falsification_scenarios=[FalsificationScenario(
            claim_id="C-001",
            scenario="If test_auth_login accepts an expired token, claim C-001 is falsified.",
        )],
        overall_assessment="No AI tells detected in this PR.",
    )
    defaults.update(kwargs)
    return ProbeRecord(**defaults)


def _make_ownership(**kwargs) -> OwnershipCommit:
    defaults = dict(
        pr_number=1,
        repository="owner/repo",
        commit_sha="a" * 40,
        author_github_id="verifier",
        commit_message="ownership: clarify auth flow naming",
        committed_at=_now(),
        renames=[RenameChange(
            file_path="src/auth.py",
            original_name="do_auth",
            new_name="authenticate_user",
            change_type="function",
            justification="Clarifies intent of authentication function",
        )],
    )
    defaults.update(kwargs)
    return OwnershipCommit(**defaults)


def _make_complete_session(**kwargs) -> SVPSession:
    defaults = dict(
        pr_number=1,
        repository="owner/repo",
        verifier_id="verifier",
        aiv_guard_passed=True,
        prediction=_make_prediction(),
        traces=[_make_trace()],
        probe=_make_probe(),
        ownership_commit=_make_ownership(),
    )
    defaults.update(kwargs)
    return SVPSession(**defaults)


# ------------------------------------------------------------------ #
# Enum tests
# ------------------------------------------------------------------ #

class TestEnums:
    def test_complexity_values(self):
        assert Complexity.CONSTANT.value == "O(1)"
        assert Complexity.EXPONENTIAL.value == "O(2^n)"

    def test_verifier_tier_from_elo(self):
        assert VerifierTier.from_elo(0) == VerifierTier.NOVICE
        assert VerifierTier.from_elo(499) == VerifierTier.NOVICE
        assert VerifierTier.from_elo(500) == VerifierTier.COMPETENT
        assert VerifierTier.from_elo(1000) == VerifierTier.PROFICIENT
        assert VerifierTier.from_elo(1500) == VerifierTier.EXPERT
        assert VerifierTier.from_elo(2000) == VerifierTier.MASTER

    def test_svp_phases(self):
        assert SVPPhase.SANITY.value == "phase_0_sanity"
        assert SVPPhase.OWNERSHIP.value == "phase_4_ownership"

    def test_ai_tell_types(self):
        assert AITellType.HAPPY_PATH_BIAS.value == "happy_path_bias"
        assert AITellType.CONTEXT_AMNESIA.value == "context_amnesia"


# ------------------------------------------------------------------ #
# Prediction tests
# ------------------------------------------------------------------ #

class TestPrediction:
    def test_valid_prediction(self):
        p = _make_prediction()
        assert p.is_valid_timing is True
        assert len(p.expected_edge_cases) >= 2

    def test_invalid_timing(self):
        now = _now()
        p = _make_prediction(
            created_at=now,
            diff_first_viewed_at=now - timedelta(hours=1),
        )
        assert p.is_valid_timing is False

    def test_prediction_comparison_exact(self):
        pred = _make_prediction()
        comp = PredictionComparison.calculate(
            pred,
            actual_complexity=Complexity.LINEAR,
            actual_edge_cases=["empty input", "null token"],
            approach_assessment="exact",
        )
        assert comp.approach_match == "exact"
        assert comp.complexity_match is True
        assert comp.accuracy_score >= 75

    def test_prediction_comparison_different(self):
        pred = _make_prediction()
        comp = PredictionComparison.calculate(
            pred,
            actual_complexity=Complexity.QUADRATIC,
            actual_edge_cases=["timeout"],
            approach_assessment="different",
        )
        assert comp.approach_match == "different"
        assert comp.complexity_match is False
        assert comp.accuracy_score < 50


# ------------------------------------------------------------------ #
# Trace tests
# ------------------------------------------------------------------ #

class TestTrace:
    def test_valid_trace(self):
        t = _make_trace()
        assert len(t.trace_notes) >= 100
        assert len(t.edge_case_tested) >= 10

    def test_state_transitions(self):
        st = StateTransition(
            step_number=1,
            variable_name="token",
            before_value="None",
            after_value="'abc123'",
            line_number=42,
        )
        assert st.step_number == 1


# ------------------------------------------------------------------ #
# Probe tests
# ------------------------------------------------------------------ #

class TestProbe:
    def test_complete_checklist(self):
        p = _make_probe()
        assert p.checklist_complete is True

    def test_incomplete_checklist(self):
        p = _make_probe(happy_path_bias_checked=False)
        assert p.checklist_complete is False

    def test_bugs_found(self):
        finding = ProbeFinding(
            finding_type=AITellType.MAGIC_NUMBERS,
            file_path="src/config.py",
            description="Hardcoded timeout value of 30",
            severity=BugSeverity.LOW,
            is_confirmed_bug=True,
        )
        p = _make_probe(findings=[finding])
        assert len(p.bugs_found) == 1

    def test_falsification_scenario_model(self):
        fs = FalsificationScenario(
            claim_id="C-001",
            scenario="If test_login accepts an expired JWT, the claim is falsified.",
        )
        assert fs.claim_id == "C-001"
        assert fs.checked is False
        assert fs.result == "confirmed"

    def test_falsification_scenario_too_short(self):
        with pytest.raises(Exception):
            FalsificationScenario(
                claim_id="C-001",
                scenario="too short",  # < 25 chars
            )

    def test_probe_with_falsification_scenarios(self):
        p = _make_probe()
        assert len(p.falsification_scenarios) == 1
        assert p.falsification_scenarios[0].claim_id == "C-001"


# ------------------------------------------------------------------ #
# Ownership tests
# ------------------------------------------------------------------ #

class TestOwnership:
    def test_follows_pattern(self):
        oc = _make_ownership()
        assert oc.follows_message_pattern is True

    def test_bad_message_pattern(self):
        oc = _make_ownership(commit_message="fix: typo")
        assert oc.follows_message_pattern is False

    def test_has_substantive_changes(self):
        oc = _make_ownership()
        assert oc.has_substantive_changes is True

    def test_no_changes(self):
        oc = _make_ownership(renames=[], docstrings=[])
        assert oc.has_substantive_changes is False

    def test_docstring_quality(self):
        ds = DocstringChange(
            file_path="src/auth.py",
            function_name="login",
            docstring_content="Authenticates user with token validation flow.",
            includes_why=True,
            includes_invariant=True,
            includes_risk=True,
        )
        oc = _make_ownership(renames=[], docstrings=[ds])
        assert oc.docstring_quality_score == 100

    def test_docstring_partial_quality(self):
        ds = DocstringChange(
            file_path="src/auth.py",
            function_name="login",
            docstring_content="Authenticates user with token validation flow.",
            includes_why=True,
            includes_invariant=False,
            includes_risk=False,
        )
        oc = _make_ownership(renames=[], docstrings=[ds])
        assert oc.docstring_quality_score == 60  # 40 base + 20 why


# ------------------------------------------------------------------ #
# Session tests
# ------------------------------------------------------------------ #

class TestSession:
    def test_complete_session(self):
        s = _make_complete_session()
        assert s.status == SVPStatus.COMPLETE
        assert s.completion_percentage == 100

    def test_blocked_session(self):
        s = _make_complete_session(aiv_guard_passed=False)
        assert s.status == SVPStatus.BLOCKED

    def test_in_progress(self):
        s = SVPSession(
            pr_number=1,
            repository="owner/repo",
            verifier_id="verifier",
            aiv_guard_passed=True,
            prediction=_make_prediction(),
        )
        assert s.status == SVPStatus.IN_PROGRESS
        assert SVPPhase.TRACE in s.missing_phases

    def test_not_started(self):
        s = SVPSession(
            pr_number=1,
            repository="owner/repo",
            verifier_id="verifier",
            aiv_guard_passed=True,
        )
        assert s.status == SVPStatus.NOT_STARTED

    def test_missing_phases(self):
        s = SVPSession(
            pr_number=1,
            repository="owner/repo",
            verifier_id="verifier",
            aiv_guard_passed=True,
            prediction=_make_prediction(),
            traces=[_make_trace()],
        )
        missing = s.missing_phases
        assert SVPPhase.PROBE in missing
        assert SVPPhase.OWNERSHIP in missing
        assert SVPPhase.PREDICTION not in missing
        assert SVPPhase.TRACE not in missing


# ------------------------------------------------------------------ #
# Rating tests
# ------------------------------------------------------------------ #

class TestRating:
    def test_initial_rating(self):
        r = VerifierRating(verifier_id="user1")
        assert r.elo_rating == 500
        assert r.tier == VerifierTier.NOVICE

    def test_apply_event_positive(self):
        r = VerifierRating(verifier_id="user1")
        event = RatingEvent(
            verifier_id="user1",
            event_type="bug_caught_critical",
            points=50,
            description="Found critical auth bypass",
        )
        r.apply_event(event)
        assert r.elo_rating == 550
        assert r.tier == VerifierTier.COMPETENT

    def test_apply_event_negative(self):
        r = VerifierRating(verifier_id="user1", elo_rating=100)
        event = RatingEvent(
            verifier_id="user1",
            event_type="bug_missed",
            points=-25,
            description="Missed null check bug",
        )
        r.apply_event(event)
        assert r.elo_rating == 75

    def test_rating_floor_zero(self):
        r = VerifierRating(verifier_id="user1", elo_rating=10)
        event = RatingEvent(
            verifier_id="user1",
            event_type="bug_missed",
            points=-25,
            description="Large penalty",
        )
        r.apply_event(event)
        assert r.elo_rating == 0

    def test_tier_transitions(self):
        r = VerifierRating(verifier_id="user1", elo_rating=1999)
        r.update_tier()
        assert r.tier == VerifierTier.EXPERT
        r.elo_rating = 2000
        r.update_tier()
        assert r.tier == VerifierTier.MASTER

    def test_rating_points_map(self):
        assert RATING_POINTS["bug_caught_critical"] == 50
        assert RATING_POINTS["false_positive"] == -10


# ------------------------------------------------------------------ #
# Session validator tests
# ------------------------------------------------------------------ #

class TestSessionValidator:
    def test_complete_session_passes(self):
        s = _make_complete_session()
        result = validate_session(s)
        assert result.is_complete is True
        assert len(result.errors) == 0

    def test_s001_aiv_guard_required(self):
        s = _make_complete_session(aiv_guard_passed=False)
        result = validate_session(s)
        assert not result.is_complete
        assert any(e.rule_id == "S001" for e in result.errors)

    def test_s002_prediction_required(self):
        s = _make_complete_session(prediction=None)
        result = validate_session(s)
        assert any(e.rule_id == "S002" for e in result.errors)

    def test_s003_prediction_timing(self):
        now = _now()
        pred = _make_prediction(
            created_at=now,
            diff_first_viewed_at=now - timedelta(hours=1),
        )
        s = _make_complete_session(prediction=pred)
        result = validate_session(s)
        assert any(e.rule_id == "S003" for e in result.errors)

    def test_s005_trace_required(self):
        s = _make_complete_session(traces=[])
        result = validate_session(s)
        assert any(e.rule_id == "S005" for e in result.errors)

    def test_s008_probe_required(self):
        s = _make_complete_session(probe=None)
        result = validate_session(s)
        assert any(e.rule_id == "S008" for e in result.errors)

    def test_s008_incomplete_checklist(self):
        probe = _make_probe(happy_path_bias_checked=False)
        s = _make_complete_session(probe=probe)
        result = validate_session(s)
        assert any(e.rule_id == "S008" for e in result.errors)

    def test_s014_missing_falsification_scenarios(self):
        probe = _make_probe(falsification_scenarios=[])
        s = _make_complete_session(probe=probe)
        result = validate_session(s)
        assert any(e.rule_id == "S014" for e in result.errors), (
            "Empty falsification_scenarios should trigger S014"
        )

    def test_s014_valid_falsification_scenarios(self):
        probe = _make_probe(falsification_scenarios=[
            FalsificationScenario(
                claim_id="C-001",
                scenario="If test_auth shows expired token accepted, claim is falsified.",
            ),
        ])
        s = _make_complete_session(probe=probe)
        result = validate_session(s)
        assert not any(e.rule_id == "S014" for e in result.errors), (
            "Valid falsification_scenarios should not trigger S014"
        )

    def test_s010_ownership_required(self):
        s = _make_complete_session(ownership_commit=None)
        result = validate_session(s)
        assert any(e.rule_id == "S010" for e in result.errors)

    def test_s011_wrong_verifier(self):
        oc = _make_ownership(author_github_id="someone-else")
        s = _make_complete_session(ownership_commit=oc)
        result = validate_session(s)
        assert any(e.rule_id == "S011" for e in result.errors)

    def test_s012_no_substantive_changes(self):
        oc = _make_ownership(renames=[], docstrings=[])
        s = _make_complete_session(ownership_commit=oc)
        result = validate_session(s)
        assert any(e.rule_id == "S012" for e in result.errors)

    def test_s013_message_pattern_warn(self):
        oc = _make_ownership(commit_message="fix: typo")
        s = _make_complete_session(ownership_commit=oc)
        result = validate_session(s)
        assert any(w.rule_id == "S013" for w in result.warnings)
        # S013 is WARN, not BLOCK — session should still pass
        assert result.phase_4_complete is True

    def test_completion_percentage(self):
        s = SVPSession(
            pr_number=1,
            repository="owner/repo",
            verifier_id="verifier",
            aiv_guard_passed=True,
            prediction=_make_prediction(),
            traces=[_make_trace()],
        )
        result = validate_session(s)
        assert result.completion_percentage == 60  # 3/5 phases

    def test_validation_result_serialization(self):
        s = _make_complete_session()
        result = validate_session(s)
        j = result.model_dump_json()
        assert "pr_number" in j
        assert "phase_0_complete" in j


# ------------------------------------------------------------------ #
# S015: AI Execution Trace
# ------------------------------------------------------------------ #

class TestS015ExecutionTrace:
    """S015: AI sessions must include verified_output on traces."""

    def test_human_session_passes_without_verified_output(self):
        s = _make_complete_session(session_type=SessionType.HUMAN_VERIFICATION)
        result = validate_session(s)
        assert not any(e.rule_id == "S015" for e in result.errors)
        assert result.phase_2_complete is True

    def test_ai_session_blocks_without_verified_output(self):
        s = _make_complete_session(
            session_type=SessionType.AI_ADVERSARIAL_TRIAGE,
        )
        result = validate_session(s)
        s015 = [e for e in result.errors if e.rule_id == "S015"]
        assert len(s015) == 1
        assert "verified_output" in s015[0].message
        assert result.phase_2_complete is False

    def test_ai_session_passes_with_verified_output(self):
        trace = _make_trace(verified_output="exit code: 0\nresult: ValueError raised")
        s = _make_complete_session(
            session_type=SessionType.AI_ADVERSARIAL_TRIAGE,
            traces=[trace],
        )
        result = validate_session(s)
        assert not any(e.rule_id == "S015" for e in result.errors)
        assert result.phase_2_complete is True

    def test_ai_session_empty_string_verified_output_blocks(self):
        trace = _make_trace(verified_output="")
        s = _make_complete_session(
            session_type=SessionType.AI_ADVERSARIAL_TRIAGE,
            traces=[trace],
        )
        result = validate_session(s)
        assert any(e.rule_id == "S015" for e in result.errors)


# ------------------------------------------------------------------ #
# S016: Falsification-as-Code
# ------------------------------------------------------------------ #

class TestS016FalsificationAsCode:
    """S016: AI sessions must have test_code on falsification scenarios."""

    def test_human_session_passes_without_test_code(self):
        s = _make_complete_session(session_type=SessionType.HUMAN_VERIFICATION)
        result = validate_session(s)
        assert not any(e.rule_id == "S016" for e in result.errors)

    def test_ai_session_blocks_without_test_code(self):
        s = _make_complete_session(
            session_type=SessionType.AI_ADVERSARIAL_TRIAGE,
            traces=[_make_trace(verified_output="confirmed")],
        )
        result = validate_session(s)
        s016 = [e for e in result.errors if e.rule_id == "S016"]
        assert len(s016) == 1
        assert "test_code" in s016[0].message
        assert result.phase_3_complete is False

    def test_ai_session_passes_with_test_code(self):
        probe = _make_probe(falsification_scenarios=[
            FalsificationScenario(
                claim_id="C-001",
                scenario="If test_auth_login accepts an expired token, claim C-001 is falsified.",
                test_code="def test_expired_token():\n    assert login(expired) == False",
            ),
        ])
        s = _make_complete_session(
            session_type=SessionType.AI_ADVERSARIAL_TRIAGE,
            traces=[_make_trace(verified_output="confirmed")],
            probe=probe,
        )
        result = validate_session(s)
        assert not any(e.rule_id == "S016" for e in result.errors)
        assert result.phase_3_complete is True


# ------------------------------------------------------------------ #
# SessionType model tests
# ------------------------------------------------------------------ #

class TestSessionType:
    """SessionType enum and session_type field on SVPSession."""

    def test_default_is_human(self):
        s = SVPSession(pr_number=1, repository="o/r", verifier_id="v")
        assert s.session_type == SessionType.HUMAN_VERIFICATION

    def test_ai_triage_type(self):
        s = SVPSession(
            pr_number=1, repository="o/r", verifier_id="cascade-ai",
            session_type=SessionType.AI_ADVERSARIAL_TRIAGE,
        )
        assert s.session_type == SessionType.AI_ADVERSARIAL_TRIAGE

    def test_session_type_serializes(self):
        s = SVPSession(
            pr_number=1, repository="o/r", verifier_id="v",
            session_type=SessionType.AI_ADVERSARIAL_TRIAGE,
        )
        data = s.model_dump()
        assert data["session_type"] == "ai_adversarial_triage"
