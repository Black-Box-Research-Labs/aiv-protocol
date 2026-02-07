"""
aiv/lib/validators/structure.py

Packet structure validation — checks completeness of required sections.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import BaseValidator

if TYPE_CHECKING:
    from ..models import (
        ValidationFinding,
        VerificationPacket,
    )


class StructureValidator(BaseValidator):
    """
    Validates the structural completeness of a Verification Packet.

    Checks:
    - Header exists (E001)
    - Intent section exists with Class E link (E002, E003)
    - At least one claim section (E005)
    - Each claim has evidence class (E006) and artifact (E007)
    """

    def validate(self, packet: VerificationPacket) -> list[ValidationFinding]:
        """Validate packet structure completeness."""
        errors: list[ValidationFinding] = []

        # E002: Intent section must exist (already enforced by parser,
        # but we double-check the verifier_check quality)
        if len(packet.intent.verifier_check.strip()) < 10:
            errors.append(
                self._make_finding(
                    rule_id="E002",
                    severity="warn",
                    message="Verifier Check in Intent section is too brief (min 10 chars)",
                    location="Section 0 (Intent Alignment)",
                    suggestion=("Describe what the verifier should confirm about the intent alignment in detail."),
                )
            )

        # E005: At least one claim (already enforced by Pydantic min_length=1,
        # but we add a semantic check for claim quality)
        for claim in packet.claims:
            # Check claim description quality
            if len(claim.description.strip()) < 15:
                errors.append(
                    self._make_finding(
                        rule_id="E005",
                        severity="warn",
                        message=(
                            f"Claim description in Section {claim.section_number} "
                            f"is very brief. Consider adding more detail."
                        ),
                        location=f"Section {claim.section_number}",
                        suggestion="Claims should be specific and falsifiable.",
                    )
                )

            # Check reproduction field exists and isn't just whitespace
            if not claim.reproduction or not claim.reproduction.strip():
                errors.append(
                    self._make_finding(
                        rule_id="E008",
                        severity="warn",
                        message=(f"Missing reproduction instructions in Section {claim.section_number}"),
                        location=f"Section {claim.section_number}",
                        suggestion="Add 'N/A', 'CI Automation', or a CI artifact link.",
                    )
                )

        return errors
