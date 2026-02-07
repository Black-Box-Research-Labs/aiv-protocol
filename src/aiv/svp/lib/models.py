"""
aiv/svp/lib/models.py

Core data models for the SVP Protocol Suite.
Implements all phases (0-4), session tracking, rating, and validation results
per SVP-SUITE-SPEC-V1.0-CANONICAL §4.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

# ================================================================= #
# Enums
# ================================================================= #


class Complexity(str, Enum):
    """Big-O complexity estimates for predictions."""

    CONSTANT = "O(1)"
    LOGARITHMIC = "O(log n)"
    LINEAR = "O(n)"
    LINEARITHMIC = "O(n log n)"
    QUADRATIC = "O(n²)"
    EXPONENTIAL = "O(2^n)"
    UNKNOWN = "Unknown"


class Confidence(str, Enum):
    """Confidence level for trace predictions."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class SVPPhase(str, Enum):
    """The five phases of SVP execution."""

    SANITY = "phase_0_sanity"
    PREDICTION = "phase_1_prediction"
    TRACE = "phase_2_trace"
    PROBE = "phase_3_probe"
    OWNERSHIP = "phase_4_ownership"


class SVPStatus(str, Enum):
    """Overall SVP completion status."""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    BLOCKED = "blocked"


class BugSeverity(str, Enum):
    """Severity of discovered bugs."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class VerifierTier(str, Enum):
    """Verifier skill tiers based on ELO rating."""

    NOVICE = "novice"
    COMPETENT = "competent"
    PROFICIENT = "proficient"
    EXPERT = "expert"
    MASTER = "master"

    @classmethod
    def from_elo(cls, elo: int) -> VerifierTier:
        """Determine tier from ELO rating."""
        if elo >= 2000:
            return cls.MASTER
        if elo >= 1500:
            return cls.EXPERT
        if elo >= 1000:
            return cls.PROFICIENT
        if elo >= 500:
            return cls.COMPETENT
        return cls.NOVICE


class AITellType(str, Enum):
    """Types of AI Tells to hunt for during adversarial probing."""

    HAPPY_PATH_BIAS = "happy_path_bias"
    CONTEXT_AMNESIA = "context_amnesia"
    FRAGILE_ASSERTIONS = "fragile_assertions"
    MAGIC_NUMBERS = "magic_numbers"
    IMPLICIT_ASSUMPTIONS = "implicit_assumptions"
    MISSING_ERROR_HANDLING = "missing_error_handling"


class SessionType(str, Enum):
    """Whether the session is human verification or AI adversarial triage."""

    HUMAN_VERIFICATION = "human_verification"
    AI_ADVERSARIAL_TRIAGE = "ai_adversarial_triage"


class ValidationSeverity(str, Enum):
    """Severity of SVP validation failures."""

    BLOCK = "block"
    WARN = "warn"
    INFO = "info"


# ================================================================= #
# Phase 1: Black Box Prediction
# ================================================================= #


class PredictionRecord(BaseModel):
    """
    Record of a Black Box Prediction (Phase 1).
    Verifier predicts implementation approach BEFORE viewing the diff.
    """

    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    pr_number: int = Field(ge=1)
    repository: str
    verifier_id: str = Field(min_length=1)

    test_file_path: str = Field(min_length=1)
    predicted_approach: str = Field(
        min_length=50,
        description="How the verifier expects the implementation to work",
    )
    predicted_complexity: Complexity
    expected_edge_cases: list[str] = Field(
        min_length=2,
        description="Edge cases the verifier expects to be handled",
    )
    expected_data_structures: list[str] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    diff_first_viewed_at: datetime | None = None

    @property
    def is_valid_timing(self) -> bool:
        """Prediction must be recorded before viewing the diff."""
        if self.diff_first_viewed_at is None:
            return True
        return self.created_at < self.diff_first_viewed_at


class PredictionComparison(BaseModel):
    """Comparison of prediction against actual implementation."""

    model_config = ConfigDict(frozen=True)

    prediction_id: UUID
    approach_match: Literal["exact", "similar", "different"]
    complexity_match: bool
    edge_cases_predicted: int
    edge_cases_in_impl: int
    edge_cases_matched: int
    accuracy_score: int = Field(ge=0, le=100)

    @classmethod
    def calculate(
        cls,
        prediction: PredictionRecord,
        actual_complexity: Complexity,
        actual_edge_cases: list[str],
        approach_assessment: Literal["exact", "similar", "different"],
    ) -> PredictionComparison:
        """Calculate prediction accuracy score (0-100)."""
        matched = len(set(prediction.expected_edge_cases) & set(actual_edge_cases))

        score = 0
        if approach_assessment == "exact":
            score += 50
        elif approach_assessment == "similar":
            score += 30

        if prediction.predicted_complexity == actual_complexity:
            score += 25

        if len(prediction.expected_edge_cases) > 0:
            score += int((matched / len(prediction.expected_edge_cases)) * 25)

        return cls(
            prediction_id=prediction.id,
            approach_match=approach_assessment,
            complexity_match=prediction.predicted_complexity == actual_complexity,
            edge_cases_predicted=len(prediction.expected_edge_cases),
            edge_cases_in_impl=len(actual_edge_cases),
            edge_cases_matched=matched,
            accuracy_score=min(100, score),
        )


# ================================================================= #
# Phase 2: Mental Trace
# ================================================================= #


class StateTransition(BaseModel):
    """A single state transition during mental trace."""

    model_config = ConfigDict(frozen=True)

    step_number: int = Field(ge=1)
    variable_name: str
    before_value: str
    after_value: str


class TraceRecord(BaseModel):
    """
    Record of a Mental Trace (Phase 2).

    For human verifiers: mental simulation without running code.
    For AI verifiers (S015): must include verified_output from actual execution.
    """

    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    pr_number: int = Field(ge=1)
    repository: str
    verifier_id: str = Field(min_length=1)

    function_path: str = Field(min_length=1)
    trace_notes: str = Field(min_length=100)
    state_transitions: list[StateTransition] = Field(default_factory=list)

    edge_case_tested: str = Field(min_length=10)
    predicted_output: str = Field(min_length=1)
    verified_output: str | None = Field(
        default=None,
        description="S015: Actual stdout/return value from execution. Required for AI sessions.",
    )

    confidence: Confidence
    uncertainty_notes: str | None = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ================================================================= #
# Phase 3: Adversarial Probe
# ================================================================= #


class ProbeFinding(BaseModel):
    """A finding from adversarial probing."""

    model_config = ConfigDict(frozen=True)

    finding_type: AITellType
    file_path: str
    line_number: int | None = None
    description: str = Field(min_length=10)
    severity: BugSeverity
    is_confirmed_bug: bool = False


class WhyQuestion(BaseModel):
    """A 'Why?' question asked during probing."""

    model_config = ConfigDict(frozen=True)

    question: str = Field(min_length=10)
    context: str
    answer_found: bool = False
    answer: str | None = None


class FalsificationScenario(BaseModel):
    """A scenario defined by the verifier to prove a claim false.

    Forces the verifier to think: 'What specific evidence in the linked
    artifact would prove this claim is a lie?'
    """

    model_config = ConfigDict(frozen=True)

    claim_id: str = Field(min_length=1, description="Claim identifier, e.g. 'C-001'")
    scenario: str = Field(
        min_length=25,
        description="Evidence that would prove this claim is false",
    )
    test_code: str | None = Field(
        default=None,
        description="S016: Executable pytest snippet that tests the scenario. Required for AI sessions.",
    )
    checked: bool = False
    result: Literal["confirmed", "falsified", "inconclusive"] = "confirmed"
    false_positive: bool = Field(
        default=False,
        description=(
            "True if the scenario itself was wrong (hallucinated, wrong count, untestable). Penalized in rating."
        ),
    )


class ProbeRecord(BaseModel):
    """
    Record of an Adversarial Probe (Phase 3).
    Verifier hunts for AI Tells and subtle hallucinations.
    """

    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    pr_number: int = Field(ge=1)
    repository: str
    verifier_id: str = Field(min_length=1)

    happy_path_bias_checked: bool
    context_amnesia_checked: bool
    fragile_assertions_checked: bool

    findings: list[ProbeFinding] = Field(default_factory=list)
    why_questions: list[WhyQuestion] = Field(min_length=1)
    falsification_scenarios: list[FalsificationScenario] = Field(
        default_factory=list,
        description="Scenarios that would prove primary claims false",
    )

    overall_assessment: str = Field(min_length=20)

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def checklist_complete(self) -> bool:
        """All checklist items must be marked."""
        return all(
            [
                self.happy_path_bias_checked,
                self.context_amnesia_checked,
                self.fragile_assertions_checked,
            ]
        )

    @property
    def bugs_found(self) -> list[ProbeFinding]:
        return [f for f in self.findings if f.is_confirmed_bug]


# ================================================================= #
# Phase 4: Ownership Lock
# ================================================================= #


class RenameChange(BaseModel):
    """A variable/function rename in an ownership commit."""

    model_config = ConfigDict(frozen=True)

    file_path: str
    original_name: str
    new_name: str
    change_type: Literal["variable", "function", "class", "parameter"]
    justification: str = Field(min_length=10)


class DocstringChange(BaseModel):
    """A docstring addition/modification in an ownership commit."""

    model_config = ConfigDict(frozen=True)

    file_path: str
    function_name: str
    docstring_content: str = Field(min_length=20)
    includes_why: bool = False
    includes_invariant: bool = False
    includes_risk: bool = False


class OwnershipCommit(BaseModel):
    """
    Record of an Ownership Lock commit (Phase 4).
    Verifier must push a commit with semantic renames or docstrings.
    """

    model_config = ConfigDict(frozen=True)

    pr_number: int = Field(ge=1)
    repository: str

    commit_sha: str = Field(min_length=7, max_length=64)
    author_github_id: str = Field(min_length=1)
    commit_message: str
    committed_at: datetime

    renames: list[RenameChange] = Field(default_factory=list)
    docstrings: list[DocstringChange] = Field(default_factory=list)

    verified_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def follows_message_pattern(self) -> bool:
        """Commit message should start with 'ownership:'."""
        return self.commit_message.lower().startswith("ownership:")

    @property
    def has_substantive_changes(self) -> bool:
        return len(self.renames) > 0 or len(self.docstrings) > 0

    @property
    def docstring_quality_score(self) -> int:
        """Quality score for docstrings (0-100)."""
        if not self.docstrings:
            return 0
        total = 0
        for ds in self.docstrings:
            score = 40
            if ds.includes_why:
                score += 20
            if ds.includes_invariant:
                score += 20
            if ds.includes_risk:
                score += 20
            total += score
        return total // len(self.docstrings)


# ================================================================= #
# SVP Session
# ================================================================= #


class SVPSession(BaseModel):
    """
    Complete SVP session for a single PR verification.
    Tracks completion of all phases.
    """

    model_config = ConfigDict(frozen=False)

    id: UUID = Field(default_factory=uuid4)
    pr_number: int = Field(ge=1)
    repository: str
    verifier_id: str = Field(min_length=1)
    session_type: SessionType = Field(
        default=SessionType.HUMAN_VERIFICATION,
        description="Whether this is a human verification or AI adversarial triage session.",
    )
    packet_ref: str = Field(
        default="",
        description=(
            "Verification packet filename this session verifies, e.g. VERIFICATION_PACKET_AIV_IMPLEMENTATION.md"
        ),
    )

    prediction: PredictionRecord | None = None
    traces: list[TraceRecord] = Field(default_factory=list)
    probe: ProbeRecord | None = None
    ownership_commit: OwnershipCommit | None = None

    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: datetime | None = None

    aiv_guard_passed: bool = False
    aiv_guard_passed_at: datetime | None = None

    @property
    def status(self) -> SVPStatus:
        if not self.aiv_guard_passed:
            return SVPStatus.BLOCKED

        phases = [
            self.prediction is not None,
            len(self.traces) > 0,
            self.probe is not None and self.probe.checklist_complete,
            (self.ownership_commit is not None and self.ownership_commit.has_substantive_changes),
        ]

        if all(phases):
            return SVPStatus.COMPLETE
        if any(phases):
            return SVPStatus.IN_PROGRESS
        return SVPStatus.NOT_STARTED

    @property
    def missing_phases(self) -> list[SVPPhase]:
        missing: list[SVPPhase] = []
        if not self.aiv_guard_passed:
            missing.append(SVPPhase.SANITY)
        if self.prediction is None:
            missing.append(SVPPhase.PREDICTION)
        if len(self.traces) == 0:
            missing.append(SVPPhase.TRACE)
        if self.probe is None or not self.probe.checklist_complete:
            missing.append(SVPPhase.PROBE)
        if self.ownership_commit is None or not self.ownership_commit.has_substantive_changes:
            missing.append(SVPPhase.OWNERSHIP)
        return missing

    @property
    def completion_percentage(self) -> int:
        total = 5
        done = total - len(self.missing_phases)
        return int((done / total) * 100)


# ================================================================= #
# Bug Reports
# ================================================================= #


class BugReport(BaseModel):
    """Bug discovered during SVP verification."""

    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    pr_number: int = Field(ge=1)
    repository: str
    verifier_id: str = Field(min_length=1)

    file_path: str
    line_start: int = Field(ge=1)
    line_end: int | None = None

    severity: BugSeverity
    bug_type: AITellType

    title: str = Field(min_length=10)
    description: str = Field(min_length=50)
    expected_behavior: str = Field(min_length=20)
    actual_behavior: str = Field(min_length=20)

    reproduction_steps: str
    related_trace_id: UUID | None = None
    related_probe_id: UUID | None = None

    confirmed: bool = False
    false_positive: bool = False

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


# ================================================================= #
# Rating
# ================================================================= #

RATING_POINTS: dict[str, int] = {
    "bug_caught_critical": 50,
    "bug_caught_high": 30,
    "bug_caught_medium": 15,
    "bug_caught_low": 5,
    "false_positive": -10,
    "bug_missed": -25,
    "prediction_accurate": 10,
    "prediction_inaccurate": -5,
    "ownership_high_quality": 15,
    "svp_completed": 5,
}


class RatingEvent(BaseModel):
    """An event that affects a verifier's rating."""

    model_config = ConfigDict(frozen=True)

    id: UUID = Field(default_factory=uuid4)
    verifier_id: str = Field(min_length=1)
    event_type: str
    points: int
    pr_number: int | None = None
    repository: str | None = None
    description: str

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class VerifierRating(BaseModel):
    """A verifier's current rating and statistics."""

    model_config = ConfigDict(frozen=False)

    verifier_id: str = Field(min_length=1)
    elo_rating: int = Field(default=500, ge=0)
    tier: VerifierTier = Field(default=VerifierTier.NOVICE)

    total_reviews: int = Field(default=0, ge=0)
    bugs_caught: int = Field(default=0, ge=0)
    bugs_missed: int = Field(default=0, ge=0)
    false_positives: int = Field(default=0, ge=0)

    avg_prediction_accuracy: float = Field(default=0.0, ge=0.0, le=100.0)
    avg_docstring_quality: float = Field(default=0.0, ge=0.0, le=100.0)

    current_streak: int = Field(default=0, ge=0)
    longest_streak: int = Field(default=0, ge=0)

    last_review_at: datetime | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def update_tier(self) -> None:
        self.tier = VerifierTier.from_elo(self.elo_rating)

    def apply_event(self, event: RatingEvent) -> None:
        self.elo_rating = max(0, self.elo_rating + event.points)
        self.update_tier()


