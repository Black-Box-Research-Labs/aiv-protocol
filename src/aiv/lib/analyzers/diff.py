"""
aiv/lib/analyzers/diff.py

Git diff analysis utilities.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class DiffFile:
    """Represents a single file in a diff."""
    path: str
    status: str  # "added", "modified", "deleted", "renamed"
    additions: int = 0
    deletions: int = 0
    old_path: str | None = None  # For renames


@dataclass
class DiffAnalysis:
    """Complete analysis of a git diff."""
    files: list[DiffFile] = field(default_factory=list)
    total_additions: int = 0
    total_deletions: int = 0

    @property
    def file_paths(self) -> list[str]:
        """Get all file paths in the diff."""
        return [f.path for f in self.files]

    @property
    def added_files(self) -> list[DiffFile]:
        """Get files that were added."""
        return [f for f in self.files if f.status == "added"]

    @property
    def modified_files(self) -> list[DiffFile]:
        """Get files that were modified."""
        return [f for f in self.files if f.status == "modified"]

    @property
    def deleted_files(self) -> list[DiffFile]:
        """Get files that were deleted."""
        return [f for f in self.files if f.status == "deleted"]


class DiffAnalyzer:
    """
    Analyzes unified diff output to extract file-level statistics.

    Used for:
    - Scope inventory validation (comparing packet claims to actual changes)
    - Risk tier auto-detection (identifying critical surface files)
    - Fast-track eligibility checking (all files are docs-only)
    """

    # Patterns for critical surface detection
    CRITICAL_SURFACE_PATTERNS = [
        (r"auth", "authentication"),
        (r"crypto|encrypt|decrypt|hash|sign|verify", "cryptography"),
        (r"payment|billing|charge|invoice", "payments"),
        (r"pii|personal|gdpr|privacy|ssn|email.*address", "PII"),
        (r"audit|log.*event|compliance", "audit-logging"),
        (r"secret|api.?key|token|credential|password", "secrets"),
    ]

    def analyze(self, diff_text: str) -> DiffAnalysis:
        """
        Parse a unified diff into structured analysis.

        Args:
            diff_text: Unified diff output (git diff or GitHub API)

        Returns:
            DiffAnalysis with file-level statistics
        """
        files: list[DiffFile] = []
        current_file: DiffFile | None = None
        total_add = 0
        total_del = 0

        for line in diff_text.split("\n"):
            # Detect file header
            if line.startswith("diff --git"):
                # Save previous file
                if current_file:
                    files.append(current_file)

                # Extract paths
                match = re.search(r"a/(.+?) b/(.+)$", line)
                if match:
                    old_path = match.group(1)
                    new_path = match.group(2)
                    current_file = DiffFile(
                        path=new_path,
                        status="modified",
                        old_path=old_path if old_path != new_path else None,
                    )
                continue

            # Detect file status markers
            if current_file:
                if line.startswith("new file mode"):
                    current_file.status = "added"
                elif line.startswith("deleted file mode"):
                    current_file.status = "deleted"
                elif line.startswith("rename from"):
                    current_file.status = "renamed"
                    current_file.old_path = line.split("rename from ")[-1].strip()

            # Count additions/deletions
            if line.startswith("+") and not line.startswith("+++"):
                if current_file:
                    current_file.additions += 1
                total_add += 1
            elif line.startswith("-") and not line.startswith("---"):
                if current_file:
                    current_file.deletions += 1
                total_del += 1

        # Save last file
        if current_file:
            files.append(current_file)

        return DiffAnalysis(
            files=files,
            total_additions=total_add,
            total_deletions=total_del,
        )

    def detect_critical_surfaces(self, diff_text: str) -> list[tuple[str, str]]:
        """
        Detect critical surfaces touched by the diff.

        Returns:
            List of (file_path, surface_type) tuples
        """
        analysis = self.analyze(diff_text)
        critical: list[tuple[str, str]] = []

        for diff_file in analysis.files:
            for pattern, surface_type in self.CRITICAL_SURFACE_PATTERNS:
                if re.search(pattern, diff_file.path, re.IGNORECASE):
                    critical.append((diff_file.path, surface_type))
                    break

        # Also check diff content for critical patterns
        for pattern, surface_type in self.CRITICAL_SURFACE_PATTERNS:
            for line in diff_text.split("\n"):
                if line.startswith("+") and not line.startswith("+++"):
                    if re.search(pattern, line, re.IGNORECASE):
                        # Find which file this belongs to
                        # (simplified — uses last seen file)
                        if analysis.files:
                            last_file = analysis.files[-1].path
                            pair = (last_file, surface_type)
                            if pair not in critical:
                                critical.append(pair)
                        break

        return critical
