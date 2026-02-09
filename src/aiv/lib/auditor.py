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

Git-history audit (``audit_commits``):

- HOOK_BYPASS: Functional file committed without a paired verification packet.
- ATOMIC_VIOLATION: Commit contains more than 1 functional file + 1 packet.

Optionally auto-fixes COMMIT_PENDING and CLASS_E_NO_URL when --fix is used.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pathlib import Path

# Packet path patterns (mirrors pre_commit.py constants)
_PACKET_PREFIXES = (
    ".github/aiv-packets/VERIFICATION_PACKET_",
    ".github/VERIFICATION_PACKET_",
)
_PACKET_SUFFIX = ".md"

# Default functional prefixes (mirrors pre_commit.py defaults)
_FUNCTIONAL_PREFIXES = (
    "src/",
    "lib/",
    "app/",
    "pkg/",
    "cmd/",
    "internal/",
    "engine/",
    "infrastructure/",
    "scripts/",
    "tests/",
    ".github/workflows/",
    ".husky/",
)

_FUNCTIONAL_ROOT_FILES = {
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "package.json",
    "package-lock.json",
    ".gitignore",
    ".env.example",
}


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


def _is_bug_fix_claim(text: str) -> bool:
    """Heuristic: does claim text describe a bug fix (not a feature named 'fix')?

    Excludes:
    - ``auto-fix`` / ``auto fix`` (feature name)
    - ``--fix`` (CLI flag)
    - ```--fix```` (inline code CLI flag)
    """
    # Strip CLI flags and feature names before checking
    cleaned = re.sub(r"auto[- ]fix", "", text, flags=re.IGNORECASE)
    cleaned = re.sub(r"`?--fix`?", "", cleaned)
    cleaned = re.sub(r"bug[- ]fix\s+claim", "", cleaned, flags=re.IGNORECASE)
    return bool(
        re.search(
            r"\b(fix(?:ed|es|ing)?|bug(?:s|fix)?|resolve[ds]?|hotfix|patch(?:ed)?)\b",
            cleaned,
            re.IGNORECASE,
        )
    )


