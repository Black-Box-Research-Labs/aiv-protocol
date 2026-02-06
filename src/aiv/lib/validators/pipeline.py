"""
aiv/lib/validators/pipeline.py

Complete validation pipeline that orchestrates all validators.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from ..models import (
    ValidationResult,
    ValidationStatus,
    ValidationFinding,
    VerificationPacket,
    AntiCheatResult,
    Severity,
)
from ..parser import PacketParser
from ..config import AIVConfig
from .structure import StructureValidator
from .evidence import EvidenceValidator
from .links import LinkValidator
from .zero_touch import ZeroTouchValidator
from .anti_cheat import AntiCheatScanner


@dataclass
class ValidationContext:
    """Context passed through validation pipeline."""
    body: str
    diff: str | None
    config: AIVConfig
    packet: VerificationPacket | None = None
    anti_cheat_result: AntiCheatResult | None = None


class ValidationPipeline:
    """
    Orchestrates the complete validation process.

    Pipeline stages:
    1. Parse - Convert markdown to structured packet
    2. Structure - Validate packet structure completeness
    3. Links - Validate URL immutability
    4. Evidence - Validate evidence class requirements
    5. Zero-Touch - Validate reproduction instructions
    6. Anti-Cheat - Scan diff for test manipulation
    7. Cross-Reference - Ensure anti-cheat findings are justified
    """

    def __init__(self, config: AIVConfig | None = None):
        self.config = config or AIVConfig()

        # Initialize validators
        self.parser = PacketParser()
        self.structure_validator = StructureValidator()
        self.link_validator = LinkValidator(self.config.mutable_branches)
        self.evidence_validator = EvidenceValidator()
        self.zero_touch_validator = ZeroTouchValidator(self.config.zero_touch)
        self.anti_cheat_scanner = AntiCheatScanner(self.config.anti_cheat)

    def validate(self, body: str, diff: str | None = None) -> ValidationResult:
        """
        Run complete validation pipeline.

        Args:
            body: PR description markdown
            diff: Git diff (optional, for anti-cheat)

        Returns:
            Complete validation result
        """
        ctx = ValidationContext(
            body=body,
            diff=diff,
            config=self.config,
        )

        all_errors: list[ValidationFinding] = []
        all_warnings: list[ValidationFinding] = []
        all_info: list[ValidationFinding] = []

        # Stage 1: Parse
        try:
            ctx.packet = self.parser.parse(body)
            # Collect parser errors by severity
            for finding in self.parser.errors:
                if finding.severity == Severity.BLOCK:
                    all_errors.append(finding)
                elif finding.severity == Severity.WARN:
                    all_warnings.append(finding)
                else:
                    all_info.append(finding)
        except Exception as e:
            all_errors.append(ValidationFinding(
                rule_id="E001",
                severity=Severity.BLOCK,
                message=f"Failed to parse packet: {e}",
            ))
            return ValidationResult(
                status=ValidationStatus.FAIL,
                packet=None,
                errors=all_errors,
            )

        # Stage 2: Structure
        structure_findings = self.structure_validator.validate(ctx.packet)
        self._distribute_findings(structure_findings, all_errors, all_warnings, all_info)

        # Stage 3: Links
        link_findings = self.link_validator.validate(ctx.packet)
        self._distribute_findings(link_findings, all_errors, all_warnings, all_info)

        # Stage 4: Evidence
        evidence_findings = self.evidence_validator.validate(ctx.packet)
        self._distribute_findings(evidence_findings, all_errors, all_warnings, all_info)

        # Stage 5: Zero-Touch
        zero_touch_findings = self.zero_touch_validator.validate(ctx.packet)
        self._distribute_findings(zero_touch_findings, all_errors, all_warnings, all_info)

        # Stage 6: Anti-Cheat (if diff provided)
        if diff:
            ctx.anti_cheat_result = self.anti_cheat_scanner.scan_diff(diff)

            # Stage 7: Cross-Reference
            if ctx.anti_cheat_result.requires_justification:
                unjustified = self.anti_cheat_scanner.check_justification(
                    ctx.anti_cheat_result,
                    ctx.packet.claims
                )

                for finding in unjustified:
                    all_errors.append(ValidationFinding(
                        rule_id="E011",
                        severity=Severity.BLOCK,
                        message=(
                            f"Test modification requires Class F justification: "
                            f"{finding.finding_type} in {finding.file_path}"
                        ),
                        location=f"{finding.file_path}:{finding.line_number or 'N/A'}",
                        suggestion=(
                            "Add a claim with Evidence Class F and include "
                            "**Justification:** explaining why this test change is valid"
                        )
                    ))

        # Determine final status
        if self.config.strict_mode:
            has_failures = len(all_errors) > 0 or len(all_warnings) > 0
        else:
            has_failures = len(all_errors) > 0

        status = ValidationStatus.FAIL if has_failures else ValidationStatus.PASS

        return ValidationResult(
            status=status,
            packet=ctx.packet,
            errors=all_errors,
            warnings=all_warnings,
            info=all_info,
        )

    @staticmethod
    def _distribute_findings(
        findings: list[ValidationFinding],
        errors: list[ValidationFinding],
        warnings: list[ValidationFinding],
        info: list[ValidationFinding],
    ) -> None:
        """Distribute findings into error/warning/info lists by severity."""
        for finding in findings:
            if finding.severity == Severity.BLOCK:
                errors.append(finding)
            elif finding.severity == Severity.WARN:
                warnings.append(finding)
            else:
                info.append(finding)
