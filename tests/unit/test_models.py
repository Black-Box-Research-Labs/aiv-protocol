"""
tests/unit/test_models.py

Unit tests for core data models.
"""

import pytest
from aiv.lib.models import (
    EvidenceClass,
    Severity,
    ValidationStatus,
    ArtifactLink,
    Claim,
    IntentSection,
    VerificationPacket,
    ValidationFinding,
    ValidationResult,
    AntiCheatFinding,
    AntiCheatResult,
    FrictionScore,
)


class TestEvidenceClass:
    """Tests for EvidenceClass enum."""

    def test_values(self):
        assert EvidenceClass.EXECUTION.value == "A"
        assert EvidenceClass.REFERENTIAL.value == "B"
        assert EvidenceClass.NEGATIVE.value == "C"
        assert EvidenceClass.STATE.value == "D"
        assert EvidenceClass.INTENT.value == "E"
        assert EvidenceClass.CONSERVATION.value == "F"

    def test_from_string_letter(self):
        assert EvidenceClass.from_string("A") == EvidenceClass.EXECUTION
        assert EvidenceClass.from_string("F") == EvidenceClass.CONSERVATION

    def test_from_string_name(self):
        assert EvidenceClass.from_string("EXECUTION") == EvidenceClass.EXECUTION

    def test_from_string_with_description(self):
        assert EvidenceClass.from_string("A (Execution)") == EvidenceClass.EXECUTION
        assert EvidenceClass.from_string("B (Referential)") == EvidenceClass.REFERENTIAL

    def test_from_string_invalid(self):
        with pytest.raises(ValueError, match="Unknown evidence class"):
            EvidenceClass.from_string("Z")

    def test_from_string_case_insensitive(self):
        assert EvidenceClass.from_string("a") == EvidenceClass.EXECUTION
        assert EvidenceClass.from_string("execution") == EvidenceClass.EXECUTION


class TestArtifactLink:
    """Tests for ArtifactLink URL parsing and immutability detection."""

    def test_github_actions_immutable(self):
        link = ArtifactLink.from_url(
            "https://github.com/owner/repo/actions/runs/12345"
        )
        assert link.is_immutable is True
        assert link.link_type == "github_actions"

    def test_github_blob_sha_immutable(self):
        link = ArtifactLink.from_url(
            "https://github.com/owner/repo/blob/abc123def456789/src/file.py#L10-L20"
        )
        assert link.is_immutable is True
        assert link.link_type == "github_blob"

    def test_github_blob_main_mutable(self):
        link = ArtifactLink.from_url(
            "https://github.com/owner/repo/blob/main/src/file.py"
        )
        assert link.is_immutable is False
        assert link.link_type == "github_blob"
        assert "Mutable branch" in (link.immutability_reason or "")

    def test_github_blob_master_mutable(self):
        link = ArtifactLink.from_url(
            "https://github.com/owner/repo/blob/master/src/file.py"
        )
        assert link.is_immutable is False

    def test_github_blob_develop_mutable(self):
        link = ArtifactLink.from_url(
            "https://github.com/owner/repo/blob/develop/src/file.py"
        )
        assert link.is_immutable is False

    def test_github_pr_immutable(self):
        link = ArtifactLink.from_url(
            "https://github.com/owner/repo/pull/42"
        )
        assert link.is_immutable is True
        assert link.link_type == "github_pr"

    def test_external_url_mutable(self):
        link = ArtifactLink.from_url("https://example.com/some/page")
        assert link.is_immutable is False
        assert link.link_type == "external"

    def test_short_sha_immutable(self):
        link = ArtifactLink.from_url(
            "https://github.com/owner/repo/blob/a1b2c3d/file.py"
        )
        assert link.is_immutable is True

    def test_frozen_model(self):
        link = ArtifactLink.from_url(
            "https://github.com/owner/repo/actions/runs/123"
        )
        with pytest.raises(Exception):
            link.url = "https://other.com"


