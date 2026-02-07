"""
tests/unit/test_validators.py

Unit tests for validator fixes — zero-touch code block stripping,
bug-fix heuristic word boundaries, provenance negative framing,
and risk-tier evidence enforcement.
"""

import pytest
from aiv.lib.models import (
    Claim,
    EvidenceClass,
    FrictionScore,
    IntentSection,
    RiskTier,
    Severity,
    VerificationPacket,
)
from aiv.lib.validators.zero_touch import ZeroTouchValidator
from aiv.lib.validators.evidence import EvidenceValidator
from aiv.lib.validators.pipeline import ValidationPipeline
from aiv.lib.config import AIVConfig


# ============================================================================
# Zero-Touch Validator Tests
# ============================================================================

class TestZeroTouchCodeBlockStripping:
    """Tests for code block stripping in zero-touch validator."""

    @pytest.fixture
    def validator(self):
        return ZeroTouchValidator()

    def _make_claim(self, reproduction: str) -> Claim:
        return Claim(
            section_number=1,
            description="Test claim with sufficient length for validation",
            evidence_class=EvidenceClass.REFERENTIAL,
            artifact="See evidence section",
            reproduction=reproduction,
        )

    def test_code_block_commands_not_flagged(self, validator):
        """Commands inside fenced code blocks should NOT trigger violations."""
        claim = self._make_claim(
            "**Zero-Touch Mandate:** Verifier inspects artifacts only.\n\n"
            "**Context only:**\n"
            "```bash\npython -m pytest tests/ -v\n```"
        )
        errors, friction = validator.validate_claim(claim)
        blocking = [e for e in errors if e.severity == Severity.BLOCK]
        assert len(blocking) == 0

    def test_bare_commands_still_flagged(self, validator):
        """Commands outside code blocks SHOULD trigger violations."""
        claim = self._make_claim("Run: git clone repo && npm install && npm test")
        errors, friction = validator.validate_claim(claim)
        blocking = [e for e in errors if e.severity == Severity.BLOCK]
        assert len(blocking) > 0

    def test_compliance_phrase_early_exit(self, validator):
        """Compliance phrases should cause immediate pass."""
        claim = self._make_claim(
            "**Zero-Touch Mandate:** Verifier inspects artifacts only."
        )
        errors, friction = validator.validate_claim(claim)
        assert len(errors) == 0
        assert friction.is_zero_touch_compliant is True

    def test_no_verification_needed_compliant(self, validator):
        """'No verification needed' should be compliant."""
        claim = self._make_claim("No verification needed — empty file.")
        errors, friction = validator.validate_claim(claim)
        assert len(errors) == 0
        assert friction.is_zero_touch_compliant is True

    def test_na_still_compliant(self, validator):
        """N/A reproduction should still be compliant."""
        claim = self._make_claim("N/A")
        errors, friction = validator.validate_claim(claim)
        assert len(errors) == 0
        assert friction.is_zero_touch_compliant is True


# ============================================================================
# Bug-Fix Heuristic Tests
# ============================================================================

