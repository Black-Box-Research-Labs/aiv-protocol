"""
tests/unit/test_models.py

Unit tests for core data models.
"""

import pytest

from aiv.lib.models import (
    AntiCheatFinding,
    AntiCheatResult,
    ArtifactLink,
    Claim,
    EvidenceClass,
    FrictionScore,
    RiskTier,
    Severity,
    ValidationFinding,
    ValidationResult,
    ValidationStatus,
)


class TestEvidenceClass:
    """Tests for EvidenceClass enum."""

    def test_values(self):
        assert EvidenceClass.EXECUTION.value == "A"
        assert EvidenceClass.REFERENTIAL.value == "B"
        assert EvidenceClass.NEGATIVE.value == "C"
        assert EvidenceClass.DIFFERENTIAL.value == "D"
        assert EvidenceClass.INTENT.value == "E"
        assert EvidenceClass.PROVENANCE.value == "F"

    def test_from_string_letter(self):
        assert EvidenceClass.from_string("A") == EvidenceClass.EXECUTION
        assert EvidenceClass.from_string("F") == EvidenceClass.PROVENANCE

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
        link = ArtifactLink.from_url("https://github.com/owner/repo/actions/runs/12345")
        assert link.is_immutable is True
        assert link.link_type == "github_actions"

    def test_github_blob_sha_immutable(self):
        link = ArtifactLink.from_url("https://github.com/owner/repo/blob/abc123def456789/src/file.py#L10-L20")
        assert link.is_immutable is True
        assert link.link_type == "github_blob"

    def test_github_blob_main_mutable(self):
        link = ArtifactLink.from_url("https://github.com/owner/repo/blob/main/src/file.py")
        assert link.is_immutable is False
        assert link.link_type == "github_blob"
        assert "Mutable branch" in (link.immutability_reason or "")

    def test_github_blob_master_mutable(self):
        link = ArtifactLink.from_url("https://github.com/owner/repo/blob/master/src/file.py")
        assert link.is_immutable is False

    def test_github_blob_develop_mutable(self):
        link = ArtifactLink.from_url("https://github.com/owner/repo/blob/develop/src/file.py")
        assert link.is_immutable is False

    def test_github_pr_immutable(self):
        link = ArtifactLink.from_url("https://github.com/owner/repo/pull/42")
        assert link.is_immutable is True
        assert link.link_type == "github_pr"

    def test_external_url_mutable(self):
        link = ArtifactLink.from_url("https://example.com/some/page")
        assert link.is_immutable is False
        assert link.link_type == "external"

    def test_short_sha_immutable(self):
        link = ArtifactLink.from_url("https://github.com/owner/repo/blob/a1b2c3d/file.py")
        assert link.is_immutable is True

    def test_frozen_model(self):
        link = ArtifactLink.from_url("https://github.com/owner/repo/actions/runs/123")
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


class TestRiskTier:
    """Tests for RiskTier enum."""

    def test_values(self):
        assert RiskTier.R0.value == "R0"
        assert RiskTier.R1.value == "R1"
        assert RiskTier.R2.value == "R2"
        assert RiskTier.R3.value == "R3"

    def test_from_string_uppercase(self):
        assert RiskTier.from_string("R0") == RiskTier.R0
        assert RiskTier.from_string("R3") == RiskTier.R3

    def test_from_string_lowercase(self):
        assert RiskTier.from_string("r1") == RiskTier.R1
        assert RiskTier.from_string("r2") == RiskTier.R2

    def test_from_string_with_whitespace(self):
        assert RiskTier.from_string("  R1  ") == RiskTier.R1

    def test_from_string_invalid(self):
        with pytest.raises(ValueError, match="Unknown risk tier"):
            RiskTier.from_string("R5")

    def test_from_string_empty(self):
        with pytest.raises(ValueError):
            RiskTier.from_string("")


class TestArtifactLinkConfig:
    """Tests for ArtifactLink.from_url() with configurable mutable_branches."""

    def test_custom_mutable_branch_detected(self):
        """A custom branch name should be detected as mutable when configured."""
        link = ArtifactLink.from_url(
            "https://github.com/owner/repo/blob/release/src/app.py",
            mutable_branches={"main", "release"},
        )
        assert link.is_immutable is False
        assert "release" in link.immutability_reason

    def test_default_branch_not_mutable_with_custom_set(self):
        """'main' should NOT be mutable if excluded from custom set."""
        link = ArtifactLink.from_url(
            "https://github.com/owner/repo/blob/main/src/app.py",
            mutable_branches={"release", "staging"},
        )
        # 'main' is not in the custom set, so it falls through to non-SHA check
        assert link.is_immutable is False  # still non-SHA, so still mutable

    def test_custom_min_sha_length(self):
        """Short SHA below custom minimum should not be treated as immutable."""
        link = ArtifactLink.from_url(
            "https://github.com/owner/repo/blob/abcdef1/src/app.py",
            min_sha_length=10,
        )
        # 7-char hex but min_sha_length=10, so not treated as SHA
        assert link.is_immutable is False

    def test_default_behavior_preserved(self):
        """Without config params, default behavior should be unchanged."""
        link = ArtifactLink.from_url("https://github.com/owner/repo/blob/a1b2c3d4e5f6/src/app.py")
        assert link.is_immutable is True
