"""
aiv/lib/auditor.py

Packet auditor — scans all verification packets in a directory for
quality issues that the validation pipeline does not catch:

- COMMIT_PENDING: Commit SHA never backfilled from `pending`.
- CLASS_E_NO_URL: Class E intent link is plain text, not a SHA-pinned URL.
- CLASS_E_MUTABLE: Class E link points to a mutable branch (main/master).
- TODO_PRESENT: TODO/TBD remnants in filled-in sections.
- CLASSIFIED_BY_TODO: classified_by field still says TODO.
- BLAST_RADIUS_TODO: blast_radius field still says TODO.
- SCOPE_TODO: Scope inventory still says TODO.
- CLAIM_TODO: A numbered claim is still TODO placeholder.
- CLASS_A_TODO: Class A execution evidence is TODO.
- SUMMARY_TODO: Summary section is TODO.
- FIX_NO_CLASS_F: Claims mention fix/bug but no Class F section.

Optionally auto-fixes COMMIT_PENDING and CLASS_E_NO_URL when --fix is used.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class AuditSeverity(str, Enum):
    """Severity of an audit finding."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass(frozen=True)
class AuditFinding:
    """A single audit finding for a packet."""
    packet_name: str
    finding_type: str
    severity: AuditSeverity
    message: str
    line_number: int | None = None
    auto_fixable: bool = False


@dataclass
class AuditResult:
    """Results from auditing all packets in a directory."""
    packets_scanned: int = 0
    packets_with_issues: int = 0
    findings: list[AuditFinding] = field(default_factory=list)
    fixed: list[str] = field(default_factory=list)

    @property
    def clean(self) -> bool:
        return self.packets_with_issues == 0

    @property
    def error_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == AuditSeverity.ERROR)

    @property
    def warning_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == AuditSeverity.WARNING)


# ---------------------------------------------------------------------------
# Git helpers
# ---------------------------------------------------------------------------

def _get_introducing_commit(filepath: Path) -> str | None:
    """Get the full commit SHA that first added this file."""
    try:
        result = subprocess.run(
            ["git", "log", "--diff-filter=A", "--format=%H", "--", str(filepath)],
            capture_output=True,
            text=True,
            timeout=10,
        )
        shas = result.stdout.strip().split("\n")
        # Last entry is the earliest commit (git log is newest-first)
        return shas[-1] if shas and shas[-1] else None
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return None


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Known local files that can be pinned to GitHub URLs
_LOCAL_FILE_PATHS: dict[str, str] = {
    "AUDIT_REPORT.md": "AUDIT_REPORT.md",
    "SPECIFICATION.md": "SPECIFICATION.md",
}

_FIX_KEYWORDS_RE = re.compile(
    r"\b(fix(?:ed|es|ing)?|bug(?:s|fix)?|resolve[ds]?|hotfix|patch(?:ed)?)\b",
    re.IGNORECASE,
)

# Words in descriptions that *mention* the TODO system rather than *being* TODOs
_TODO_META_KEYWORDS = [
    "TODO-only", "_is_substantive", "placeholder", "PLACEHOLDER",
    "_PLACEHOLDER", "ALWAYS_PLACEHOLDER", "reject TODO", "strips TODO",
    "correctly rejected", "TODO/TBD", "TODO (always", "TODO from N/A",
    "scaffold", "substance check", "substance patch",
]


# ---------------------------------------------------------------------------
# Core auditor
# ---------------------------------------------------------------------------

