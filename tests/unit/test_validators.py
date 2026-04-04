"""
tests/unit/test_validators.py

Unit tests for validator fixes — zero-touch code block stripping,
bug-fix heuristic word boundaries, provenance negative framing,
and risk-tier evidence enforcement.
"""

import pytest

from aiv.lib.config import AIVConfig
from aiv.lib.models import (
    AntiCheatFinding,
    AntiCheatResult,
    Claim,
    EvidenceClass,
    IntentSection,
    RiskTier,
    Severity,
    VerificationPacket,
)
from aiv.lib.validators.evidence import EvidenceValidator
from aiv.lib.validators.links import LinkValidator
from aiv.lib.validators.pipeline import ValidationPipeline
from aiv.lib.validators.zero_touch import ZeroTouchValidator

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
        claim = self._make_claim("**Zero-Touch Mandate:** Verifier inspects artifacts only.")
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
        claim = self._make_provenance_claim("No existing tests were modified or deleted during this change.")
        errors = validator._validate_provenance(claim)
        assert len(errors) == 0

    def test_preserved_framing_no_justification_needed(self, validator):
        """'Tests preserved' should NOT require justification."""
        claim = self._make_provenance_claim("All existing test assertions were preserved unchanged.")
        errors = validator._validate_provenance(claim)
        assert len(errors) == 0

    def test_test_modification_requires_justification(self, validator):
        """Test modification without negative framing SHOULD warn."""
        claim = self._make_provenance_claim("Updated test assertions to match new API response format.")
        errors = validator._validate_provenance(claim)
        e011 = [e for e in errors if e.rule_id == "E011"]
        assert len(e011) == 1
        assert e011[0].severity == Severity.WARN

    def test_non_test_claim_no_warning(self, validator):
        """Provenance claim without test keywords should not warn."""
        claim = self._make_provenance_claim("Configuration file backed up before migration.")
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

    def _make_packet_with_classes(self, tier: RiskTier, classes: set[EvidenceClass]) -> VerificationPacket:
        claims = []
        for i, ec in enumerate(classes - {EvidenceClass.INTENT}, start=1):
            claims.append(
                Claim(
                    section_number=i,
                    description=f"Claim {i} with sufficient description for validation.",
                    evidence_class=ec,
                    artifact="See evidence section",
                    reproduction="N/A",
                )
            )
        if not claims:
            claims.append(
                Claim(
                    section_number=1,
                    description="Default claim with enough text for validation checks.",
                    evidence_class=EvidenceClass.REFERENTIAL,
                    artifact="See evidence section",
                    reproduction="N/A",
                )
            )
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
            self._make_packet_with_classes(RiskTier.R0, {EvidenceClass.EXECUTION, EvidenceClass.REFERENTIAL})
        )
        blocking = [f for f in findings if f.severity == Severity.BLOCK]
        assert len(blocking) == 0

    def test_r0_missing_a_blocks(self, pipeline):
        """R0 missing Class A should block."""
        findings = pipeline._check_tier_requirements(
            self._make_packet_with_classes(RiskTier.R0, {EvidenceClass.REFERENTIAL})
        )
        blocking = [f for f in findings if f.severity == Severity.BLOCK]
        assert len(blocking) == 1
        assert "Class A" in blocking[0].message

    def test_r1_needs_a_b_e(self, pipeline):
        """R1 requires A, B, E."""
        findings = pipeline._check_tier_requirements(
            self._make_packet_with_classes(
                RiskTier.R1, {EvidenceClass.EXECUTION, EvidenceClass.REFERENTIAL, EvidenceClass.INTENT}
            )
        )
        blocking = [f for f in findings if f.severity == Severity.BLOCK]
        assert len(blocking) == 0

    def test_r2_needs_c(self, pipeline):
        """R2 requires A, B, E, C. Missing C should block."""
        findings = pipeline._check_tier_requirements(
            self._make_packet_with_classes(
                RiskTier.R2, {EvidenceClass.EXECUTION, EvidenceClass.REFERENTIAL, EvidenceClass.INTENT}
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
                    EvidenceClass.EXECUTION,
                    EvidenceClass.REFERENTIAL,
                    EvidenceClass.NEGATIVE,
                    EvidenceClass.DIFFERENTIAL,
                    EvidenceClass.INTENT,
                    EvidenceClass.PROVENANCE,
                },
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
                    EvidenceClass.EXECUTION,
                    EvidenceClass.REFERENTIAL,
                    EvidenceClass.NEGATIVE,
                    EvidenceClass.INTENT,
                    EvidenceClass.PROVENANCE,
                },
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
            claims=[
                Claim(
                    section_number=1,
                    description="Claim with enough text for validation checks to pass.",
                    evidence_class=EvidenceClass.REFERENTIAL,
                    artifact="See evidence section",
                    reproduction="N/A",
                )
            ],
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
                    EvidenceClass.EXECUTION,
                    EvidenceClass.REFERENTIAL,
                    EvidenceClass.INTENT,
                    EvidenceClass.NEGATIVE,
                },
            )
        )
        info = [f for f in findings if f.severity == Severity.INFO]
        assert len(info) >= 1  # At least D or F recommended


