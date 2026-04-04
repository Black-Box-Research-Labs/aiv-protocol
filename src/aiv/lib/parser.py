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

import contextlib
import re
from dataclasses import dataclass, field

from .errors import PacketParseError
from .models import (
    ArtifactLink,
    Claim,
    EvidenceClass,
    IntentSection,
    RiskTier,
    Severity,
    ValidationFinding,
    VerificationPacket,
)


@dataclass
class ParsedSection:
    """Intermediate representation of a parsed section."""

    level: int
    title: str
    content: list[str] = field(default_factory=list)
    raw_start: int = 0
    raw_end: int = 0


@dataclass
class ParseResult:
    """Result of parsing a verification packet."""

    packet: VerificationPacket | None
    errors: list[ValidationFinding] = field(default_factory=list)


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
    HEADER_PATTERN = re.compile(r"#\s*AIV\s+Verification\s+Packet(?:\s*\(v?([\d.]+)\))?", re.IGNORECASE)

    # Pattern for markdown headings
    HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

    # Pattern for numbered list items (claims)
    NUMBERED_ITEM_PATTERN = re.compile(r"^(\d+)\.\s+(.+)$")

    # Pattern for evidence class subsection titles
    EVIDENCE_CLASS_PATTERN = re.compile(r"Class\s+([A-F])\b", re.IGNORECASE)

    # Always-placeholder keywords: strip entire line regardless of trailing text.
    # "TODO: Before/after diff" is a placeholder even with descriptive text.
    _ALWAYS_PLACEHOLDER_RE = re.compile(
        r"^[\s\-*]*(TODO|TBD|PENDING|FIXME|XXX)[:\s.].*$",
        re.IGNORECASE | re.MULTILINE,
    )

    # Exemption keywords: only placeholder when alone (no explanation).
    # "N/A" alone is a placeholder; "N/A — config file, no execution" is valid.
    _EXEMPTION_PLACEHOLDER_RE = re.compile(
        r"^[\s\-*]*(N/?A|NONE)\s*[:\.]?\s*$",
        re.IGNORECASE | re.MULTILINE,
    )

    # Minimum non-placeholder alphabetic characters for substance
    _MIN_SUBSTANCE_ALPHA = 10

    def __init__(self) -> None:
        self._last_errors: list[ValidationFinding] = []

    @property
    def errors(self) -> list[ValidationFinding]:
        """Errors from the most recent parse() call (backward-compat)."""
        return self._last_errors

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
        errors: list[ValidationFinding] = []

        # Check for packet header
        header_match = self.HEADER_PATTERN.search(markdown_text)
        if not header_match:
            raise PacketParseError("Missing packet header. Expected '# AIV Verification Packet'")

        version = header_match.group(1)
        if not version:
            version = "2.1"
            errors.append(
                ValidationFinding(
                    rule_id="E001",
                    severity=Severity.INFO,
                    message=(
                        "Packet header lacks explicit version "
                        "(e.g. '# AIV Verification Packet (v2.1)'). "
                        "Defaulting to v2.1."
                    ),
                    location="Header",
                    suggestion="Add the version to the header: # AIV Verification Packet (v2.1)",
                )
            )

        # Parse into sections
        sections = self._extract_sections(markdown_text)

        # Parse intent from ## Evidence > ### Class E
        intent = self._parse_intent(sections)
        if intent is None:
            raise PacketParseError("Missing Class E (Intent Alignment) evidence section")

        # Parse claims from ## Claim(s) section
        claims = self._parse_claims(sections, errors)
        if not claims:
            raise PacketParseError("No valid claims found. At least one numbered claim is required.")

        # Enrich claims with evidence from ## Evidence subsections
        claims = self._enrich_claims_with_evidence(claims, sections)

        # Collect all evidence classes present in evidence sections
        evidence_classes_present = self._collect_evidence_classes(sections)
        # Intent (Class E) is always present if we got here
        evidence_classes_present.add(EvidenceClass.INTENT)
        # Also include evidence classes from enriched claims
        for claim in claims:
            evidence_classes_present.add(claim.evidence_class)

        # Parse classification (optional — may not be present in older packets)
        risk_tier = self._parse_classification(sections, errors)

        # Store errors for backward-compat property access
        self._last_errors = errors

        return VerificationPacket(
            version=version,
            risk_tier=risk_tier,
            evidence_classes_present=evidence_classes_present,
            intent=intent,
            claims=claims,
            raw_markdown=markdown_text,
        )

    _FENCE_PATTERN = re.compile(r"^(`{3,}|~{3,})")

    def _extract_sections(self, markdown_text: str) -> list[ParsedSection]:
        """Extract sections from markdown using heading detection."""
        sections: list[ParsedSection] = []
        lines = markdown_text.split("\n")

        current_section: ParsedSection | None = None
        current_content: list[str] = []
        in_fence = False
        fence_char = ""
        fence_len = 0

        for i, line in enumerate(lines):
            fence_match = self._FENCE_PATTERN.match(line)
            if fence_match:
                matched = fence_match.group(1)
                if not in_fence:
                    in_fence = True
                    fence_char = matched[0]
                    fence_len = len(matched)
                else:
                    stripped = line.strip()
                    if (
                        stripped[0] == fence_char
                        and len(stripped) >= fence_len
                        and stripped == fence_char * len(stripped)
                    ):
                        in_fence = False
                        fence_char = ""
                        fence_len = 0
                current_content.append(line)
                continue

            if in_fence:
                current_content.append(line)
                continue

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

    def _parse_classification(self, sections: list[ParsedSection], errors: list[ValidationFinding]) -> RiskTier | None:
        """
        Parse risk_tier from ## Classification (required) YAML code block.

        Expected format in packet:
            ## Classification (required)
            ```yaml
            classification:
              risk_tier: R2
              ...
            ```

        Returns None if section or risk_tier not found (graceful degradation
        for older packets without classification).
        """
        section = self._find_section(sections, "classification", level=2)
        if not section:
            return None

        content = "\n".join(section.content)

        # Extract risk_tier from YAML-like content (simple regex, avoids
        # requiring PyYAML just for one field extraction).
        tier_match = re.search(r"risk_tier:\s*(R[0-3])\b", content, re.IGNORECASE)
        if not tier_match:
            return None

        try:
            return RiskTier.from_string(tier_match.group(1))
        except ValueError:
            errors.append(
                ValidationFinding(
                    rule_id="E001",
                    severity=Severity.WARN,
                    message=f"Invalid risk_tier value: {tier_match.group(1)!r}",
                    location="## Classification",
                )
            )
            return None

    def _collect_evidence_classes(self, sections: list[ParsedSection]) -> set[EvidenceClass]:
        """Scan all ### Class X evidence sections and return the set of classes found.

        Only counts a section as present if its content is substantive —
        headings with only placeholder text (TODO, TBD, N/A, etc.) are ignored.

        Also parses ## Evidence References tables (Layer 2 packets) to extract
        classes from the Classes column (e.g., "A, B").
        """
        found: set[EvidenceClass] = set()
        for s in sections:
            if s.level == 3:
                match = self.EVIDENCE_CLASS_PATTERN.search(s.title)
                if match:
                    try:
                        ev_class = EvidenceClass.from_string(match.group(1))
                        if self._is_substantive(s.content):
                            found.add(ev_class)
                    except ValueError:
                        pass

            # Layer 2: ## Evidence References table with Classes column
            if s.level == 2 and "evidence references" in s.title.lower():
                found.update(self._parse_evidence_refs_table(s.content))

        return found

    _EVIDENCE_REF_CLASS_RE = re.compile(r"[ABCDEF]")

    def _parse_evidence_refs_table(self, content: list[str]) -> set[EvidenceClass]:
        """Extract evidence classes from a markdown table's Classes column."""
        found: set[EvidenceClass] = set()
        header_idx: int | None = None

        for line in content:
            stripped = line.strip()
            if not stripped.startswith("|"):
                continue

            cells = [c.strip() for c in stripped.split("|") if c.strip()]

            # Find the Classes column in the header row
            if header_idx is None:
                for i, cell in enumerate(cells):
                    if cell.lower() in ("classes", "class"):
                        header_idx = i
                        break
                continue

            # Skip separator row
            if all(c.replace("-", "").replace(":", "").strip() == "" for c in cells):
                continue

            # Extract classes from the identified column
            if header_idx is not None and header_idx < len(cells):
                class_cell = cells[header_idx]
                for letter in self._EVIDENCE_REF_CLASS_RE.findall(class_cell):
                    with contextlib.suppress(ValueError):
                        found.add(EvidenceClass.from_string(letter))

        return found

    def _is_substantive(self, content: list[str]) -> bool:
        """Return True if section content is more than just placeholders."""
        joined = "\n".join(content).strip()
        if not joined:
            return False
        # Strip lines with always-placeholder keywords (TODO, TBD, etc.)
        cleaned = self._ALWAYS_PLACEHOLDER_RE.sub("", joined)
        # Strip exemption keywords only when alone (N/A, NONE without explanation)
        non_placeholder = self._EXEMPTION_PLACEHOLDER_RE.sub("", cleaned).strip()
        # Must have real alphanumeric content beyond punctuation/bullets
        alpha_content = re.sub(r"[^a-zA-Z0-9]", "", non_placeholder)
        return len(alpha_content) >= self._MIN_SUBSTANCE_ALPHA

    def _parse_intent(self, sections: list[ParsedSection]) -> IntentSection | None:
        """
        Parse intent from ### Class E (Intent Alignment) under ## Evidence.
        """
        # Strategy 1: Look for ### Class E subsection under ## Evidence
        class_e = self._find_section(sections, "class e", level=3)
        if class_e:
            return self._build_intent_from_class_e(class_e)

        return None

    def _build_intent_from_class_e(self, section: ParsedSection) -> IntentSection | None:
        """Build IntentSection from ### Class E section content."""
        content = "\n".join(section.content)

        # Extract **Link:** field
        link_match = re.search(r"\*\*Link:\*\*\s*(.+?)(?=\n\*\*|\n##|\n###|\Z)", content, re.DOTALL | re.IGNORECASE)

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
            r"\*\*Requirements\s+Verified:\*\*\s*(.+?)(?=\n###|\n##|\Z)", content, re.DOTALL | re.IGNORECASE
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

    def _parse_claims(self, sections: list[ParsedSection], errors: list[ValidationFinding]) -> list[Claim]:
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

                # Skip if description is too short (unified with structure.py threshold)
                if len(description) < 15:
                    errors.append(
                        ValidationFinding(
                            rule_id="E005",
                            severity=Severity.WARN,
                            message=f"Claim {number} description is too brief",
                            location=f"Claim {number}",
                        )
                    )
                    continue

                claims.append(
                    Claim(
                        section_number=number,
                        description=description,
                        evidence_class=EvidenceClass.REFERENTIAL,  # Default; enriched later
                        artifact="See Evidence section",  # Default; enriched later
                        reproduction="N/A",  # Default; enriched later
                    )
                )

        return sorted(claims, key=lambda c: c.section_number)

    # Pattern for extracting **Justification:** text from Class F evidence sections
    _JUSTIFICATION_PATTERN = re.compile(
        r"\*\*Justification:\*\*\s*(.+?)(?=\n\*\*|\n##|\n###|\Z)",
        re.DOTALL | re.IGNORECASE,
    )

    def _enrich_claims_with_evidence(
        self,
        claims: list[Claim],
        sections: list[ParsedSection],
    ) -> list[Claim]:
        """
        Enrich claims with evidence from ## Evidence subsections.

        Scans ### Class B, ### Class A, etc. for "Claim N:" references
        and updates the corresponding claim's evidence_class and artifact.

        Each unlinked evidence item (no "Claim N:" reference) is consumed by
        at most one claim to prevent the same artifact from being silently
        applied to multiple claims.

        For Class F (Provenance) sections, extracts **Justification:** text
        and stores it in the claim's ``justification`` field so the anti-cheat
        cross-reference stage can verify it.
        """
        evidence_sections = [s for s in sections if s.level == 3 and self.EVIDENCE_CLASS_PATTERN.search(s.title)]

        # Build a map: claim_number -> (evidence_class, artifact_text)
        claim_evidence: dict[int, tuple[EvidenceClass, str]] = {}
        # Build a map: claim_number -> justification text (from **Justification:** in Class F)
        claim_justification: dict[int, str] = {}
        # Track evidence without explicit claim references; consumed one-per-claim
        # to prevent the same artifact from satisfying multiple claims.
        unlinked_evidence: list[tuple[EvidenceClass, str]] = []
        # Broad justification from an unlinked Class F section (no "Claim N:" ref)
        unlinked_justification: str | None = None

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

            # Extract **Justification:** from Class F (Provenance) sections
            justification_text: str | None = None
            if ev_class == EvidenceClass.PROVENANCE:
                just_match = self._JUSTIFICATION_PATTERN.search(content)
                if just_match:
                    justification_text = just_match.group(1).strip()

            # Find "Claim N:" references
            claim_refs = list(
                re.finditer(r"(?:\*\*)?Claim\s+(\d+)(?:-(\d+))?(?:\s*:.+?)?(?:\*\*)?", content, re.IGNORECASE)
            )

            if claim_refs:
                for ref in claim_refs:
                    start = int(ref.group(1))
                    end = int(ref.group(2)) if ref.group(2) else start
                    # Extract the content after this claim reference
                    ref_pos = ref.end()
                    next_claim = re.search(r"\n\*\*Claim\s+\d+", content[ref_pos:], re.IGNORECASE)
                    end_offset = next_claim.start() if next_claim else len(content[ref_pos:])
                    artifact_text = content[ref_pos : ref_pos + end_offset]
                    artifact_text = artifact_text.strip()

                    # Try to extract a URL from the artifact text
                    url = self._extract_url(artifact_text)

                    for n in range(start, end + 1):
                        if url:
                            claim_evidence[n] = (ev_class, url)
                        elif artifact_text:
                            claim_evidence[n] = (ev_class, artifact_text)
                        if justification_text:
                            claim_justification[n] = justification_text
            else:
                # No "Claim N:" references — collect for heuristic (one-per-claim) assignment
                artifact_text = content.strip()
                if artifact_text:
                    unlinked_evidence.append((ev_class, artifact_text))
                if justification_text:
                    unlinked_justification = justification_text

        # Extract reproduction from ## Verification Methodology section.
        # If absent, default to "N/A" (zero-touch compliant).
        # If present but empty/whitespace, leave as "" so structure validator can flag it.
        methodology = self._find_section(sections, "verification methodology", level=2)
        if methodology:
            reproduction = "\n".join(methodology.content).strip()
        else:
            reproduction = "N/A"

        # Rebuild claims with enriched evidence.
        # ``unlinked_evidence`` is consumed (each item popped after use) so that a single
        # unlinked evidence section cannot silently satisfy multiple distinct claims.
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
                # Consume the best-matching unlinked evidence item (one per claim).
                # Prefer an item whose class matches the claim's default class,
                # then fall back to the first available item.
                best_idx = 0
                for i, (ue_class, _) in enumerate(unlinked_evidence):
                    if ue_class == claim.evidence_class:
                        best_idx = i
                        break
                ev_class, artifact_raw = unlinked_evidence.pop(best_idx)
                url = self._extract_url(artifact_raw) if not artifact_raw.startswith("http") else artifact_raw
                if url:
                    try:
                        artifact = ArtifactLink.from_url(url)
                    except Exception:
                        artifact = artifact_raw
                else:
                    artifact = artifact_raw

            # Resolve justification: explicit per-claim mapping takes priority;
            # fall back to the broad unlinked justification for Class F claims.
            justification: str | None = claim_justification.get(claim.section_number)
            if justification is None and ev_class == EvidenceClass.PROVENANCE:
                justification = unlinked_justification

            # Since Claim is frozen, we must create a new instance
            enriched.append(
                Claim(
                    section_number=claim.section_number,
                    description=claim.description,
                    evidence_class=ev_class,
                    artifact=artifact,
                    reproduction=reproduction,
                    justification=justification,
                )
            )

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