class TestBugFixHeuristic:
    """Tests for word-boundary bug-fix detection in EvidenceValidator."""

    @pytest.fixture
    def validator(self):
        return EvidenceValidator()

    def _make_packet(self, intent_text: str, claim_descs: list[str]) -> VerificationPacket:
        return VerificationPacket(
            version="2.1",
            intent=IntentSection(
                evidence_link="Spec reference with enough characters here",
                verifier_check=intent_text,
            ),
            claims=[
                Claim(
                    section_number=i + 1,
                    description=desc,
                    evidence_class=EvidenceClass.REFERENTIAL,
                    artifact="See evidence section",
                    reproduction="N/A",
                )
                for i, desc in enumerate(claim_descs)
            ],
            raw_markdown="# AIV Verification Packet (v2.1)\n...",
        )

    def test_fix_triggers_bug_fix_detection(self, validator):
        """Word 'fix' should trigger bug-fix heuristic."""
        packet = self._make_packet(
            "Fix the authentication flow for SSO users",
            ["Authentication flow now handles SAML correctly"],
        )
        assert validator._is_bug_fix(packet) is True

    def test_prefix_does_not_trigger(self, validator):
        """'prefix' should NOT trigger (contains 'fix' as substring)."""
        packet = self._make_packet(
            "Add prefix handling for CSS class names",
            ["CSS prefix handling added for cross-browser support"],
        )
        assert validator._is_bug_fix(packet) is False

    def test_tissue_does_not_trigger(self, validator):
        """'tissue' should NOT trigger (contains 'issue' as substring)."""
        packet = self._make_packet(
            "Implement tissue sample tracking module",
            ["Sample tracking module processes tissue data correctly"],
        )
        assert validator._is_bug_fix(packet) is False

    def test_issue_number_triggers(self, validator):
        """'issue #42' should trigger."""
        packet = self._make_packet(
            "Resolve issue #42 in authentication module",
            ["Authentication module updated per requirements"],
        )
        assert validator._is_bug_fix(packet) is True

    def test_hotfix_triggers(self, validator):
        """'hotfix' should trigger."""
        packet = self._make_packet(
            "Apply hotfix for production deployment error",
            ["Deployment script updated with correct paths"],
        )
        assert validator._is_bug_fix(packet) is True

    def test_closes_hash_triggers(self, validator):
        """'closes #123' should trigger."""
        packet = self._make_packet(
            "Update login flow, closes #123",
            ["Login flow updated for edge case"],
        )
        assert validator._is_bug_fix(packet) is True

    def test_no_bug_keywords(self, validator):
        """Normal feature description should not trigger."""
        packet = self._make_packet(
            "Implement new dashboard widget for analytics",
            ["Dashboard widget displays real-time metrics"],
        )
        assert validator._is_bug_fix(packet) is False


# ============================================================================
# Provenance Negative Framing Tests
# ============================================================================

class TestProvenanceNegativeFraming:
    """Tests for provenance validator negative framing logic."""

    @pytest.fixture
    def validator(self):
        return EvidenceValidator()

    def _make_provenance_claim(self, description: str) -> Claim:
        return Claim(
            section_number=1,
            description=description,
            evidence_class=EvidenceClass.PROVENANCE,
            artifact="See evidence section",
            reproduction="N/A",
        )

    def test_negative_framing_no_justification_needed(self, validator):
        """'No existing tests modified' should NOT require justification."""
        claim = self._make_provenance_claim(
            "No existing tests were modified or deleted during this change."
        )
        errors = validator._validate_provenance(claim)
        assert len(errors) == 0

    def test_preserved_framing_no_justification_needed(self, validator):
        """'Tests preserved' should NOT require justification."""
        claim = self._make_provenance_claim(
            "All existing test assertions were preserved unchanged."
        )
        errors = validator._validate_provenance(claim)
        assert len(errors) == 0

    def test_test_modification_requires_justification(self, validator):
        """Test modification without negative framing SHOULD warn."""
        claim = self._make_provenance_claim(
            "Updated test assertions to match new API response format."
        )
        errors = validator._validate_provenance(claim)
        e011 = [e for e in errors if e.rule_id == "E011"]
        assert len(e011) == 1
        assert e011[0].severity == Severity.WARN

    def test_non_test_claim_no_warning(self, validator):
        """Provenance claim without test keywords should not warn."""
        claim = self._make_provenance_claim(
            "Configuration file backed up before migration."
        )
        errors = validator._validate_provenance(claim)
        assert len(errors) == 0


# ============================================================================
# Risk-Tier Evidence Enforcement Tests
# ============================================================================