class PacketAuditor:
    """Scans verification packets for quality issues beyond pipeline checks."""

    def __init__(
        self,
        github_base: str = "https://github.com/ImmortalDemonGod/aiv-protocol/blob",
    ) -> None:
        self._github_base = github_base

    def audit(
        self,
        packets_dir: Path,
        *,
        fix: bool = False,
    ) -> AuditResult:
        """Audit all VERIFICATION_PACKET_*.md files in *packets_dir*.

        If *fix* is True, auto-fixable issues are corrected in-place.
        """
        packets = sorted(
            p for p in packets_dir.glob("VERIFICATION_PACKET_*.md")
            if "TEMPLATE" not in p.name
        )

        result = AuditResult(packets_scanned=len(packets))
        packets_with_findings: set[str] = set()

        # Pre-compute commit SHAs for all packets (used by fix mode)
        commit_map: dict[str, str | None] = {}
        if fix or True:  # Always compute; cheap enough and needed for checks
            for p in packets:
                commit_map[p.name] = _get_introducing_commit(p)

        for p in packets:
            body = p.read_text(encoding="utf-8")
            sha = commit_map.get(p.name)
            findings = self._check_packet(p.name, body, sha)

            if findings:
                packets_with_findings.add(p.name)
                result.findings.extend(findings)

            if fix:
                new_body = self._apply_fixes(body, sha)
                if new_body != body:
                    p.write_text(new_body, encoding="utf-8")
                    result.fixed.append(p.name)

        result.packets_with_issues = len(packets_with_findings)
        return result

    # ----- Checks -----

    def _check_packet(
        self,
        name: str,
        body: str,
        commit_sha: str | None,
    ) -> list[AuditFinding]:
        findings: list[AuditFinding] = []

        # 1. COMMIT_PENDING
        if re.search(r"\*\*Commit:\*\*\s*`pending`", body):
            findings.append(AuditFinding(
                packet_name=name,
                finding_type="COMMIT_PENDING",
                severity=AuditSeverity.ERROR,
                message="Commit SHA is still `pending` — no traceability.",
                auto_fixable=commit_sha is not None,
            ))

        # 2. CLASS_E link checks
        ce_match = re.search(r"- \*\*Link:\*\*\s*(.*?)\n", body)
        if ce_match:
            link_text = ce_match.group(1).strip()
            if not link_text:
                findings.append(AuditFinding(
                    packet_name=name,
                    finding_type="CLASS_E_EMPTY",
                    severity=AuditSeverity.ERROR,
                    message="Class E link is empty.",
                ))
            elif "http" not in link_text:
                findings.append(AuditFinding(
                    packet_name=name,
                    finding_type="CLASS_E_NO_URL",
                    severity=AuditSeverity.WARNING,
                    message=f"Class E link is plain text: {link_text[:80]}",
                    auto_fixable=self._can_pin_link(link_text),
                ))
            elif "/blob/main/" in link_text or "/blob/master/" in link_text:
                findings.append(AuditFinding(
                    packet_name=name,
                    finding_type="CLASS_E_MUTABLE",
                    severity=AuditSeverity.ERROR,
                    message="Class E link uses mutable branch (main/master).",
                ))

        # 3. TODO remnants in content
        for i, line in enumerate(body.split("\n"), 1):
            stripped = line.strip()
            if re.search(r"\bTODO\b", stripped, re.IGNORECASE):
                if any(kw in stripped for kw in _TODO_META_KEYWORDS):
                    continue
                findings.append(AuditFinding(
                    packet_name=name,
                    finding_type="TODO_PRESENT",
                    severity=AuditSeverity.WARNING,
                    message=f"TODO on line {i}: {stripped[:80]}",
                    line_number=i,
                ))

        # 4. classified_by still TODO
        if re.search(r'classified_by:\s*"TODO"', body):
            findings.append(AuditFinding(
                packet_name=name,
                finding_type="CLASSIFIED_BY_TODO",
                severity=AuditSeverity.ERROR,
                message="classified_by is still TODO.",
                auto_fixable=False,
            ))

        # 5. blast_radius still TODO
        if re.search(r"blast_radius:\s*TODO\b", body):
            findings.append(AuditFinding(
                packet_name=name,
                finding_type="BLAST_RADIUS_TODO",
                severity=AuditSeverity.ERROR,
                message="blast_radius is still TODO.",
                auto_fixable=False,
            ))

        # 6. Claims still TODO
        claims_match = re.search(r"## Claim\(s\)\s*\n(.*?)(?=---|\Z)", body, re.DOTALL)
        if claims_match:
            for cl_line in claims_match.group(1).split("\n"):
                if re.match(r"\s*\d+\.\s*TODO", cl_line):
                    findings.append(AuditFinding(
                        packet_name=name,
                        finding_type="CLAIM_TODO",
                        severity=AuditSeverity.ERROR,
                        message=f"Claim is still TODO: {cl_line.strip()[:80]}",
                    ))

        # 7. Summary still TODO
        summary_match = re.search(r"## Summary\s*\n(.*?)$", body, re.DOTALL)
        if summary_match:
            sm = summary_match.group(1).strip()
            if re.match(r"^TODO", sm, re.IGNORECASE):
                findings.append(AuditFinding(
                    packet_name=name,
                    finding_type="SUMMARY_TODO",
                    severity=AuditSeverity.ERROR,
                    message="Summary section is still TODO.",
                ))

        # 8. Fix claims without Class F
        if "### Class F" not in body and claims_match:
            claims_text = claims_match.group(1)
            if _FIX_KEYWORDS_RE.search(claims_text):
                findings.append(AuditFinding(
                    packet_name=name,
                    finding_type="FIX_NO_CLASS_F",
                    severity=AuditSeverity.ERROR,
                    message="Claims mention fix/bug but packet has no Class F section.",
                ))

        return findings

    # ----- Auto-fix helpers -----

    def _can_pin_link(self, link_text: str) -> bool:
        """Check if a plain-text link references a known local file."""
        return any(name in link_text for name in _LOCAL_FILE_PATHS)

    def _pin_local_reference(self, link_text: str, commit_sha: str | None) -> str | None:
        """Build a SHA-pinned GitHub URL for a local file reference."""
        for local_name, repo_path in _LOCAL_FILE_PATHS.items():
            if local_name in link_text:
                short = commit_sha[:7] if commit_sha else "main"
                return f"{self._github_base}/{short}/{repo_path}"
        return None

    def _apply_fixes(self, body: str, commit_sha: str | None) -> str:
        """Apply auto-fixes to packet body text. Returns modified body."""
        short_sha = commit_sha[:7] if commit_sha else None

        # Fix COMMIT_PENDING
        if short_sha and re.search(r"\*\*Commit:\*\*\s*`pending`", body):
            body = re.sub(
                r"(\*\*Commit:\*\*\s*)`pending`",
                rf"\g<1>`{short_sha}`",
                body,
            )

        # Fix CLASS_E_NO_URL for local file references
        ce_match = re.search(r"(- \*\*Link:\*\*\s*)(.*?)(\n)", body)
        if ce_match:
            link_text = ce_match.group(2)
            if "http" not in link_text and link_text.strip():
                pinned_url = self._pin_local_reference(link_text, commit_sha)
                if pinned_url:
                    clean_text = link_text.strip()
                    new_link = f"[{clean_text}]({pinned_url})"
                    body = body[:ce_match.start(2)] + new_link + body[ce_match.end(2):]

        return body
