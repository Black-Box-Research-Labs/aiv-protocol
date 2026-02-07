"""
tests/unit/test_coverage.py

Additional test coverage for audit report recommendations:
- P1-a: aiv generate command (Rec #20)
- P1-b: Anti-cheat deleted file detection (Rec #21)
- P1-c: Parser edge cases (malformed markdown)
- P1-d: Strict mode behavior
- P1-e: Multi-claim evidence enrichment
- P1-f: AIVConfig.from_file() YAML loading
"""

from pathlib import Path

import pytest

from aiv.cli.main import _build_evidence_sections
from aiv.lib.config import AIVConfig
from aiv.lib.errors import ConfigurationError, PacketParseError
from aiv.lib.models import (
    EvidenceClass,
    Severity,
)
from aiv.lib.parser import PacketParser
from aiv.lib.validators.anti_cheat import AntiCheatScanner
from aiv.lib.validators.pipeline import ValidationPipeline

# ============================================================================
# P1-a: Generate Command Tests (Rec #20)
# ============================================================================


class TestBuildEvidenceSections:
    """Tests for _build_evidence_sections helper used by `aiv generate`."""

    def test_r0_has_class_b_and_a(self):
        result = _build_evidence_sections("R0", "  - `src/file.py`")
        assert "### Class B" in result
        assert "### Class A" in result
        assert "### Class E" in result  # structurally required by parser
        assert "### Class C" not in result

    def test_r1_adds_class_e(self):
        result = _build_evidence_sections("R1", "  - `src/file.py`")
        assert "### Class E" in result
        assert "### Class B" in result
        assert "### Class A" in result
        assert "### Class C" not in result

    def test_r2_adds_class_c_and_f(self):
        result = _build_evidence_sections("R2", "  - `src/file.py`")
        assert "### Class E" in result
        assert "### Class C" in result
        assert "### Class F (Provenance Evidence)" in result
        assert "### Class D" not in result

    def test_r3_has_all_six_classes(self):
        result = _build_evidence_sections("R3", "  - `src/file.py`")
        assert "### Class E" in result
        assert "### Class B" in result
        assert "### Class A" in result
        assert "### Class C" in result
        assert "### Class D" in result
        assert "### Class F" in result

    def test_scope_lines_embedded(self):
        result = _build_evidence_sections("R0", "  - `src/auth.py`\n  - `src/login.py`")
        assert "`src/auth.py`" in result
        assert "`src/login.py`" in result


# ============================================================================
# P1-b: Anti-Cheat Deleted File Detection (Rec #21)
# ============================================================================


class TestAntiCheatDeletedFiles:
    """Tests for deleted test file detection in AntiCheatScanner."""

    @pytest.fixture
    def scanner(self):
        return AntiCheatScanner()

    def test_deleted_test_file_detected(self, scanner):
        """Deleting a test file should produce an anti-cheat finding."""
        diff = (
            "diff --git a/tests/test_auth.py b/tests/test_auth.py\n"
            "old mode 100644\n"
            "deleted file mode 100644\n"
            "index abc123..0000000\n"
            "--- a/tests/test_auth.py\n"
            "+++ /dev/null\n"
            "@@ -1,4 +0,0 @@\n"
            "-import pytest\n"
            "-\n"
            "-def test_login():\n"
            "-    assert True\n"
        )
        result = scanner.scan_diff(diff)
        removed = [f for f in result.findings if f.finding_type == "removed_test_file"]
        assert len(removed) >= 1
        assert "test_auth.py" in removed[0].file_path

    def test_deleted_non_test_file_ignored(self, scanner):
        """Deleting a non-test file should NOT produce removed_test_file finding."""
        diff = """\
diff --git a/src/utils.py b/src/utils.py
deleted file mode 100644
index abc123..0000000
--- a/src/utils.py
+++ /dev/null
@@ -1,5 +0,0 @@
-def helper():
-    pass
"""
        result = scanner.scan_diff(diff)
        removed = [f for f in result.findings if f.finding_type == "removed_test_file"]
        assert len(removed) == 0

    def test_multi_hunk_line_numbers(self, scanner):
        """Line numbers should be correct across multiple hunks."""
        diff = """\
diff --git a/tests/test_example.py b/tests/test_example.py
index abc123..def456 100644
--- a/tests/test_example.py
+++ b/tests/test_example.py
@@ -5,6 +5,7 @@ import pytest
 
 def test_first():
     assert True
+    assert 1 == 1
 
 def test_second():
     assert True
@@ -20,7 +21,6 @@ def test_third():
     result = compute()
     assert result is not None
-    assert result > 0
     assert result != -1
"""
        result = scanner.scan_diff(diff)
        deleted = [f for f in result.findings if f.finding_type == "deleted_assertion"]
        assert len(deleted) >= 1


