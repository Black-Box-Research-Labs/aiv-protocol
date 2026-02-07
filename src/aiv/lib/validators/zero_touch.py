"""
aiv/lib/validators/zero_touch.py

Zero-Touch compliance validation (Addendum 2.7).
"""

from __future__ import annotations

import re
from re import Pattern

from ..config import ZeroTouchConfig
from ..models import (
    Claim,
    FrictionScore,
    Severity,
    ValidationFinding,
    VerificationPacket,
)
from .base import BaseValidator


class ZeroTouchValidator(BaseValidator):
    """
    Validates reproduction instructions for Zero-Touch compliance.

    The Zero-Touch mandate requires that verifiers never need to
    execute code locally. All verification must be artifact-based.
    """

    def __init__(self, config: ZeroTouchConfig | None = None):
        self.config = config or ZeroTouchConfig()

        # Compile patterns once
        self.prohibited_patterns: list[Pattern[str]] = [
            re.compile(p, re.IGNORECASE) for p in self.config.prohibited_patterns
        ]
        self.allowed_patterns: list[Pattern[str]] = [re.compile(p, re.IGNORECASE) for p in self.config.allowed_patterns]
        self.step_patterns: list[Pattern[str]] = [re.compile(p, re.IGNORECASE) for p in self.config.step_separators]

    def validate(self, packet: VerificationPacket) -> list[ValidationFinding]:
        """Validate all claims in a packet for zero-touch compliance."""
        return self.validate_packet(packet)

    # Pattern to match fenced code blocks (```...```) which are
    # informational context, not execution instructions.
    _CODE_BLOCK_RE = re.compile(r"```[^\n]*\n.*?```", re.DOTALL)

    # Phrases that signal zero-touch compliance regardless of surrounding content.
    _ZT_COMPLIANCE_PHRASES = [
        "zero-touch mandate",
        "verifier inspects artifacts only",
        "no local code execution",
        "no verification needed",
    ]

    def validate_claim(self, claim: Claim) -> tuple[list[ValidationFinding], FrictionScore]:
        """
        Validate a single claim's reproduction instructions.

        Returns:
            Tuple of (errors, friction_score)
        """
        errors: list[ValidationFinding] = []
        reproduction = claim.reproduction.strip()

        # Check if reproduction matches allowed patterns (early exit)
        for pattern in self.allowed_patterns:
            if pattern.match(reproduction):
                return errors, FrictionScore(
                    score=0,
                    step_count=0,
                    prohibited_patterns_found=[],
                    is_zero_touch_compliant=True,
                    recommendation=None,
                )

        # Check for explicit zero-touch compliance phrases (early exit)
        repro_lower = reproduction.lower()
        if any(phrase in repro_lower for phrase in self._ZT_COMPLIANCE_PHRASES):
            return errors, FrictionScore(
                score=0, step_count=0, prohibited_patterns_found=[], is_zero_touch_compliant=True, recommendation=None
            )

        # Strip fenced code blocks before checking prohibited patterns.
        # Methodology sections include commands as informational context
        # (often labeled "context only"), not as execution instructions.
        repro_stripped = self._CODE_BLOCK_RE.sub("", reproduction).strip()

        # Check for prohibited patterns in non-code-block content only
        prohibited_found: list[str] = []
        for pattern in self.prohibited_patterns:
            if pattern.search(repro_stripped):
                prohibited_found.append(pattern.pattern)

        if prohibited_found:
            errors.append(
                ValidationFinding(
                    rule_id="E008",
                    severity=Severity.BLOCK,
                    message=("Reproduction instructions require local execution. Zero-Touch mandate violated."),
                    location=f"Section {claim.section_number}",
                    suggestion=(
                        "Replace manual steps with a link to CI artifacts. Example: 'See CI artifact: test_output.log'"
                    ),
                )
            )

        # Count steps (using stripped text, excluding code blocks)
        step_count = 1  # Start with 1 (the instruction itself)
        for pattern in self.step_patterns:
            matches = pattern.findall(repro_stripped)
            step_count += len(matches)

        if step_count > self.config.max_steps:
            errors.append(
                ValidationFinding(
                    rule_id="E008",
                    severity=Severity.WARN,
                    message=(
                        f"High-friction reproduction: {step_count} steps detected. "
                        f"Maximum recommended: {self.config.max_steps}"
                    ),
                    location=f"Section {claim.section_number}",
                    suggestion="Consolidate into a single automated script or CI artifact link",
                )
            )

        # Calculate friction score
        friction_score = FrictionScore(
            score=len(prohibited_found) * 10 + max(0, step_count - 1) * 2,
            step_count=step_count,
            prohibited_patterns_found=prohibited_found,
            is_zero_touch_compliant=len(prohibited_found) == 0,
            recommendation=self._generate_recommendation(prohibited_found, step_count),
        )

        return errors, friction_score

    def validate_packet(self, packet: VerificationPacket) -> list[ValidationFinding]:
        """Validate all claims in a packet."""
        all_errors: list[ValidationFinding] = []
        total_friction = 0

        for claim in packet.claims:
            errors, friction = self.validate_claim(claim)
            all_errors.extend(errors)
            total_friction += friction.score

        # Aggregate warning if total friction is high
        if total_friction > 20:
            all_errors.append(
                ValidationFinding(
                    rule_id="E008",
                    severity=Severity.WARN,
                    message=f"Total packet friction score: {total_friction}. Consider simplifying.",
                    location="Packet-wide",
                )
            )

        return all_errors

    def _generate_recommendation(self, prohibited: list[str], step_count: int) -> str | None:
        """Generate actionable recommendation based on findings."""

        if not prohibited and step_count <= 1:
            return None

        recommendations: list[str] = []

        if any("git" in p for p in prohibited):
            recommendations.append("Replace git commands with GitHub file permalinks")

        if any("install" in p for p in prohibited):
            recommendations.append("Dependencies should be handled by CI; link to successful CI run")

        if any("run" in p.lower() or "pytest" in p for p in prohibited):
            recommendations.append("Execution evidence should be a CI artifact link, not a command")

        if step_count > 1:
            recommendations.append(f"Consolidate {step_count} steps into single CI job")

        return "; ".join(recommendations) if recommendations else None
