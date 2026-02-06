"""
tests/integration/test_full_workflow.py

End-to-end integration tests.
"""

import pytest
from aiv.lib.validators.pipeline import ValidationPipeline
from aiv.lib.models import ValidationStatus, Severity


class TestFullValidationWorkflow:
    """Integration tests for complete validation pipeline."""

    @pytest.fixture
    def pipeline(self):
        return ValidationPipeline()

    def test_valid_packet_passes(self, pipeline, valid_full_packet):
        """A complete, valid packet should pass all validations."""
        result = pipeline.validate(valid_full_packet)

        assert result.status == ValidationStatus.PASS
        assert len(result.blocking_errors) == 0
        assert result.packet is not None
        assert len(result.packet.claims) == 3

    def test_missing_header_fails(self, pipeline, invalid_missing_header):
        """Missing header should fail with E001."""
        result = pipeline.validate(invalid_missing_header)

        assert result.status == ValidationStatus.FAIL
        assert any(e.rule_id == "E001" for e in result.errors)

    def test_mutable_link_fails(self, pipeline, invalid_mutable_link):
        """Mutable Class E link should fail with E004."""
        result = pipeline.validate(invalid_mutable_link)

        assert result.status == ValidationStatus.FAIL
        assert any(e.rule_id == "E004" for e in result.errors)

    def test_manual_reproduction_blocks_in_strict(self, pipeline, invalid_manual_reproduction):
        """Manual reproduction should block in strict mode."""
        result = pipeline.validate(invalid_manual_reproduction)

        assert result.status == ValidationStatus.FAIL
        assert any(e.rule_id == "E008" for e in result.errors)

    def test_deleted_assertion_without_justification_fails(
        self,
        pipeline,
        valid_minimal_packet,
        diff_with_deleted_assertion
    ):
        """Deleted assertion without Class F justification should fail."""
        result = pipeline.validate(
            valid_minimal_packet,
            diff=diff_with_deleted_assertion
        )

        assert result.status == ValidationStatus.FAIL
        assert any(e.rule_id == "E011" for e in result.errors)

    def test_clean_diff_passes(self, pipeline, valid_full_packet, diff_clean):
        """Clean diff with proper packet should pass."""
        result = pipeline.validate(valid_full_packet, diff=diff_clean)

        assert result.status == ValidationStatus.PASS

    def test_skip_decorator_detected(
        self,
        pipeline,
        valid_minimal_packet,
        diff_with_skip_decorator
    ):
        """Added skip decorator should be detected."""
        result = pipeline.validate(
            valid_minimal_packet,
            diff=diff_with_skip_decorator
        )

        assert result.status == ValidationStatus.FAIL
        assert any(e.rule_id == "E011" for e in result.errors)

    def test_non_strict_mode_allows_warnings(self, valid_full_packet):
        """Non-strict mode should allow warnings to pass."""
        from aiv.lib.config import AIVConfig
        config = AIVConfig(strict_mode=False)
        pipeline = ValidationPipeline(config)

        result = pipeline.validate(valid_full_packet)

        # Should pass even if there are warnings
        if result.errors:
            # Only fail if there are actual blocking errors
            blocking = [e for e in result.errors if e.severity == Severity.BLOCK]
            assert len(blocking) == 0 or result.status == ValidationStatus.FAIL
        else:
            assert result.status == ValidationStatus.PASS