# ============================================================================
# Link Vitality Tests (E021)
# ============================================================================


class TestLinkVitality:
    """Tests for E021 link vitality checking via HTTP HEAD requests."""

    @pytest.fixture
    def _make_packet_with_url(self):
        """Factory for packets with a specific Class E URL."""
        from aiv.lib.models import ArtifactLink, IntentSection

        def _factory(url: str) -> VerificationPacket:
            link = ArtifactLink.from_url(url)
            return VerificationPacket(
                version="2.1",
                raw_markdown="# test packet",
                intent=IntentSection(
                    evidence_link=link,
                    verifier_check="Verify the link is reachable and returns 200",
                    requirements_verified=["Link resolves"],
                ),
                claims=[
                    Claim(
                        section_number=1,
                        description="Test claim with sufficient length for link validation",
                        evidence_class=EvidenceClass.REFERENTIAL,
                        artifact="src/feature.py",
                        reproduction="Inspect CI artifacts.",
                    )
                ],
            )

        return _factory

    def test_audit_links_off_skips_network(self, _make_packet_with_url):
        """When audit_links=False (default), no HTTP checks run."""
        validator = LinkValidator(audit_links=False)
        packet = _make_packet_with_url("https://github.com/owner/repo/blob/abc123def456/docs/spec.md")
        findings = validator.validate(packet)
        e021 = [f for f in findings if f.rule_id == "E021"]
        assert len(e021) == 0

    def test_audit_links_404_blocks(self, _make_packet_with_url, monkeypatch):
        """E021 BLOCK when HTTP HEAD returns 404."""
        from urllib.error import HTTPError

        def _mock_urlopen(req, **kwargs):
            raise HTTPError(req.full_url, 404, "Not Found", {}, None)

        monkeypatch.setattr("aiv.lib.validators.links.urlopen", _mock_urlopen)

        validator = LinkValidator(audit_links=True)
        packet = _make_packet_with_url("https://github.com/owner/repo/blob/abc123def456/docs/spec.md")
        findings = validator.validate(packet)
        e021 = [f for f in findings if f.rule_id == "E021"]
        assert len(e021) == 1
        assert e021[0].severity == Severity.BLOCK
        assert "404" in e021[0].message

    def test_audit_links_200_passes(self, _make_packet_with_url, monkeypatch):
        """No E021 when HTTP HEAD returns 200."""

        class FakeResp:
            status = 200
            reason = "OK"

            def __enter__(self):
                return self

            def __exit__(self, *a):
                pass

        monkeypatch.setattr("aiv.lib.validators.links.urlopen", lambda req, **kw: FakeResp())

        validator = LinkValidator(audit_links=True)
        packet = _make_packet_with_url("https://github.com/owner/repo/blob/abc123def456/docs/spec.md")
        findings = validator.validate(packet)
        e021 = [f for f in findings if f.rule_id == "E021"]
        assert len(e021) == 0

    def test_audit_links_network_error_warns(self, _make_packet_with_url, monkeypatch):
        """E021 WARN when network is unreachable."""
        from urllib.error import URLError

        monkeypatch.setattr(
            "aiv.lib.validators.links.urlopen",
            lambda req, **kw: (_ for _ in ()).throw(URLError("Name resolution failed")),
        )

        validator = LinkValidator(audit_links=True)
        packet = _make_packet_with_url("https://github.com/owner/repo/blob/abc123def456/docs/spec.md")
        findings = validator.validate(packet)
        e021 = [f for f in findings if f.rule_id == "E021"]
        assert len(e021) == 1
        assert e021[0].severity == Severity.WARN
        assert "could not be reached" in e021[0].message

    def test_audit_links_403_blocks(self, _make_packet_with_url, monkeypatch):
        """E021 BLOCK when HTTP HEAD returns 403 (permission denied)."""
        from urllib.error import HTTPError

        def _mock_urlopen(req, **kwargs):
            raise HTTPError(req.full_url, 403, "Forbidden", {}, None)

        monkeypatch.setattr("aiv.lib.validators.links.urlopen", _mock_urlopen)

        validator = LinkValidator(audit_links=True)
        packet = _make_packet_with_url("https://github.com/owner/repo/blob/abc123def456/docs/spec.md")
        findings = validator.validate(packet)
        e021 = [f for f in findings if f.rule_id == "E021"]
        assert len(e021) == 1
        assert "403" in e021[0].message

    def test_audit_links_deduplicates_urls(self, monkeypatch):
        """Same URL appearing in multiple places is only checked once."""
        from aiv.lib.models import ArtifactLink, IntentSection

        call_count = 0

        class FakeResp:
            status = 200
            reason = "OK"

            def __enter__(self):
                return self

            def __exit__(self, *a):
                pass

        def _counting_urlopen(req, **kw):
            nonlocal call_count
            call_count += 1
            return FakeResp()

        monkeypatch.setattr("aiv.lib.validators.links.urlopen", _counting_urlopen)

        url = "https://github.com/owner/repo/blob/abc123def456/docs/spec.md"
        link = ArtifactLink.from_url(url)
        packet = VerificationPacket(
            version="2.1",
            raw_markdown="# test packet",
            intent=IntentSection(
                evidence_link=link,
                verifier_check="Verify the link is reachable",
                requirements_verified=["Link resolves"],
            ),
            claims=[
                Claim(
                    section_number=1,
                    description="Test claim referencing the same URL as intent",
                    evidence_class=EvidenceClass.REFERENTIAL,
                    artifact=link,
                    reproduction="Inspect CI artifacts.",
                ),
            ],
        )

        validator = LinkValidator(audit_links=True)
        validator.validate(packet)
        assert call_count == 1, f"URL should be checked exactly once, was checked {call_count} times"