class TestClaim:
    """Tests for Claim model."""

    def test_valid_claim(self):
        claim = Claim(
            section_number=1,
            description="Implements new API endpoint for user auth",
            evidence_class=EvidenceClass.EXECUTION,
            artifact="https://example.com/ci/run/123",
            reproduction="CI Automation",
        )
        assert claim.section_number == 1
        assert claim.evidence_class == EvidenceClass.EXECUTION

    def test_description_min_length(self):
        with pytest.raises(Exception):
            Claim(
                section_number=1,
                description="short",
                evidence_class=EvidenceClass.EXECUTION,
                artifact="test",
                reproduction="N/A",
            )

    def test_section_number_must_be_positive(self):
        with pytest.raises(Exception):
            Claim(
                section_number=0,
                description="Valid description here",
                evidence_class=EvidenceClass.EXECUTION,
                artifact="test",
                reproduction="N/A",
            )


class TestValidationFinding:
    """Tests for ValidationFinding model."""

    def test_valid_rule_id(self):
        finding = ValidationFinding(
            rule_id="E001",
            severity=Severity.BLOCK,
            message="Test error message",
        )
        assert finding.rule_id == "E001"

    def test_invalid_rule_id(self):
        with pytest.raises(Exception):
            ValidationFinding(
                rule_id="X001",
                severity=Severity.BLOCK,
                message="Bad rule ID",
            )


class TestValidationResult:
    """Tests for ValidationResult model."""

    def test_is_valid_no_errors(self):
        result = ValidationResult(
            status=ValidationStatus.PASS,
            errors=[],
        )
        assert result.is_valid is True

    def test_is_valid_with_blocking_error(self):
        result = ValidationResult(
            status=ValidationStatus.FAIL,
            errors=[
                ValidationFinding(
                    rule_id="E001",
                    severity=Severity.BLOCK,
                    message="Error",
                )
            ],
        )
        assert result.is_valid is False

    def test_blocking_errors_filters_correctly(self):
        result = ValidationResult(
            status=ValidationStatus.FAIL,
            errors=[
                ValidationFinding(rule_id="E001", severity=Severity.BLOCK, message="Block"),
                ValidationFinding(rule_id="E002", severity=Severity.WARN, message="Warn"),
            ],
        )
        assert len(result.blocking_errors) == 1
        assert result.blocking_errors[0].rule_id == "E001"


class TestAntiCheatResult:
    """Tests for AntiCheatResult model."""

    def test_has_violations_false_when_empty(self):
        result = AntiCheatResult(
            findings=[],
            files_analyzed=5,
            test_files_modified=0,
        )
        assert result.has_violations is False

    def test_has_violations_true_with_block(self):
        result = AntiCheatResult(
            findings=[
                AntiCheatFinding(
                    finding_type="deleted_assertion",
                    file_path="tests/test_auth.py",
                    severity=Severity.BLOCK,
                )
            ],
            files_analyzed=3,
            test_files_modified=1,
        )
        assert result.has_violations is True

    def test_requires_justification(self):
        result = AntiCheatResult(
            findings=[
                AntiCheatFinding(
                    finding_type="skipped_test",
                    file_path="tests/test_pay.py",
                    requires_justification=True,
                )
            ],
            files_analyzed=2,
            test_files_modified=1,
        )
        assert result.requires_justification is True


class TestFrictionScore:
    """Tests for FrictionScore model."""

    def test_zero_friction(self):
        score = FrictionScore(
            score=0,
            step_count=0,
            prohibited_patterns_found=[],
            is_zero_touch_compliant=True,
        )
        assert score.is_zero_touch_compliant is True

    def test_high_friction(self):
        score = FrictionScore(
            score=30,
            step_count=5,
            prohibited_patterns_found=["git clone", "npm install"],
            is_zero_touch_compliant=False,
            recommendation="Use CI artifacts instead",
        )
        assert score.is_zero_touch_compliant is False
        assert score.score == 30