# ============================================================================
# P1-c: Parser Edge Case Tests (malformed markdown)
# ============================================================================


class TestParserEdgeCases:
    """Tests for PacketParser with malformed/edge-case markdown."""

    @pytest.fixture
    def parser(self):
        return PacketParser()

    def test_missing_header_raises(self, parser):
        """Packet without header should raise PacketParseError."""
        with pytest.raises(PacketParseError, match="Missing packet header"):
            parser.parse("## Just some random markdown\n\nSome content.")

    def test_missing_intent_raises(self, parser):
        """Packet with header but no Class E section should raise."""
        with pytest.raises(PacketParseError, match="Missing Class E"):
            parser.parse("# AIV Verification Packet (v2.1)\n\n## Claim(s)\n\n1. Some claim with enough text here.\n")

    def test_missing_claims_raises(self, parser):
        """Packet with header + intent but no claims should raise."""
        with pytest.raises(PacketParseError, match="No valid claims"):
            parser.parse(
                "# AIV Verification Packet (v2.1)\n\n"
                "## Evidence\n\n"
                "### Class E (Intent Alignment)\n\n"
                "- **Link:** [Spec](https://github.com/o/r/blob/abc1234/docs/spec.md)\n"
                "- **Requirements Verified:**\n  1. Requirement met\n"
            )

    def test_empty_string_raises(self, parser):
        """Empty string should raise."""
        with pytest.raises(PacketParseError):
            parser.parse("")

    def test_short_claim_skipped_with_warning(self, parser):
        """Claims with very short descriptions should produce a warning."""
        packet_text = """\
# AIV Verification Packet (v2.1)

## Claim(s)

1. Too short
2. This claim has a sufficient description length for validation checks to pass.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [Spec](https://github.com/o/r/blob/abc1234/docs/spec.md)
- **Requirements Verified:**
  1. Done

---

## Summary

Test.
"""
        result = parser.parse(packet_text)
        assert result is not None
        # Only the long claim should make it through
        assert len(result.claims) == 1
        assert result.claims[0].section_number == 2
        # Parser should have a warning about short claim
        warnings = [e for e in parser.errors if e.severity == Severity.WARN]
        assert any("too brief" in w.message.lower() for w in warnings)

    def test_duplicate_section_headers(self, parser):
        """Parser should handle duplicate section headers gracefully."""
        packet_text = """\
# AIV Verification Packet (v2.1)

## Claim(s)

1. First claim with enough description text for validation checks here.

## Claim(s)

1. Second duplicate claim with enough description text for validation.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [Spec](https://github.com/o/r/blob/abc1234/docs/spec.md)
- **Requirements Verified:**
  1. Done

---

## Summary

Test.
"""
        # Should not crash — parser finds first matching section
        result = parser.parse(packet_text)
        assert result is not None
        assert len(result.claims) >= 1


# ============================================================================
# P1-d: Strict Mode Behavior Tests
# ============================================================================


class TestStrictModeBehavior:
    """Tests for strict_mode flag in pipeline validation."""

    def test_strict_mode_creates_valid_config(self):
        """strict_mode should be settable at construction time."""
        cfg = AIVConfig(strict_mode=True)
        assert cfg.strict_mode is True

    def test_strict_mode_default_is_true(self):
        """Default strict_mode should be True."""
        cfg = AIVConfig()
        assert cfg.strict_mode is True

    def test_model_copy_preserves_strict(self):
        """model_copy should correctly override strict_mode."""
        cfg = AIVConfig(strict_mode=False)
        strict_cfg = cfg.model_copy(update={"strict_mode": True})
        assert strict_cfg.strict_mode is True
        assert cfg.strict_mode is False  # Original unchanged

    def test_pipeline_accepts_strict_config(self):
        """Pipeline should accept strict configuration without error."""
        cfg = AIVConfig(strict_mode=True)
        pipeline = ValidationPipeline(cfg)
        assert pipeline.config.strict_mode is True


