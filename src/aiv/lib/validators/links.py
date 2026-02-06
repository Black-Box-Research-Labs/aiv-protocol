"""
aiv/lib/validators/links.py

URL validation and immutability checking (Addendum 2.2).
"""

from __future__ import annotations

import re
from urllib.parse import urlparse

from ..models import (
    ArtifactLink,
    ValidationFinding,
    Severity,
    VerificationPacket,
)
from ..config import MutableBranchConfig
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

    def validate_packet_links(
        self,
        packet: VerificationPacket
    ) -> list[ValidationFinding]:
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
                errors.append(self._make_finding(
                    rule_id="E004",
                    severity="block",
                    message=(
                        f"Class E Evidence must be immutable. "
                        f"Reason: {intent_link.immutability_reason}"
                    ),
                    location="Section 0 (Intent Alignment)",
                    suggestion=(
                        "Link to a specific commit SHA, not a branch. "
                        "Example: /blob/a1b2c3d/docs/spec.md instead of /blob/main/..."
                    ),
                ))
        elif isinstance(intent_link, str):
            errors.append(self._make_finding(
                rule_id="E004",
                severity="warn",
                message=(
                    "Class E Evidence is a plain text reference, not a URL. "
                    "Consider using a SHA-pinned permalink for immutability."
                ),
                location="Section 0 (Intent Alignment)",
            ))

        # Validate claim artifacts
        for claim in packet.claims:
            if isinstance(claim.artifact, ArtifactLink):
                link = claim.artifact

                # GitHub blob/tree links should be immutable
                if link.link_type == "github_blob" and not link.is_immutable:
                    errors.append(self._make_finding(
                        rule_id="E009",
                        severity="block",
                        message=(
                            f"Evidence artifact link is mutable. "
                            f"Reason: {link.immutability_reason}"
                        ),
                        location=f"Section {claim.section_number}",
                        suggestion=(
                            "Use a SHA-pinned link. Copy the link from the "
                            "'Copy permalink' option in GitHub."
                        ),
                    ))

        return errors

    def validate_link_format(self, url: str) -> list[ValidationFinding]:
        """
        Validate a single URL format without network access.
        """
        errors: list[ValidationFinding] = []

        try:
            parsed = urlparse(url)

            if not parsed.scheme:
                errors.append(self._make_finding(
                    rule_id="E009",
                    severity="block",
                    message="URL missing scheme (http/https)",
                    suggestion="Ensure URL starts with https://",
                ))

            if parsed.scheme not in ("http", "https"):
                errors.append(self._make_finding(
                    rule_id="E009",
                    severity="warn",
                    message=f"Unusual URL scheme: {parsed.scheme}",
                ))

            if not parsed.netloc:
                errors.append(self._make_finding(
                    rule_id="E009",
                    severity="block",
                    message="URL missing domain",
                ))

        except Exception as e:
            errors.append(self._make_finding(
                rule_id="E009",
                severity="block",
                message=f"Invalid URL format: {e}",
            ))

        return errors
