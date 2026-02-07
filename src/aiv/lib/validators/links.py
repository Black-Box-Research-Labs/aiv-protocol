"""
aiv/lib/validators/links.py

URL validation and immutability checking (Addendum 2.2).
"""

from __future__ import annotations

from ..config import MutableBranchConfig
from ..models import (
    ArtifactLink,
    ValidationFinding,
    VerificationPacket,
)
from .base import BaseValidator


class LinkValidator(BaseValidator):
    """
    Validates artifact links for accessibility and immutability.
    """

    def __init__(self, config: MutableBranchConfig | None = None):
        self.config = config or MutableBranchConfig()

    def validate(self, packet: VerificationPacket) -> list[ValidationFinding]:
        """Validate all links in a packet."""
        return self.validate_packet_links(packet)

    def validate_packet_links(self, packet: VerificationPacket) -> list[ValidationFinding]:
        """
        Validate all links in a packet.

        Checks:
        - Class E links must be immutable (SHA-pinned)
        - All GitHub blob/tree links should be immutable
        - Links should be accessible (optional, requires network)
        """
        errors: list[ValidationFinding] = []

        # Validate intent link (Class E) - MUST be immutable if it's a URL
        intent_link = packet.intent.evidence_link
        if isinstance(intent_link, ArtifactLink):
            if not intent_link.is_immutable:
                errors.append(
                    self._make_finding(
                        rule_id="E004",
                        severity="block",
                        message=(f"Class E Evidence must be immutable. Reason: {intent_link.immutability_reason}"),
                        location="Section 0 (Intent Alignment)",
                        suggestion=(
                            "Link to a specific commit SHA, not a branch. "
                            "Example: /blob/a1b2c3d/docs/spec.md instead of /blob/main/..."
                        ),
                    )
                )
        elif isinstance(intent_link, str):
            errors.append(
                self._make_finding(
                    rule_id="E004",
                    severity="info",
                    message=(
                        "Class E Evidence is a plain text reference, not a URL. "
                        "Consider using a SHA-pinned permalink for immutability."
                    ),
                    location="Section 0 (Intent Alignment)",
                )
            )

        # Validate claim artifacts using configured mutable branch set
        for claim in packet.claims:
            if isinstance(claim.artifact, ArtifactLink):
                link = claim.artifact

                # Re-check blob/tree links with configured mutable branches
                if link.link_type == "github_blob":
                    recheck = ArtifactLink.from_url(
                        str(link.url),
                        mutable_branches=self.config.mutable_branches,
                        min_sha_length=self.config.min_sha_length,
                    )
                    if not recheck.is_immutable:
                        errors.append(
                            self._make_finding(
                                rule_id="E009",
                                severity="block",
                                message=(f"Evidence artifact link is mutable. Reason: {recheck.immutability_reason}"),
                                location=f"Section {claim.section_number}",
                                suggestion=(
                                    "Use a SHA-pinned link. Copy the link from the 'Copy permalink' option in GitHub."
                                ),
                            )
                        )

        return errors