# ============================================================================
# P1-e: Multi-Claim Evidence Enrichment Tests
# ============================================================================


class TestMultiClaimEvidenceEnrichment:
    """Tests for evidence enrichment across multiple claims."""

    @pytest.fixture
    def parser(self):
        return PacketParser()

    def test_multiple_claims_get_default_evidence(self, parser):
        """Multiple claims should each get default evidence class."""
        packet_text = """\
# AIV Verification Packet (v2.1)

## Claim(s)

1. First claim: Implemented new authentication flow for SSO users.
2. Second claim: Added regression tests for the SSO edge case.
3. Third claim: No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [Spec](https://github.com/o/r/blob/abc1234/docs/spec.md)
- **Requirements Verified:**
  1. SSO flow works correctly

### Class B (Referential Evidence)

**Scope Inventory (required)**

- Modified:
  - `src/auth.py`

---

## Summary

Multi-claim test.
"""
        packet = parser.parse(packet_text)
        assert len(packet.claims) == 3
        # All claims should have evidence class assigned
        for claim in packet.claims:
            assert claim.evidence_class is not None

    def test_evidence_classes_collected_from_sections(self, parser):
        """Evidence classes should be collected from all ### Class X sections."""
        packet_text = """\
# AIV Verification Packet (v2.1)

## Claim(s)

1. Test claim with sufficient description length for validation checks.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [Spec](https://github.com/o/r/blob/abc1234/docs/spec.md)
- **Requirements Verified:**
  1. Done

### Class B (Referential Evidence)

**Scope Inventory (required)**
- Modified: `src/file.py`

### Class A (Execution Evidence)

- CI Run passed

---

## Summary

Test.
"""
        packet = parser.parse(packet_text)
        assert EvidenceClass.INTENT in packet.evidence_classes_present
        assert EvidenceClass.REFERENTIAL in packet.evidence_classes_present
        assert EvidenceClass.EXECUTION in packet.evidence_classes_present


# ============================================================================
# P1-f: AIVConfig.from_file() YAML Loading Tests
# ============================================================================


class TestAIVConfigFromFile:
    """Tests for AIVConfig.from_file() YAML loading."""

    def test_nonexistent_file_returns_default(self):
        """Missing file should return default config."""
        cfg = AIVConfig.from_file(Path("/nonexistent/.aiv.yml"))
        assert cfg.strict_mode is True  # Default is True

    def test_valid_yaml_loads(self, tmp_path):
        """Valid YAML file should load correctly."""
        config_file = tmp_path / ".aiv.yml"
        config_file.write_text("strict_mode: true\n", encoding="utf-8")
        cfg = AIVConfig.from_file(config_file)
        assert cfg.strict_mode is True

    def test_invalid_yaml_raises_configuration_error(self, tmp_path):
        """Invalid YAML should raise ConfigurationError."""
        config_file = tmp_path / ".aiv.yml"
        # Use a truly invalid YAML structure (tab indentation error)
        config_file.write_text(
            "strict_mode: true\n  bad_indent:\n\t- mixed tabs and spaces\n",
            encoding="utf-8",
        )
        with pytest.raises(ConfigurationError):
            AIVConfig.from_file(config_file)

    def test_empty_yaml_returns_default(self, tmp_path):
        """Empty YAML file should return default config."""
        config_file = tmp_path / ".aiv.yml"
        config_file.write_text("", encoding="utf-8")
        cfg = AIVConfig.from_file(config_file)
        assert cfg.strict_mode is True  # Default is True

    def test_invalid_field_raises_configuration_error(self, tmp_path):
        """YAML with invalid field type should raise ConfigurationError."""
        config_file = tmp_path / ".aiv.yml"
        config_file.write_text(
            "strict_mode: not_a_bool_or_valid_value\nmin_sha_length: not_an_int\n",
            encoding="utf-8",
        )
        with pytest.raises(ConfigurationError, match="Invalid configuration"):
            AIVConfig.from_file(config_file)