# ============================================================================
# Parser: Unlinked Evidence Consumed One-Per-Claim (Bug Fix CRITICAL-1)
# ============================================================================


class TestUnlinkedEvidenceConsumption:
    """
    The parser must consume unlinked evidence one-per-claim rather than
    applying the same artifact to all unenriched claims.
    """

    _PACKET_MULTI_CLAIM_SINGLE_UNLINKED = """\
# AIV Verification Packet (v2.1)

## Classification (required)
```yaml
classification:
  risk_tier: R1
```

## Claim(s)
1. Input validation correctly rejects malformed payloads
2. Output serialization produces well-formed JSON
3. Error handler returns appropriate HTTP status codes

## Evidence

### Class E (Intent Alignment)
**Link:** https://github.com/org/repo/issues/42
**Requirements Verified:** Spec §3.1 — all three claims must be independently evidenced.

### Class B (Referential)
Modified file: src/handler.py (no explicit Claim N reference)

## Verification Methodology
N/A — automated via CI run #9999.

## Summary
Three claims, one unlinked evidence section.
"""

    def test_unlinked_evidence_not_repeated_across_all_claims(self):
        """
        When a single unlinked evidence item exists and there are multiple
        claims, only the FIRST unenriched claim should receive the artifact.
        Subsequent claims must fall back to their default artifact, not
        silently reuse the same artifact.
        """
        from aiv.lib.parser import PacketParser

        parser = PacketParser()
        packet = parser.parse(self._PACKET_MULTI_CLAIM_SINGLE_UNLINKED)
        assert packet is not None

        # After consuming the unlinked item for claim 1, claims 2 and 3 should
        # NOT have the same artifact as claim 1.
        artifacts = [str(c.artifact) for c in packet.claims]
        # The first claim gets the unlinked evidence
        assert "src/handler.py" in artifacts[0] or "handler" in artifacts[0]
        # Claims 2 and 3 should NOT have consumed the same artifact
        # (they fall back to the default "See Evidence section" placeholder)
        assert artifacts[1] != artifacts[0] or artifacts[2] != artifacts[0], (
            "Unlinked evidence was incorrectly applied to multiple claims"
        )

    def test_single_claim_single_unlinked_still_works(self):
        """One unlinked evidence + one claim = correct assignment (regression guard)."""
        packet_text = """\
# AIV Verification Packet (v2.1)

## Classification (required)
```yaml
classification:
  risk_tier: R0
```

## Claim(s)
1. Documentation update is self-consistent and accurate

## Evidence

### Class E (Intent Alignment)
**Link:** https://github.com/org/repo/issues/10
**Requirements Verified:** Docs review spec.

### Class B (Referential)
Modified docs/README.md — no claim ref needed for single claim

## Verification Methodology
N/A

## Summary
One claim, one unlinked evidence.
"""
        from aiv.lib.parser import PacketParser

        parser = PacketParser()
        packet = parser.parse(packet_text)
        assert packet is not None
        assert len(packet.claims) == 1
        # The single claim should receive the unlinked evidence
        assert "README" in str(packet.claims[0].artifact) or "docs" in str(packet.claims[0].artifact).lower()


