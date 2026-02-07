"""
aiv/lib/parser.py

Markdown packet parser for AIV Verification Packets.

Handles the standard template format used in .github/aiv-packets/:
  - # AIV Verification Packet (v2.1)
  - ## Classification (required)
  - ## Claim(s) — numbered list items
  - ## Evidence — with ### Class E/B/A/C/D/F subsections
  - ## Verification Methodology
  - ## Summary
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

    Supports the actual template format from VERIFICATION_PACKET_TEMPLATE.md:
    - Claims listed as numbered items under ## Claim(s)
    - Evidence grouped by class under ## Evidence > ### Class X
    """

    # Pattern for extracting URLs from markdown links
    URL_PATTERN = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")

    # Pattern for packet header
    HEADER_PATTERN = re.compile(
        r"#\s*AIV\s+Verification\s+Packet(?:\s*\(v?([\d.]+)\))?",
        re.IGNORECASE
    )

    # Pattern for markdown headings
    HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

    # Pattern for numbered list items (claims)
    NUMBERED_ITEM_PATTERN = re.compile(r"^(\d+)\.\s+(.+)$")

    # Pattern for evidence class subsection titles
    EVIDENCE_CLASS_PATTERN = re.compile(
        r"Class\s+([A-F])\b", re.IGNORECASE
    )

    def __init__(self) -> None:
        self.errors: list[ValidationFinding] = []

    def parse(self, markdown_text: str) -> VerificationPacket | None:
        """
        Parse markdown text into a VerificationPacket.

        Args:
            markdown_text: Raw markdown content from PR description or packet file

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

        # Parse intent from ## Evidence > ### Class E
        intent = self._parse_intent(sections)
        if intent is None:
            raise PacketParseError(
                "Missing Class E (Intent Alignment) evidence section"
            )

        # Parse claims from ## Claim(s) section
        claims = self._parse_claims(sections)
        if not claims:
            raise PacketParseError(
                "No valid claims found. At least one numbered claim is required."
            )

        # Enrich claims with evidence from ## Evidence subsections
        claims = self._enrich_claims_with_evidence(claims, sections)

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

    def _find_section(
        self,
        sections: list[ParsedSection],
        title_contains: str,
        level: int | None = None,
    ) -> ParsedSection | None:
        """Find a section by title substring and optional level."""
        for section in sections:
            if title_contains.lower() in section.title.lower():
                if level is None or section.level == level:
                    return section
        return None

    def _parse_intent(self, sections: list[ParsedSection]) -> IntentSection | None:
        """
        Parse intent from ### Class E (Intent Alignment) under ## Evidence.

        Also handles legacy format where intent is ## 0. Intent Alignment.
        """
        # Strategy 1: Look for ### Class E subsection under ## Evidence
        class_e = self._find_section(sections, "class e", level=3)
        if class_e:
            return self._build_intent_from_class_e(class_e)

        # Strategy 2: Legacy format — ## section with "Intent" or "0."
        for section in sections:
            if section.level == 2:
                title_lower = section.title.lower()
                if "intent" in title_lower or section.title.startswith("0"):
                    return self._build_intent_from_legacy(section)

        return None

    def _build_intent_from_class_e(self, section: ParsedSection) -> IntentSection | None:
        """Build IntentSection from ### Class E section content."""
        content = "\n".join(section.content)

        # Extract **Link:** field
        link_match = re.search(
            r"\*\*Link:\*\*\s*(.+?)(?=\n\*\*|\n##|\n###|\Z)",
            content, re.DOTALL | re.IGNORECASE
        )

        evidence_link: ArtifactLink | str
        if link_match:
            link_text = link_match.group(1).strip()
            url = self._extract_url(link_text)
            if url:
                evidence_link = ArtifactLink.from_url(url)
            else:
                # Plain text reference (e.g. "AIV Protocol Addendum 2.5 — ...")
                evidence_link = link_text
        else:
            # No **Link:** field — use first line of content as reference
            first_line = content.strip().split("\n")[0] if content.strip() else ""
            evidence_link = first_line or "See evidence section"

        # Extract **Requirements Verified:** as verifier check
        req_match = re.search(
            r"\*\*Requirements\s+Verified:\*\*\s*(.+?)(?=\n###|\n##|\Z)",
            content, re.DOTALL | re.IGNORECASE
        )
        if req_match:
            verifier_check = req_match.group(1).strip()
        else:
            # Fall back to full section content
            verifier_check = content.strip()

        # Ensure minimum length
        if len(verifier_check) < 10:
            verifier_check = f"Class E evidence: {verifier_check or 'see linked specification'}"

        return IntentSection(
            evidence_link=evidence_link,
            verifier_check=verifier_check[:500],  # Truncate if very long
        )

    def _build_intent_from_legacy(self, section: ParsedSection) -> IntentSection | None:
        """Build IntentSection from legacy ## 0. Intent Alignment format."""
        content = "\n".join(section.content)

        # Look for **Class E Evidence:** field
        class_e_match = re.search(
            r"\*\*Class\s+E\s+Evidence:\*\*\s*(.+?)(?=\n\*\*|\n##|\Z)",
            content, re.DOTALL | re.IGNORECASE
        )

        evidence_link: ArtifactLink | str
        if class_e_match:
            link_text = class_e_match.group(1).strip()
            url = self._extract_url(link_text)
            if url:
                evidence_link = ArtifactLink.from_url(url)
            else:
                evidence_link = link_text
        else:
            evidence_link = "See intent section"

        # Extract **Verifier Check:** field
        verifier_match = re.search(
            r"\*\*Verifier\s+Check:\*\*\s*(.+?)(?=\n\*\*|\n##|\Z)",
            content, re.DOTALL | re.IGNORECASE
        )
        verifier_check = verifier_match.group(1).strip() if verifier_match else ""

        if len(verifier_check) < 10:
            verifier_check = verifier_check or "See linked specification"

        return IntentSection(
            evidence_link=evidence_link,
            verifier_check=verifier_check,
        )

    def _parse_claims(self, sections: list[ParsedSection]) -> list[Claim]:
        """
        Parse claims from ## Claim(s) section.

        Claims are numbered list items: "1. Description of claim"
        """
        # Find ## Claim(s) section
        claims_section = self._find_section(sections, "claim", level=2)
        if not claims_section:
            return []

        claims: list[Claim] = []
        for line in claims_section.content:
            match = self.NUMBERED_ITEM_PATTERN.match(line.strip())
            if match:
                number = int(match.group(1))
                description = match.group(2).strip()

                # Strip markdown bold if present
                description = re.sub(r"\*\*(.+?)\*\*", r"\1", description)

                # Skip if description is too short
                if len(description) < 10:
                    self.errors.append(ValidationFinding(
                        rule_id="E005",
                        severity=Severity.WARN,
                        message=f"Claim {number} description is too brief",
                        location=f"Claim {number}",
                    ))
                    continue

                claims.append(Claim(
                    section_number=number,
                    description=description,
                    evidence_class=EvidenceClass.REFERENTIAL,  # Default; enriched later
                    artifact="See Evidence section",  # Default; enriched later
                    reproduction="N/A",  # Default; enriched later
                ))

        return sorted(claims, key=lambda c: c.section_number)

    def _enrich_claims_with_evidence(
        self,
        claims: list[Claim],
        sections: list[ParsedSection],
    ) -> list[Claim]:
        """
        Enrich claims with evidence from ## Evidence subsections.

        Scans ### Class B, ### Class A, etc. for "Claim N:" references
        and updates the corresponding claim's evidence_class and artifact.
        """
        evidence_sections = [
            s for s in sections
            if s.level == 3 and self.EVIDENCE_CLASS_PATTERN.search(s.title)
        ]

        # Build a map: claim_number -> (evidence_class, artifact_text)
        claim_evidence: dict[int, tuple[EvidenceClass, str]] = {}
        # Track evidence sections that don't reference specific claims
        unlinked_evidence: list[tuple[EvidenceClass, str]] = []

        for ev_section in evidence_sections:
            class_match = self.EVIDENCE_CLASS_PATTERN.search(ev_section.title)
            if not class_match:
                continue

            try:
                ev_class = EvidenceClass.from_string(class_match.group(1))
            except ValueError:
                continue

            # Skip Class E — handled separately as IntentSection
            if ev_class == EvidenceClass.INTENT:
                continue

            content = "\n".join(ev_section.content)

            # Find "Claim N:" references
            claim_refs = list(re.finditer(
                r"(?:\*\*)?Claim\s+(\d+)(?:-(\d+))?(?:\s*:.+?)?(?:\*\*)?",
                content, re.IGNORECASE
            ))

            if claim_refs:
                for ref in claim_refs:
                    start = int(ref.group(1))
                    end = int(ref.group(2)) if ref.group(2) else start
                    # Extract the content after this claim reference
                    ref_pos = ref.end()
                    next_claim = re.search(
                        r"\n\*\*Claim\s+\d+",
                        content[ref_pos:], re.IGNORECASE
                    )
                    artifact_text = content[ref_pos:ref_pos + (next_claim.start() if next_claim else len(content[ref_pos:]))]
                    artifact_text = artifact_text.strip()

                    # Try to extract a URL from the artifact text
                    url = self._extract_url(artifact_text)

                    for n in range(start, end + 1):
                        if url:
                            claim_evidence[n] = (ev_class, url)
                        elif artifact_text:
                            claim_evidence[n] = (ev_class, artifact_text)
            else:
                # No "Claim N:" references — this evidence applies broadly
                artifact_text = content.strip()
                if artifact_text:
                    unlinked_evidence.append((ev_class, artifact_text))

        # Reproduction defaults to "N/A" (zero-touch compliant).
        # The ## Verification Methodology section is informational context
        # for the packet as a whole, not a per-claim reproduction instruction.
        reproduction = "N/A"

        # Rebuild claims with enriched evidence
        enriched: list[Claim] = []
        for claim in claims:
            ev_class = claim.evidence_class
            artifact: ArtifactLink | str = claim.artifact

            if claim.section_number in claim_evidence:
                ev_class, artifact_raw = claim_evidence[claim.section_number]
                url = self._extract_url(artifact_raw) if not artifact_raw.startswith("http") else artifact_raw
                if url:
                    try:
                        artifact = ArtifactLink.from_url(url)
                    except Exception:
                        artifact = artifact_raw
                else:
                    artifact = artifact_raw
            elif unlinked_evidence:
                # Apply the best matching unlinked evidence to unenriched claims.
                # Prefer evidence whose class matches the claim's default, then
                # fall back to the first available unlinked evidence.
                best = unlinked_evidence[0]
                for ue_class, ue_artifact in unlinked_evidence:
                    if ue_class == claim.evidence_class:
                        best = (ue_class, ue_artifact)
                        break
                ev_class, artifact = best

            # Since Claim is frozen, we must create a new instance
            enriched.append(Claim(
                section_number=claim.section_number,
                description=claim.description,
                evidence_class=ev_class,
                artifact=artifact,
                reproduction=reproduction,
            ))

        return enriched

    def _extract_url(self, text: str) -> str | None:
        """Extract URL from markdown link or plain text."""

        # Try markdown link format first
        match = self.URL_PATTERN.search(text)
        if match:
            return match.group(2)

        # Try plain URL
        url_match = re.search(r"https?://[^\s\)\>]+", text)
        if url_match:
            return url_match.group(0)

        return None