# ================================================================= #
# Validation Results
# ================================================================= #


class SVPValidationError(BaseModel):
    """A single SVP validation error."""

    model_config = ConfigDict(frozen=True)

    rule_id: str
    phase: SVPPhase
    severity: ValidationSeverity
    message: str
    suggestion: str | None = None


class SVPValidationResult(BaseModel):
    """Complete SVP validation result for a PR."""

    model_config = ConfigDict(frozen=True)

    pr_number: int
    repository: str
    verifier_id: str

    status: SVPStatus

    phase_0_complete: bool = False
    phase_1_complete: bool = False
    phase_2_complete: bool = False
    phase_3_complete: bool = False
    phase_4_complete: bool = False

    errors: list[SVPValidationError] = Field(default_factory=list)
    warnings: list[SVPValidationError] = Field(default_factory=list)

    validated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def blocking_errors(self) -> list[SVPValidationError]:
        return [e for e in self.errors if e.severity == ValidationSeverity.BLOCK]

    @property
    def is_complete(self) -> bool:
        return (
            all(
                [
                    self.phase_0_complete,
                    self.phase_1_complete,
                    self.phase_2_complete,
                    self.phase_3_complete,
                    self.phase_4_complete,
                ]
            )
            and len(self.blocking_errors) == 0
        )

    @property
    def completion_percentage(self) -> int:
        phases = [
            self.phase_0_complete,
            self.phase_1_complete,
            self.phase_2_complete,
            self.phase_3_complete,
            self.phase_4_complete,
        ]
        return int((sum(phases) / len(phases)) * 100)