# ============================================================================
# Parser: **Justification:** Extraction from Class F (Bug Fix CRITICAL-2a)
# ============================================================================


class TestJustificationExtraction:
    """
    The parser must extract **Justification:** text from Class F evidence
    sections and store it in claim.justification so the anti-cheat stage
    can verify it.
    """

    _PACKET_WITH_JUSTIFICATION = """\
# AIV Verification Packet (v2.1)

## Classification (required)
```yaml
classification:
  risk_tier: R1
```

## Claim(s)
1. Stale assertion in test_auth.py removed after JWT expiry logic refactor

## Evidence

### Class E (Intent Alignment)
**Link:** https://github.com/org/repo/issues/55
**Requirements Verified:** JWT expiry refactor spec §4.2.

### Class B (Referential)
**Claim 1:** https://github.com/org/repo/blob/abc1234def5678/src/auth.py#L42-L58

### Class F (Provenance)
**Claim 1:** https://github.com/org/repo/issues/55
**Justification:** The assertion at test_auth.py:42 was stale — it checked for
the old 200 status on expired tokens. Post-refactor the correct response is 401.
The assertion was updated to match the new behaviour, not removed to hide failures.

## Verification Methodology
N/A — all evidence from CI run #12345.

## Summary
JWT expiry assertion update with full provenance.
"""

    def test_justification_field_populated_from_class_f(self):
        """Parser extracts **Justification:** text into claim.justification."""
        from aiv.lib.parser import PacketParser

        parser = PacketParser()
        packet = parser.parse(self._PACKET_WITH_JUSTIFICATION)
        assert packet is not None

        class_f_claims = [c for c in packet.claims if c.evidence_class.value == "F"]
        assert class_f_claims, "Expected at least one Class F claim"
        claim = class_f_claims[0]

        assert claim.justification is not None, "justification field should be populated"
        assert "stale" in claim.justification.lower() or "assertion" in claim.justification.lower(), (
            f"Justification text does not match expected content: {claim.justification!r}"
        )
        assert len(claim.justification) > 20

    def test_class_f_without_justification_marker_leaves_field_none(self):
        """Class F claims without **Justification:** leave justification=None."""
        packet_text = """\
# AIV Verification Packet (v2.1)

## Classification (required)
```yaml
classification:
  risk_tier: R1
```

## Claim(s)
1. Bug source traced to faulty input sanitizer

## Evidence

### Class E (Intent Alignment)
**Link:** https://github.com/org/repo/issues/60
**Requirements Verified:** Input sanitizer bug spec.

### Class B (Referential)
**Claim 1:** https://github.com/org/repo/blob/deadbeef1234567/src/sanitizer.py#L10-L20

### Class F (Provenance)
**Claim 1:** https://github.com/org/repo/issues/60

## Verification Methodology
N/A

## Summary
Provenance traced, no justification marker.
"""
        from aiv.lib.parser import PacketParser

        parser = PacketParser()
        packet = parser.parse(packet_text)
        assert packet is not None

        class_f_claims = [c for c in packet.claims if c.evidence_class.value == "F"]
        assert class_f_claims
        # No **Justification:** marker → field stays None
        assert class_f_claims[0].justification is None