# Words in descriptions that *mention* the TODO system rather than *being* TODOs
_TODO_META_KEYWORDS = [
    "TODO-only",
    "_is_substantive",
    "placeholder",
    "PLACEHOLDER",
    "_PLACEHOLDER",
    "ALWAYS_PLACEHOLDER",
    "reject TODO",
    "strips TODO",
    "correctly rejected",
    "TODO/TBD",
    "TODO (always",
    "TODO from N/A",
    "scaffold",
    "substance check",
    "substance patch",
    "TODO remnant",
    "COMMIT_PENDING",
    "CLAIM_TODO",
    "SUMMARY_TODO",
    "CLASSIFIED_BY_TODO",
    "BLAST_RADIUS_TODO",
    "CLASS_A_TODO",
    "TODO_PRESENT",
    "finding type",
    "quality issue",
    "detects",
    "detection",
    "auto-fix",
    "auto-remediation",
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
        packets = sorted(p for p in packets_dir.glob("VERIFICATION_PACKET_*.md") if "TEMPLATE" not in p.name)

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
            findings.append(
                AuditFinding(
                    packet_name=name,
                    finding_type="COMMIT_PENDING",
                    severity=AuditSeverity.ERROR,
                    message="Commit SHA is still `pending` — no traceability.",
                    auto_fixable=commit_sha is not None,
                )
            )

        # 2. CLASS_E link checks
        ce_match = re.search(r"- \*\*Link:\*\*\s*(.*?)\n", body)
        if ce_match:
            link_text = ce_match.group(1).strip()
            if not link_text:
                findings.append(
                    AuditFinding(
                        packet_name=name,
                        finding_type="CLASS_E_EMPTY",
                        severity=AuditSeverity.ERROR,
                        message="Class E link is empty.",
                    )
                )
            elif "http" not in link_text:
                # TODO in Class E is an error, not a warning
                is_todo = bool(re.search(r"\bTODO\b", link_text, re.IGNORECASE))
                findings.append(
                    AuditFinding(
                        packet_name=name,
                        finding_type="CLASS_E_NO_URL",
                        severity=AuditSeverity.ERROR if is_todo else AuditSeverity.WARNING,
                        message=f"Class E link is {'TODO' if is_todo else 'plain text'}: {link_text[:80]}",
                        auto_fixable=self._can_pin_link(link_text),
                    )
                )
            elif "/blob/main/" in link_text or "/blob/master/" in link_text:
                findings.append(
                    AuditFinding(
                        packet_name=name,
                        finding_type="CLASS_E_MUTABLE",
                        severity=AuditSeverity.ERROR,
                        message="Class E link uses mutable branch (main/master).",
                    )
                )

        # 3. TODO remnants in content
        # TODOs in evidence sections are errors (they mean the evidence is missing).
        # TODOs in classification rationale are warnings (soft guidance).
        evidence_section = False
        for i, line in enumerate(body.split("\n"), 1):
            stripped = line.strip()
            if stripped.startswith("## Evidence"):
                evidence_section = True
            elif stripped.startswith("## ") and evidence_section:
                evidence_section = False
            if re.search(r"\bTODO\b", stripped, re.IGNORECASE):
                if any(kw in stripped for kw in _TODO_META_KEYWORDS):
                    continue
                # TODOs inside evidence sections are blocking errors
                sev = AuditSeverity.ERROR if evidence_section else AuditSeverity.WARNING
                findings.append(
                    AuditFinding(
                        packet_name=name,
                        finding_type="TODO_PRESENT",
                        severity=sev,
                        message=f"TODO on line {i}: {stripped[:80]}",
                        line_number=i,
                    )
                )

        # 4. classified_by still TODO
        if re.search(r'classified_by:\s*"TODO"', body):
            findings.append(
                AuditFinding(
                    packet_name=name,
                    finding_type="CLASSIFIED_BY_TODO",
                    severity=AuditSeverity.ERROR,
                    message="classified_by is still TODO.",
                    auto_fixable=False,
                )
            )

        # 5. blast_radius still TODO
        if re.search(r"blast_radius:\s*TODO\b", body):
            findings.append(
                AuditFinding(
                    packet_name=name,
                    finding_type="BLAST_RADIUS_TODO",
                    severity=AuditSeverity.ERROR,
                    message="blast_radius is still TODO.",
                    auto_fixable=False,
                )
            )

        # 6. Claims still TODO
        claims_match = re.search(r"## Claim\(s\)\s*\n(.*?)(?=---|\Z)", body, re.DOTALL)
        if claims_match:
            for cl_line in claims_match.group(1).split("\n"):
                if re.match(r"\s*\d+\.\s*TODO", cl_line):
                    findings.append(
                        AuditFinding(
                            packet_name=name,
                            finding_type="CLAIM_TODO",
                            severity=AuditSeverity.ERROR,
                            message=f"Claim is still TODO: {cl_line.strip()[:80]}",
                        )
                    )

        # 7. Summary still TODO
        summary_match = re.search(r"## Summary\s*\n(.*?)$", body, re.DOTALL)
        if summary_match:
            sm = summary_match.group(1).strip()
            if re.match(r"^TODO", sm, re.IGNORECASE):
                findings.append(
                    AuditFinding(
                        packet_name=name,
                        finding_type="SUMMARY_TODO",
                        severity=AuditSeverity.ERROR,
                        message="Summary section is still TODO.",
                    )
                )

        # 8. Fix claims without Class F
        if "### Class F" not in body and claims_match:
            claims_text = claims_match.group(1)
            if _is_bug_fix_claim(claims_text):
                findings.append(
                    AuditFinding(
                        packet_name=name,
                        finding_type="FIX_NO_CLASS_F",
                        severity=AuditSeverity.ERROR,
                        message="Claims mention fix/bug but packet has no Class F section.",
                    )
                )

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
                    body = body[: ce_match.start(2)] + new_link + body[ce_match.end(2) :]

        return body

    # ----- Git-history audit -----

    @staticmethod
    def _is_packet_path(path: str) -> bool:
        return (
            any(path.startswith(p) for p in _PACKET_PREFIXES)
            and path.endswith(_PACKET_SUFFIX)
        )

    @staticmethod
    def _is_functional_path(path: str) -> bool:
        if any(path.startswith(p) for p in _FUNCTIONAL_PREFIXES):
            return True
        return path in _FUNCTIONAL_ROOT_FILES

    def audit_commits(
        self,
        repo_root: Path,
        *,
        num_commits: int = 20,
    ) -> AuditResult:
        """Scan recent git commits for protocol violations.

        Detects:
        - HOOK_BYPASS: functional file(s) committed without a verification packet
        - ATOMIC_VIOLATION: commit has >1 functional file (multi-file bundle)
        """
        result = AuditResult()

        try:
            log_output = subprocess.run(
                ["git", "log", f"-{num_commits}", "--format=%H", "--name-only"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(repo_root),
            )
            if log_output.returncode != 0:
                return result
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return result

        # Parse git log output: SHA followed by file list, separated by blank lines
        commits: list[tuple[str, list[str]]] = []
        current_sha = ""
        current_files: list[str] = []
        for line in log_output.stdout.strip().split("\n"):
            line = line.strip()
            if not line:
                if current_sha and current_files:
                    commits.append((current_sha, current_files))
                    current_files = []
                continue
            if len(line) == 40 and all(c in "0123456789abcdef" for c in line):
                if current_sha and current_files:
                    commits.append((current_sha, current_files))
                    current_files = []
                current_sha = line
            else:
                current_files.append(line)
        if current_sha and current_files:
            commits.append((current_sha, current_files))

        result.packets_scanned = len(commits)

        for sha, files in commits:
            short = sha[:7]
            packets = [f for f in files if self._is_packet_path(f)]
            functional = [f for f in files if self._is_functional_path(f)]

            # Skip commits with no functional files (docs-only, etc.)
            if not functional:
                continue

            # HOOK_BYPASS: functional files but no packet
            if functional and not packets:
                result.findings.append(
                    AuditFinding(
                        packet_name=f"commit:{short}",
                        finding_type="HOOK_BYPASS",
                        severity=AuditSeverity.ERROR,
                        message=(
                            f"Commit {short} has {len(functional)} functional "
                            f"file(s) but no verification packet. "
                            f"Files: {', '.join(functional[:5])}"
                        ),
                    )
                )

            # ATOMIC_VIOLATION: more than 1 functional file in a commit
            if len(functional) > 1:
                result.findings.append(
                    AuditFinding(
                        packet_name=f"commit:{short}",
                        finding_type="ATOMIC_VIOLATION",
                        severity=AuditSeverity.WARNING,
                        message=(
                            f"Commit {short} bundles {len(functional)} "
                            f"functional files (atomic rule: max 1). "
                            f"Files: {', '.join(functional[:5])}"
                        ),
                    )
                )

        if result.findings:
            seen: set[str] = set()
            for f in result.findings:
                seen.add(f.packet_name)
            result.packets_with_issues = len(seen)

        return result
