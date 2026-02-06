"""
aiv/lib/validators/anti_cheat.py

Anti-cheat detection for test modifications (Addendum 2.4).
"""

from __future__ import annotations

import re
from re import Pattern

from ..models import (
    AntiCheatFinding,
    AntiCheatResult,
    Claim,
    Severity,
)
from ..config import AntiCheatConfig


class AntiCheatScanner:
    """
    Scans git diffs for potential test manipulation.

    Detects:
    - Deleted assertions
    - Skipped tests
    - Mock/bypass flags
    - Relaxed conditions
    - Removed test files
    """

    def __init__(self, config: AntiCheatConfig | None = None):
        self.config = config or AntiCheatConfig()

        # Compile patterns
        self.test_file_patterns: list[Pattern[str]] = [
            re.compile(p) for p in self.config.test_file_patterns
        ]
        self.assertion_patterns: list[Pattern[str]] = [
            re.compile(p, re.IGNORECASE) for p in self.config.assertion_patterns
        ]
        self.skip_patterns: list[Pattern[str]] = [
            re.compile(p, re.IGNORECASE) for p in self.config.skip_patterns
        ]
        self.bypass_patterns: list[Pattern[str]] = [
            re.compile(p, re.IGNORECASE) for p in self.config.bypass_patterns
        ]

    def scan_diff(self, diff_text: str) -> AntiCheatResult:
        """
        Scan a unified diff for anti-cheat violations.

        Args:
            diff_text: Unified diff output (from git diff or GitHub API)

        Returns:
            AntiCheatResult with all findings
        """
        findings: list[AntiCheatFinding] = []
        files_analyzed = 0
        test_files_modified = 0

        # Parse diff into file chunks
        current_file: str | None = None
        current_line = 0

        for line in diff_text.split("\n"):
            # Detect file header
            if line.startswith("diff --git"):
                # Extract file path
                match = re.search(r"b/(.+)$", line)
                if match:
                    current_file = match.group(1)
                    files_analyzed += 1

                    if self._is_test_file(current_file):
                        test_files_modified += 1
                continue

            # Track line numbers
            if line.startswith("@@"):
                match = re.search(r"\+(\d+)", line)
                if match:
                    current_line = int(match.group(1))
                continue

            # Only analyze test files for assertion/skip patterns
            if current_file and self._is_test_file(current_file):

                # Check for deleted assertions (lines starting with -)
                if line.startswith("-"):
                    for pattern in self.assertion_patterns:
                        if pattern.search(line):
                            findings.append(AntiCheatFinding(
                                finding_type="deleted_assertion",
                                file_path=current_file,
                                line_number=current_line,
                                original_content=line[1:].strip(),
                                severity=Severity.BLOCK,
                                requires_justification=True,
                            ))
                            break

                # Check for added skip decorators
                if line.startswith("+"):
                    for pattern in self.skip_patterns:
                        if pattern.search(line):
                            findings.append(AntiCheatFinding(
                                finding_type="skipped_test",
                                file_path=current_file,
                                line_number=current_line,
                                original_content=line[1:].strip(),
                                severity=Severity.BLOCK,
                                requires_justification=True,
                            ))
                            break

            # Check for bypass patterns in any file
            if line.startswith("+"):
                for pattern in self.bypass_patterns:
                    if pattern.search(line):
                        findings.append(AntiCheatFinding(
                            finding_type="mock_bypass",
                            file_path=current_file or "unknown",
                            line_number=current_line,
                            original_content=line[1:].strip(),
                            severity=Severity.WARN,
                            requires_justification=True,
                        ))
                        break

            # Track line numbers for additions
            if line.startswith("+") and not line.startswith("+++"):
                current_line += 1
            elif not line.startswith("-") and not line.startswith("\\"):
                current_line += 1

        # Check for removed test files
        # In unified diffs, 'diff --git a/X b/X' comes BEFORE 'deleted file mode'.
        removed_files = re.findall(
            r"diff --git a/([^\s]+) b/[^\s]+\n(?:old|new|deleted|index|similarity|rename|copy)[^\n]*\ndeleted file mode \d+",
            diff_text,
        )
        for removed in removed_files:
            if self._is_test_file(removed):
                findings.append(AntiCheatFinding(
                    finding_type="removed_test_file",
                    file_path=removed,
                    line_number=None,
                    original_content=None,
                    severity=Severity.BLOCK,
                    requires_justification=True,
                ))

        return AntiCheatResult(
            findings=findings,
            files_analyzed=files_analyzed,
            test_files_modified=test_files_modified,
        )

    def _is_test_file(self, file_path: str) -> bool:
        """Check if a file path matches test file patterns."""
        for pattern in self.test_file_patterns:
            if pattern.search(file_path):
                return True
        return False

    def check_justification(
        self,
        result: AntiCheatResult,
        packet_claims: list[Claim]
    ) -> list[AntiCheatFinding]:
        """
        Cross-reference findings with packet claims to check for justification.

        Returns:
            List of findings that lack justification
        """
        unjustified: list[AntiCheatFinding] = []

        for finding in result.findings:
            if not finding.requires_justification:
                continue

            # Check if any Class F claim provides justification
            has_justification = False
            for claim in packet_claims:
                if claim.evidence_class.value == "F":
                    if claim.justification and len(claim.justification) > 20:
                        has_justification = True
                        break

            if not has_justification:
                unjustified.append(finding)

        return unjustified
