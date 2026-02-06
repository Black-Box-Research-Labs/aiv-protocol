"""
aiv/lib/parser.py

Markdown packet parser using AST analysis.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from .models import (
    ArtifactLink,
    Claim,
    EvidenceClass,
    IntentSection,
    VerificationPacket,
    ValidationFinding,
    Severity,
)
from .errors import PacketParseError


@dataclass
class ParsedSection:
    """Intermediate representation of a parsed section."""
    level: int
    title: str
    content: list[str] = field(default_factory=list)
    raw_start: int = 0
    raw_end: int = 0


class PacketParser:
    """
    Parser for AIV Verification Packets.

    Converts markdown text into structured VerificationPacket objects.
    Uses regex-based section extraction rather than a full AST library
    to minimize dependencies while remaining robust.
    """

    # Regex patterns for field extraction
    FIELD_PATTERNS = {
        "evidence_class": re.compile(
            r"\*\*Evidence\s+Class:\*\*\s*([A-F](?:\s*\([^)]+\))?)",
            re.IGNORECASE
        ),
        "evidence_artifact": re.compile(
            r"\*\*Evidence\s+Artifact:\*\*\s*(.+?)(?=\n\*\*|\n##|\Z)",
            re.IGNORECASE | re.DOTALL
        ),
        "reproduction": re.compile(
            r"\*\*Reproduction(?:\s+Instructions)?:\*\*\s*(.+?)(?=\n\*\*|\n##|\Z)",
            re.IGNORECASE | re.DOTALL
        ),
        "class_e_evidence": re.compile(
            r"\*\*Class\s+E\s+Evidence:\*\*\s*(.+?)(?=\n\*\*|\n##|\Z)",
            re.IGNORECASE | re.DOTALL
        ),
        "verifier_check": re.compile(
            r"\*\*Verifier\s+Check:\*\*\s*(.+?)(?=\n\*\*|\n##|\Z)",
            re.IGNORECASE | re.DOTALL
        ),
        "justification": re.compile(
            r"\*\*Justification:\*\*\s*(.+?)(?=\n\*\*|\n##|\Z)",
            re.IGNORECASE | re.DOTALL
        ),
    }

    # Pattern for extracting URLs from markdown links
    URL_PATTERN = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")

    # Pattern for packet header
    HEADER_PATTERN = re.compile(
        r"#\s*AIV\s+Verification\s+Packet(?:\s*\(v?([\d.]+)\))?",
        re.IGNORECASE
    )

    # Pattern for claim section title
    CLAIM_PATTERN = re.compile(
        r"(?:Claim(?:\s*\d+)?:?\s*)?(.+)",
        re.IGNORECASE
    )

    # Pattern for markdown headings
    HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

    def __init__(self) -> None:
        self.errors: list[ValidationFinding] = []

    def parse(self, markdown_text: str) -> VerificationPacket | None:
        """
        Parse markdown text into a VerificationPacket.

        Args:
            markdown_text: Raw markdown content from PR description

        Returns:
            Parsed packet if successful, None if critical parse failure

        Raises:
            PacketParseError: If packet is missing or fundamentally malformed
        """
        self.errors = []

        # Check for packet header
        header_match = self.HEADER_PATTERN.search(markdown_text)
        if not header_match:
            raise PacketParseError(
                "Missing packet header. Expected '# AIV Verification Packet'"
            )

        version = header_match.group(1) or "2.1"

        # Parse into sections
        sections = self._extract_sections(markdown_text)

        # Find Section 0 (Intent Alignment)
        intent = self._parse_intent_section(sections, markdown_text)
        if intent is None:
            raise PacketParseError(
                "Missing Section 0: Intent Alignment (required by Addendum 2.1)"
            )

        # Parse claim sections
        claims = self._parse_claim_sections(sections, markdown_text)
        if not claims:
            raise PacketParseError(
                "No valid claims found. At least one claim is required."
            )

        return VerificationPacket(
            version=version,
            intent=intent,
            claims=claims,
            raw_markdown=markdown_text,
        )

    def _extract_sections(self, markdown_text: str) -> list[ParsedSection]:
        """Extract sections from markdown using heading detection."""
        sections: list[ParsedSection] = []
        lines = markdown_text.split("\n")

        current_section: ParsedSection | None = None
        current_content: list[str] = []

        for i, line in enumerate(lines):
            heading_match = self.HEADING_PATTERN.match(line)
            if heading_match:
                # Save previous section
                if current_section is not None:
                    current_section.content = current_content
                    current_section.raw_end = i - 1
                    sections.append(current_section)

                # Start new section
                level = len(heading_match.group(1))
                title = heading_match.group(2).strip()
                current_section = ParsedSection(
                    level=level,
                    title=title,
                    raw_start=i,
                )
                current_content = []
            else:
                current_content.append(line)

        # Save last section
        if current_section is not None:
            current_section.content = current_content
            current_section.raw_end = len(lines) - 1
            sections.append(current_section)

        return sections

    def _parse_intent_section(
        self,
        sections: list[ParsedSection],
        raw_text: str
    ) -> IntentSection | None:
        """Parse Section 0: Intent Alignment."""

        # Find section with "Intent" or "0." in title
        intent_section = None
        for section in sections:
            title_lower = section.title.lower()
            if "intent" in title_lower or section.title.startswith("0"):
                intent_section = section
                break

        if intent_section is None:
            return None

        content = "\n".join(intent_section.content)

        # Extract Class E Evidence link
        class_e_match = self.FIELD_PATTERNS["class_e_evidence"].search(content)
        if not class_e_match:
            self.errors.append(ValidationFinding(
                rule_id="E003",
                severity=Severity.BLOCK,
                message="Missing Class E Evidence link in Intent section",
                location="Section 0",
                suggestion="Add '**Class E Evidence:** [Link](url)'"
            ))
            return None

        # Extract URL from the field
        url = self._extract_url(class_e_match.group(1))
        if not url:
            self.errors.append(ValidationFinding(
                rule_id="E003",
                severity=Severity.BLOCK,
                message="Class E Evidence must contain a valid URL",
                location="Section 0",
            ))
            return None

        # Extract Verifier Check
        verifier_match = self.FIELD_PATTERNS["verifier_check"].search(content)
        verifier_check = verifier_match.group(1).strip() if verifier_match else ""

        if len(verifier_check) < 10:
            self.errors.append(ValidationFinding(
                rule_id="E002",
                severity=Severity.WARN,
                message="Verifier Check description is too brief",
                location="Section 0",
                suggestion="Describe what the verifier should confirm (min 10 chars)"
            ))
            verifier_check = verifier_check or "See linked specification"

        return IntentSection(
            evidence_link=ArtifactLink.from_url(url),
            verifier_check=verifier_check,
        )

    def _parse_claim_sections(
        self,
        sections: list[ParsedSection],
        raw_text: str
    ) -> list[Claim]:
        """Parse numbered claim sections."""

        claims: list[Claim] = []

        for section in sections:
            # Skip non-claim sections
            if section.level != 2:  # Claims should be ## level
                continue

            # Skip Section 0
            if "intent" in section.title.lower() or section.title.startswith("0"):
                continue

            # Try to extract section number
            number_match = re.match(r"(\d+)\.", section.title)
            if not number_match:
                continue

            section_number = int(number_match.group(1))

            # Extract claim description from title
            claim_match = self.CLAIM_PATTERN.search(
                section.title[number_match.end():].strip()
            )
            description = claim_match.group(1).strip() if claim_match else section.title

            content = "\n".join(section.content)

            # Extract Evidence Class
            class_match = self.FIELD_PATTERNS["evidence_class"].search(content)
            if not class_match:
                self.errors.append(ValidationFinding(
                    rule_id="E006",
                    severity=Severity.BLOCK,
                    message=f"Missing Evidence Class in Section {section_number}",
                    location=f"Section {section_number}",
                ))
                continue

            try:
                evidence_class = EvidenceClass.from_string(class_match.group(1))
            except ValueError as e:
                self.errors.append(ValidationFinding(
                    rule_id="E006",
                    severity=Severity.BLOCK,
                    message=f"Invalid Evidence Class: {e}",
                    location=f"Section {section_number}",
                ))
                continue

            # Extract Evidence Artifact
            artifact_match = self.FIELD_PATTERNS["evidence_artifact"].search(content)
            if not artifact_match:
                self.errors.append(ValidationFinding(
                    rule_id="E007",
                    severity=Severity.BLOCK,
                    message=f"Missing Evidence Artifact in Section {section_number}",
                    location=f"Section {section_number}",
                ))
                continue

            artifact_text = artifact_match.group(1).strip()
            artifact_url = self._extract_url(artifact_text)

            artifact: ArtifactLink | str
            if artifact_url:
                artifact = ArtifactLink.from_url(artifact_url)
            else:
                artifact = artifact_text

            # Extract Reproduction
            repro_match = self.FIELD_PATTERNS["reproduction"].search(content)
            reproduction = repro_match.group(1).strip() if repro_match else "N/A"

            # Extract Justification (for Class F)
            justification: str | None = None
            if evidence_class == EvidenceClass.CONSERVATION:
                just_match = self.FIELD_PATTERNS["justification"].search(content)
                justification = just_match.group(1).strip() if just_match else None

            claims.append(Claim(
                section_number=section_number,
                description=description,
                evidence_class=evidence_class,
                artifact=artifact,
                reproduction=reproduction,
                justification=justification,
            ))

        return sorted(claims, key=lambda c: c.section_number)

    def _extract_url(self, text: str) -> str | None:
        """Extract URL from markdown link or plain text."""

        # Try markdown link format first
        match = self.URL_PATTERN.search(text)
        if match:
            return match.group(2)

        # Try plain URL
        url_match = re.search(r"https?://[^\s\)]+", text)
        if url_match:
            return url_match.group(0)

        return None