# ============================================================================
# Anti-Cheat: check_justification() Fixed (Bug Fix CRITICAL-2b)
# ============================================================================


class TestAntiCheatJustificationCheck:
    """
    check_justification() was broken: claim.justification was always None
    because the parser never populated it. After the fix:
    - A Class F claim with a populated justification field satisfies findings.
    - A Class F claim with no justification but a substantive description also
      satisfies findings (backward compat fallback).
    - A packet with no Class F claims at all fails the check.
    """

    def _make_finding(self) -> AntiCheatFinding:
        return AntiCheatFinding(
            finding_type="deleted_assertion",
            file_path="tests/test_auth.py",
            line_number=42,
            original_content="assert response.status_code == 200",
            requires_justification=True,
        )

    def _make_result(self, finding: AntiCheatFinding) -> AntiCheatResult:
        return AntiCheatResult(findings=[finding], files_analyzed=1, test_files_modified=1)

    def _make_class_f_claim(self, justification: str | None, description: str) -> Claim:
        return Claim(
            section_number=1,
            description=description,
            evidence_class=EvidenceClass.PROVENANCE,
            artifact="https://github.com/org/repo/issues/55",
            reproduction="N/A",
            justification=justification,
        )

    def test_populated_justification_field_satisfies_finding(self):
        """When claim.justification is set (> 20 chars), the finding is justified."""
        from aiv.lib.validators.anti_cheat import AntiCheatScanner

        scanner = AntiCheatScanner()
        finding = self._make_finding()
        result = self._make_result(finding)
        claim = self._make_class_f_claim(
            justification="The assertion was stale after the JWT expiry refactor; updated to check 401.",
            description="Provenance: bug traced to faulty token validation logic.",
        )
        unjustified = scanner.check_justification(result, [claim])
        assert unjustified == [], (
            f"Finding should be justified by claim.justification, got: {unjustified}"
        )

    def test_description_fallback_when_justification_is_none(self):
        """When justification is None, a substantive description satisfies the finding."""
        from aiv.lib.validators.anti_cheat import AntiCheatScanner

        scanner = AntiCheatScanner()
        finding = self._make_finding()
        result = self._make_result(finding)
        claim = self._make_class_f_claim(
            justification=None,  # No **Justification:** marker in packet
            description="Stale assertion removed: the 200 status was incorrect post-refactor.",
        )
        unjustified = scanner.check_justification(result, [claim])
        assert unjustified == [], (
            "Finding should be satisfied by description fallback when justification is None"
        )

    def test_no_class_f_claim_is_unjustified(self):
        """A packet with no Class F claims at all leaves the finding unjustified."""
        from aiv.lib.validators.anti_cheat import AntiCheatScanner

        scanner = AntiCheatScanner()
        finding = self._make_finding()
        result = self._make_result(finding)
        class_b_claim = Claim(
            section_number=1,
            description="Referential evidence for the code change in src/auth.py",
            evidence_class=EvidenceClass.REFERENTIAL,
            artifact="https://github.com/org/repo/blob/abc123def456/src/auth.py#L10",
            reproduction="N/A",
        )
        unjustified = scanner.check_justification(result, [class_b_claim])
        assert finding in unjustified

    def test_short_justification_is_insufficient(self):
        """A justification shorter than 20 chars does not satisfy the finding."""
        from aiv.lib.validators.anti_cheat import AntiCheatScanner

        scanner = AntiCheatScanner()
        finding = self._make_finding()
        result = self._make_result(finding)
        claim = self._make_class_f_claim(
            justification="Too short",  # < 20 chars
            description="Provenance for this code change traced to issue tracker.",
        )
        unjustified = scanner.check_justification(result, [claim])
        assert finding in unjustified

    def test_finding_without_justification_requirement_is_ignored(self):
        """Findings with requires_justification=False are not returned as unjustified."""
        from aiv.lib.validators.anti_cheat import AntiCheatScanner

        scanner = AntiCheatScanner()
        finding = AntiCheatFinding(
            finding_type="mock_bypass",
            file_path="tests/test_foo.py",
            line_number=10,
            requires_justification=False,
        )
        result = AntiCheatResult(findings=[finding], files_analyzed=1, test_files_modified=0)
        unjustified = scanner.check_justification(result, [])
        assert unjustified == []