class TestRiskTierEnforcement:
    """Tests for pipeline risk-tier evidence requirement enforcement."""

    @pytest.fixture
    def pipeline(self):
        return ValidationPipeline(AIVConfig(strict_mode=False))

    def _make_packet_with_classes(
        self, tier: RiskTier, classes: set[EvidenceClass]
    ) -> VerificationPacket:
        claims = []
        for i, ec in enumerate(classes - {EvidenceClass.INTENT}, start=1):
            claims.append(Claim(
                section_number=i,
                description=f"Claim {i} with sufficient description for validation.",
                evidence_class=ec,
                artifact="See evidence section",
                reproduction="N/A",
            ))
        if not claims:
            claims.append(Claim(
                section_number=1,
                description="Default claim with enough text for validation checks.",
                evidence_class=EvidenceClass.REFERENTIAL,
                artifact="See evidence section",
                reproduction="N/A",
            ))
        return VerificationPacket(
            version="2.1",
            risk_tier=tier,
            evidence_classes_present=classes,
            intent=IntentSection(
                evidence_link="Spec reference with enough text for validation",
                verifier_check="Verify the implementation matches spec requirements",
            ),
            claims=claims,
            raw_markdown="# AIV Verification Packet (v2.1)\n...",
        )

    def test_r0_needs_a_and_b(self, pipeline):
        """R0 requires Class A and B."""
        findings = pipeline._check_tier_requirements(
            self._make_packet_with_classes(
                RiskTier.R0,
                {EvidenceClass.EXECUTION, EvidenceClass.REFERENTIAL}
            )
        )
        blocking = [f for f in findings if f.severity == Severity.BLOCK]
        assert len(blocking) == 0

    def test_r0_missing_a_blocks(self, pipeline):
        """R0 missing Class A should block."""
        findings = pipeline._check_tier_requirements(
            self._make_packet_with_classes(
                RiskTier.R0,
                {EvidenceClass.REFERENTIAL}
            )
        )
        blocking = [f for f in findings if f.severity == Severity.BLOCK]
        assert len(blocking) == 1
        assert "Class A" in blocking[0].message

    def test_r1_needs_a_b_e(self, pipeline):
        """R1 requires A, B, E."""
        findings = pipeline._check_tier_requirements(
            self._make_packet_with_classes(
                RiskTier.R1,
                {EvidenceClass.EXECUTION, EvidenceClass.REFERENTIAL, EvidenceClass.INTENT}
            )
        )
        blocking = [f for f in findings if f.severity == Severity.BLOCK]
        assert len(blocking) == 0

    def test_r2_needs_c(self, pipeline):
        """R2 requires A, B, E, C. Missing C should block."""
        findings = pipeline._check_tier_requirements(
            self._make_packet_with_classes(
                RiskTier.R2,
                {EvidenceClass.EXECUTION, EvidenceClass.REFERENTIAL, EvidenceClass.INTENT}
            )
        )
        blocking = [f for f in findings if f.severity == Severity.BLOCK]
        assert any("Class C" in f.message for f in blocking)

    def test_r3_needs_all_six(self, pipeline):
        """R3 requires A, B, C, D, E, F."""
        findings = pipeline._check_tier_requirements(
            self._make_packet_with_classes(
                RiskTier.R3,
                {
                    EvidenceClass.EXECUTION, EvidenceClass.REFERENTIAL,
                    EvidenceClass.NEGATIVE, EvidenceClass.DIFFERENTIAL,
                    EvidenceClass.INTENT, EvidenceClass.PROVENANCE,
                }
            )
        )
        blocking = [f for f in findings if f.severity == Severity.BLOCK]
        assert len(blocking) == 0

    def test_r3_missing_d_blocks(self, pipeline):
        """R3 missing Class D should block."""
        findings = pipeline._check_tier_requirements(
            self._make_packet_with_classes(
                RiskTier.R3,
                {
                    EvidenceClass.EXECUTION, EvidenceClass.REFERENTIAL,
                    EvidenceClass.NEGATIVE, EvidenceClass.INTENT,
                    EvidenceClass.PROVENANCE,
                }
            )
        )
        blocking = [f for f in findings if f.severity == Severity.BLOCK]
        assert any("Class D" in f.message for f in blocking)

    def test_no_classification_warns(self, pipeline):
        """Missing classification should produce E014 warning."""
        packet = VerificationPacket(
            version="2.1",
            risk_tier=None,
            intent=IntentSection(
                evidence_link="Spec reference with enough text for validation",
                verifier_check="Verify the implementation matches spec requirements",
            ),
            claims=[Claim(
                section_number=1,
                description="Claim with enough text for validation checks to pass.",
                evidence_class=EvidenceClass.REFERENTIAL,
                artifact="See evidence section",
                reproduction="N/A",
            )],
            raw_markdown="# AIV Verification Packet (v2.1)\n...",
        )
        findings = pipeline._check_tier_requirements(packet)
        assert any(f.rule_id == "E014" and f.severity == Severity.WARN for f in findings)

    def test_r2_optional_d_and_f_info(self, pipeline):
        """R2 should produce INFO for missing optional D and F."""
        findings = pipeline._check_tier_requirements(
            self._make_packet_with_classes(
                RiskTier.R2,
                {
                    EvidenceClass.EXECUTION, EvidenceClass.REFERENTIAL,
                    EvidenceClass.INTENT, EvidenceClass.NEGATIVE,
                }
            )
        )
        info = [f for f in findings if f.severity == Severity.INFO]
        assert len(info) >= 1  # At least D or F recommended
