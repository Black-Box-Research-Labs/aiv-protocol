"""
tests/integration/test_full_workflow.py

End-to-end integration tests using the ACTUAL packet template format.
"""

from pathlib import Path

import pytest

from aiv.lib.config import AIVConfig
from aiv.lib.models import Severity, ValidationStatus
from aiv.lib.validators.pipeline import ValidationPipeline


class TestFullValidationWorkflow:
    """Integration tests for complete validation pipeline."""

    @pytest.fixture
    def strict_pipeline(self):
        return ValidationPipeline(AIVConfig(strict_mode=True))

    @pytest.fixture
    def lenient_pipeline(self):
        return ValidationPipeline(AIVConfig(strict_mode=False))

    def test_valid_packet_passes(self, lenient_pipeline, valid_full_packet):
        """A complete, valid packet should pass all validations."""
        result = lenient_pipeline.validate(valid_full_packet)

        assert result.status == ValidationStatus.PASS
        assert len(result.blocking_errors) == 0
        assert result.packet is not None
        assert len(result.packet.claims) == 3

    def test_missing_header_fails(self, strict_pipeline, invalid_missing_header):
        """Missing header should fail with E001."""
        result = strict_pipeline.validate(invalid_missing_header)

        assert result.status == ValidationStatus.FAIL
        assert any(e.rule_id == "E001" for e in result.errors)

    def test_mutable_link_blocks(self, strict_pipeline, invalid_mutable_link):
        """Mutable Class E link should produce E004 blocking error."""
        result = strict_pipeline.validate(invalid_mutable_link)

        assert result.status == ValidationStatus.FAIL
        e004_findings = [e for e in result.errors if e.rule_id == "E004"]
        assert len(e004_findings) > 0

    def test_strict_mode_fails_on_warnings(self, strict_pipeline, invalid_mutable_link):
        """Strict mode should treat warnings as failures."""
        result = strict_pipeline.validate(invalid_mutable_link)
        assert result.status == ValidationStatus.FAIL

    def test_deleted_assertion_without_justification_fails(
        self, lenient_pipeline, valid_minimal_packet, diff_with_deleted_assertion
    ):
        """Deleted assertion without Class F justification should fail."""
        result = lenient_pipeline.validate(valid_minimal_packet, diff=diff_with_deleted_assertion)

        assert result.status == ValidationStatus.FAIL
        assert any(e.rule_id == "E011" for e in result.errors)

    def test_clean_diff_passes(self, lenient_pipeline, valid_full_packet, diff_clean):
        """Clean diff with proper packet should pass."""
        result = lenient_pipeline.validate(valid_full_packet, diff=diff_clean)

        assert result.status == ValidationStatus.PASS

    def test_skip_decorator_detected(self, lenient_pipeline, valid_minimal_packet, diff_with_skip_decorator):
        """Added skip decorator should be detected."""
        result = lenient_pipeline.validate(valid_minimal_packet, diff=diff_with_skip_decorator)

        assert result.status == ValidationStatus.FAIL
        assert any(e.rule_id == "E011" for e in result.errors)

    def test_non_strict_mode_allows_warnings(self, lenient_pipeline, valid_full_packet):
        """Non-strict mode should pass when only warnings exist."""
        result = lenient_pipeline.validate(valid_full_packet)

        blocking = [e for e in result.errors if e.severity == Severity.BLOCK]
        assert len(blocking) == 0
        assert result.status == ValidationStatus.PASS


class TestRealPacketSmoke:
    """Smoke tests against actual packets from .github/aiv-packets/."""

    PACKETS_DIR = Path(__file__).resolve().parents[2] / ".github" / "aiv-packets"

    @pytest.fixture
    def lenient_pipeline(self):
        return ValidationPipeline(AIVConfig(strict_mode=False))

    def _get_real_packets(self):
        """Find all real verification packets in the repo."""
        if not self.PACKETS_DIR.exists():
            pytest.skip("aiv-packets directory not found")
        packets = list(self.PACKETS_DIR.glob("VERIFICATION_PACKET_*.md"))
        # Exclude the template — it's not a real packet
        return [p for p in packets if "TEMPLATE" not in p.name]

    def test_real_packets_exist(self):
        """At least one real packet should exist in the repo."""
        packets = self._get_real_packets()
        assert len(packets) > 0, "No real verification packets found"

    def test_real_packets_parse_without_crash(self, lenient_pipeline):
        """Every real packet should parse without crashing the pipeline."""
        packets = self._get_real_packets()
        for packet_path in packets:
            body = packet_path.read_text(encoding="utf-8")
            # Should not raise — may fail validation, but must not crash
            result = lenient_pipeline.validate(body)
            assert result is not None, f"Pipeline returned None for {packet_path.name}"
            assert result.packet is not None, (
                f"Failed to parse {packet_path.name}: {[e.message for e in result.errors]}"
            )

    def test_implementation_packet_passes(self, lenient_pipeline):
        """The consolidated implementation packet should pass in lenient mode."""
        impl_packet = self.PACKETS_DIR / "VERIFICATION_PACKET_AIV_IMPLEMENTATION.md"
        if not impl_packet.exists():
            pytest.skip("Implementation packet not found")

        body = impl_packet.read_text(encoding="utf-8")
        result = lenient_pipeline.validate(body)

        assert result.packet is not None
        assert result.packet.claims, "No claims parsed"
        assert len(result.blocking_errors) == 0, f"Blocking errors: {[e.message for e in result.blocking_errors]}"