# ============================================================================
# Pipeline: Anti-Cheat End-to-End with Diff (High Gap)
# ============================================================================


class TestPipelineAntiCheatWithDiff:
    """
    Verify the pipeline's Stage 7/8 (anti-cheat + cross-reference) when a diff
    is provided. Before the fix, Stage 8 always failed because justification
    was never populated. After the fix, a packet with a Class F claim and a
    **Justification:** marker in the markdown should pass.
    """

    _BASE_PACKET = """\
# AIV Verification Packet (v2.1)

## Classification (required)
```yaml
classification:
  risk_tier: R1
```

## Claim(s)
1. Stale assertion removed from test_auth.py after JWT refactor

## Evidence

### Class E (Intent Alignment)
**Link:** https://github.com/org/repo/issues/55
**Requirements Verified:** JWT expiry spec §4.2 — expired tokens must return 401.

### Class B (Referential)
**Claim 1:** https://github.com/org/repo/blob/abc1234def5678/src/auth.py#L42-L58

### Class F (Provenance)
**Claim 1:** https://github.com/org/repo/issues/55
**Justification:** The deleted assertion at test_auth.py:42 checked for HTTP 200
on expired tokens. Post-refactor the correct response is 401. The assertion
was updated to match the new behaviour, not to hide test failures.

## Verification Methodology
N/A — evidence from CI run https://github.com/org/repo/actions/runs/99999

## Summary
JWT expiry assertion corrected with full Class F provenance and justification.
"""

    _DIFF_WITH_DELETED_ASSERTION = """\
diff --git a/tests/test_auth.py b/tests/test_auth.py
index aaaaaaa..bbbbbbb 100644
--- a/tests/test_auth.py
+++ b/tests/test_auth.py
@@ -40,7 +40,7 @@ def test_expired_token():
     response = client.get("/api/data", headers={"Authorization": f"Bearer {token}"})
-    assert response.status_code == 200
+    assert response.status_code == 401
"""

    def test_packet_with_class_f_justification_passes_anticheat(self):
        """
        A packet with **Justification:** in its Class F section must pass
        the anti-cheat cross-reference stage when a diff with a deleted
        assertion is provided.
        """
        pipeline = ValidationPipeline(AIVConfig(strict_mode=False))
        result = pipeline.validate(self._BASE_PACKET, diff=self._DIFF_WITH_DELETED_ASSERTION)

        e011_errors = [e for e in result.errors if e.rule_id == "E011"]
        assert e011_errors == [], (
            f"E011 should not fire when Class F justification is present. Got: {e011_errors}"
        )

    def test_packet_without_class_f_fails_anticheat(self):
        """
        A packet with no Class F claim must fail E011 when the diff has a
        deleted assertion.
        """
        packet_no_f = """\
# AIV Verification Packet (v2.1)

## Classification (required)
```yaml
classification:
  risk_tier: R1
```

## Claim(s)
1. Test suite updated to reflect new API contract

## Evidence

### Class E (Intent Alignment)
**Link:** https://github.com/org/repo/issues/88
**Requirements Verified:** API contract change spec.

### Class B (Referential)
**Claim 1:** https://github.com/org/repo/blob/abc1234def5678/src/api.py#L10-L30

## Verification Methodology
N/A

## Summary
API update, no provenance claim.
"""
        pipeline = ValidationPipeline(AIVConfig(strict_mode=False))
        result = pipeline.validate(packet_no_f, diff=self._DIFF_WITH_DELETED_ASSERTION)

        e011_errors = [e for e in result.errors if e.rule_id == "E011"]
        assert e011_errors, "E011 should fire when no Class F justification is present"
