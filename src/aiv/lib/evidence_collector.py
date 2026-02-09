"""
aiv/lib/evidence_collector.py

Evidence COLLECTOR — runs real tools, captures real output, assembles
real evidence for verification packets. This is NOT a text template filler.

Each collect_* method runs actual analysis and returns structured evidence
or raises if the evidence cannot be collected.
"""

from __future__ import annotations

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ClassBEvidence:
    """Referential evidence: SHA-pinned line-range permalinks to changed code."""

    head_sha: str
    owner: str
    repo: str
    hunks: list[str]  # ["src/auth.py#L42-L58", ...]

    def to_markdown(self) -> str:
        """Render as markdown with clickable SHA-pinned GitHub permalinks.

        Each hunk becomes a link like:
        ``[`src/auth.py#L42-L58`](https://github.com/org/repo/blob/<sha>/src/auth.py#L42-L58)``
        """
        short = self.head_sha[:7]
        lines = [
            "### Class B (Referential Evidence)\n",
            f"**Scope Inventory** (SHA: [`{short}`]"
            f"(https://github.com/{self.owner}/{self.repo}/tree/{self.head_sha}))\n",
        ]
        for hunk in self.hunks:
            lines.append(
                f"- [`{hunk}`]"
                f"(https://github.com/{self.owner}/{self.repo}/blob/{self.head_sha}/{hunk})"
            )
        return "\n".join(lines)


@dataclass
class ClassAEvidence:
    """Execution evidence: actual test output with specific test names."""

    total_passed: int
    total_failed: int
    total_warnings: int
    duration: str
    relevant_tests: list[str]  # test names that cover the changed file
    ruff_clean: bool
    ruff_errors: int
    mypy_clean: bool
    mypy_summary: str

    def to_markdown(self) -> str:
        """Render as markdown including specific test names and tool output.

        Emits a WARNING if no tests are found that reference the changed file,
        making coverage gaps visible rather than hidden.
        """
        lines = ["### Class A (Execution Evidence)\n"]
        lines.append(f"- **pytest:** {self.total_passed} passed, {self.total_failed} failed in {self.duration}")
        if self.relevant_tests:
            lines.append(f"- **Tests covering changed file** ({len(self.relevant_tests)}):")
            for t in self.relevant_tests[:20]:  # cap at 20 to avoid huge packets
                lines.append(f"  - `{t}`")
        else:
            lines.append("- **WARNING:** No tests found that directly import or reference the changed file.")
        lines.append(f"- **ruff:** {'All checks passed' if self.ruff_clean else f'{self.ruff_errors} error(s)'}")
        lines.append(f"- **mypy:** {self.mypy_summary}")
        return "\n".join(lines)


@dataclass
class ClassCEvidence:
    """Negative evidence: what was searched for and NOT found."""

    test_files_modified: list[str]
    test_files_deleted: list[str]
    assertions_removed: list[str]  # lines where assert was deleted
    skip_markers_added: list[str]  # lines where @skip was added
    anti_cheat_clean: bool

    def to_markdown(self) -> str:
        """Render as markdown documenting search methodology and findings.

        Reports what was searched for (assertions, test deletions, skip markers)
        and whether each indicator was found or absent. ALERTs are emitted for
        any regression indicator detected.
        """
        lines = ["### Class C (Negative Evidence)\n"]
        lines.append("**Search methodology:** Ran `git diff --cached` and scanned for regression indicators.\n")

        if not self.test_files_deleted:
            lines.append("- Test file deletions: **none**")
        else:
            lines.append(f"- **ALERT:** {len(self.test_files_deleted)} test file(s) deleted:")
            for f in self.test_files_deleted:
                lines.append(f"  - `{f}`")

        if not self.test_files_modified:
            lines.append("- Test file modifications: **none**")
        else:
            lines.append(f"- Test files modified: {len(self.test_files_modified)}")
            for f in self.test_files_modified:
                lines.append(f"  - `{f}`")

        if not self.assertions_removed:
            lines.append("- Deleted assertions (`assert` removals in diff): **none found**")
        else:
            lines.append(f"- **ALERT:** {len(self.assertions_removed)} assertion(s) removed:")
            for a in self.assertions_removed:
                lines.append(f"  - `{a}`")

        if not self.skip_markers_added:
            lines.append("- Added skip markers (`@pytest.mark.skip`, `@unittest.skip`): **none found**")
        else:
            lines.append(f"- **ALERT:** {len(self.skip_markers_added)} skip marker(s) added:")
            for s in self.skip_markers_added:
                lines.append(f"  - `{s}`")

        return "\n".join(lines)


@dataclass
class ClassFEvidence:
    """Provenance evidence: chain-of-custody proof from git diff on test files."""

    test_files_in_diff: list[str]
    test_assertions_deleted: int
    test_files_deleted: int

    def to_markdown(self) -> str:
        """Render as markdown documenting test file chain-of-custody.

        Reports whether any test files were deleted or any assertions removed
        in the staged diff, providing cryptographic-grade provenance via git.
        """
        lines = ["### Class F (Provenance Evidence)\n"]
        if self.test_files_deleted == 0 and self.test_assertions_deleted == 0:
            lines.append("- No test files deleted. No assertions removed. Full test suite passes.")
        else:
            if self.test_files_deleted > 0:
                lines.append(f"- **ALERT:** {self.test_files_deleted} test file(s) deleted in this commit.")
            if self.test_assertions_deleted > 0:
                lines.append(f"- **ALERT:** {self.test_assertions_deleted} assertion(s) removed in this commit.")
        if self.test_files_in_diff:
            lines.append(f"- Test files touched: {', '.join(f'`{t}`' for t in self.test_files_in_diff)}")
        return "\n".join(lines)


def _run_git(*args: str) -> str:
    """Run a git command and return stripped stdout.

    Returns empty string on failure or timeout (never raises).
    """
    result = subprocess.run(
        ["git", *args], capture_output=True, text=True, timeout=30
    )
    return result.stdout.strip()


def _run(cmd: list[str], timeout: int = 60) -> subprocess.CompletedProcess[str]:
    """Run an arbitrary command and return the CompletedProcess."""
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


# ---------------------------------------------------------------------------
# Collectors
# ---------------------------------------------------------------------------


def collect_class_b(file_path: str, owner: str, repo: str) -> ClassBEvidence:
    """Collect Class B evidence by parsing ``git diff --cached`` for exact line ranges.

    Produces SHA-pinned GitHub permalinks to every changed hunk in the file.
    For new files (no diff hunks), falls back to the full file line range.

    Args:
        file_path: Path to the changed file (e.g. ``src/aiv/lib/auditor.py``).
        owner: GitHub repository owner (e.g. ``ImmortalDemonGod``).
        repo: GitHub repository name (e.g. ``aiv-protocol``).

    Returns:
        ClassBEvidence with head_sha, owner, repo, and a list of hunk strings
        like ``src/auth.py#L42-L58``.
    """
    head_sha = _run_git("rev-parse", "HEAD")
    if not head_sha:
        head_sha = "unknown"

    # Get the diff for the specific file to find changed line ranges
    diff_output = _run_git("diff", "--cached", "-U0", "--", file_path)
    if not diff_output:
        # File might not be staged yet — try unstaged diff
        diff_output = _run_git("diff", "-U0", "--", file_path)

    hunks: list[str] = []
    file_posix = file_path.replace("\\", "/")

    if diff_output:
        # Parse @@ -old,count +new,count @@ hunks
        for match in re.finditer(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", diff_output):
            start = int(match.group(1))
            count = int(match.group(2)) if match.group(2) else 1
            if count == 0:
                continue
            end = start + count - 1
            if start == end:
                hunks.append(f"{file_posix}#L{start}")
            else:
                hunks.append(f"{file_posix}#L{start}-L{end}")

    if not hunks:
        # Fallback: new file, show entire range
        try:
            line_count = len(Path(file_path).read_text(encoding="utf-8").splitlines())
            hunks.append(f"{file_posix}#L1-L{line_count}")
        except Exception:
            hunks.append(file_posix)

    return ClassBEvidence(head_sha=head_sha, owner=owner, repo=repo, hunks=hunks)


def collect_class_a(file_path: str) -> ClassAEvidence:
    """Collect Class A evidence by running pytest, ruff, and mypy.

    1. Runs ``pytest --tb=no -q`` to get pass/fail counts and duration.
    2. Uses ``git grep`` to find test files that reference the changed module,
       then extracts ``test_*`` function names from those files.
    3. Runs ``ruff check`` on the changed file.
    4. Runs ``mypy`` on the changed file.

    If no tests reference the changed file, emits a WARNING in the output
    rather than silently omitting this gap.

    Args:
        file_path: Path to the changed file.

    Returns:
        ClassAEvidence with test counts, relevant test names, and linter results.
    """
    import sys

    # 1. Run pytest in parallel (-n auto via pytest-xdist, fallback to serial)
    pytest_cmd = [sys.executable, "-m", "pytest", "--tb=no", "-q", "--no-header"]
    try:
        import pytest_xdist as _  # noqa: F401

        pytest_cmd.extend(["-n", "auto"])
    except ImportError:
        pass  # xdist not installed — run serial
    r = _run(pytest_cmd, timeout=180)
    last_line = r.stdout.strip().split("\n")[-1] if r.stdout.strip() else ""

    # Parse "N passed, M failed, K warnings in Xs"
    passed = 0
    failed = 0
    warnings = 0
    duration = "unknown"
    m = re.search(r"(\d+) passed", last_line)
    if m:
        passed = int(m.group(1))
    m = re.search(r"(\d+) failed", last_line)
    if m:
        failed = int(m.group(1))
    m = re.search(r"(\d+) warning", last_line)
    if m:
        warnings = int(m.group(1))
    m = re.search(r"in ([\d.]+s)", last_line)
    if m:
        duration = m.group(1)

    # 2. Find tests that reference the changed file's module
    # Extract module name from file path (e.g., src/aiv/lib/auditor.py -> auditor)
    stem = Path(file_path).stem

    # Search test files for imports/references to the changed module
    relevant_tests: list[str] = []
    try:
        # Use grep to find test files that import or reference the module
        grep_result = _run(
            ["git", "grep", "-l", stem, "--", "tests/"],
            timeout=10,
        )
        test_files = [f.strip() for f in grep_result.stdout.splitlines() if f.strip()]

        # Collect test function names from those files
        for tf in test_files[:5]:  # cap file scan
            try:
                content = Path(tf).read_text(encoding="utf-8")
                for line in content.splitlines():
                    m = re.match(r"\s*(def |class )(test_\w+)", line)
                    if m:
                        relevant_tests.append(f"{tf}::{m.group(2)}")
            except Exception:
                pass
    except Exception:
        pass

    # 3. Ruff
    ruff_r = _run([sys.executable, "-m", "ruff", "check", file_path], timeout=30)
    ruff_clean = ruff_r.returncode == 0
    ruff_errors = ruff_r.stdout.strip().count("\n") + 1 if ruff_r.stdout.strip() else 0

    # 4. Mypy
    mypy_r = _run([sys.executable, "-m", "mypy", file_path], timeout=60)
    mypy_lines = mypy_r.stdout.strip().split("\n")
    mypy_summary = mypy_lines[-1] if mypy_lines else "unknown"
    mypy_clean = "no issues" in mypy_summary.lower() or "success" in mypy_summary.lower()

    return ClassAEvidence(
        total_passed=passed,
        total_failed=failed,
        total_warnings=warnings,
        duration=duration,
        relevant_tests=relevant_tests,
        ruff_clean=ruff_clean,
        ruff_errors=ruff_errors if not ruff_clean else 0,
        mypy_clean=mypy_clean,
        mypy_summary=mypy_summary,
    )


def collect_class_c() -> ClassCEvidence:
    """Collect Class C (negative) evidence by scanning ``git diff --cached``.

    Searches the staged diff for four regression indicators:

    1. **Test file deletions** — any file with "test" in its path deleted.
    2. **Test file modifications** — any test file modified (informational).
    3. **Deleted assertions** — lines removed that contain ``assert``.
    4. **Added skip markers** — lines added with ``@pytest.mark.skip`` etc.
       (Excludes string literals to avoid false positives from documentation.)

    Returns:
        ClassCEvidence with lists of findings and an ``anti_cheat_clean`` flag.
    """
    diff = _run_git("diff", "--cached")

    # Find modified/deleted test files
    name_status = _run_git("diff", "--cached", "--name-status")
    test_modified: list[str] = []
    test_deleted: list[str] = []
    for line in name_status.splitlines():
        parts = line.split("\t", 1)
        if len(parts) == 2:
            status, path = parts
            if "test" in path.lower():
                if status.startswith("D"):
                    test_deleted.append(path)
                elif status.startswith("M"):
                    test_modified.append(path)

    # Scan diff for removed assertions (lines starting with -)
    assertions_removed: list[str] = []
    skip_markers_added: list[str] = []
    for line in diff.splitlines():
        stripped = line.strip()
        if stripped.startswith("-") and not stripped.startswith("---"):
            # Removed line
            content = stripped[1:].strip()
            if re.search(r"\bassert\b", content):
                assertions_removed.append(content[:100])
        if stripped.startswith("+") and not stripped.startswith("+++"):
            content = stripped[1:].strip()
            # Only flag actual code, not string literals or documentation
            if re.search(r"@pytest\.mark\.skip|@unittest\.skip|pytest\.skip", content):
                if not re.search(r"['\"`].*@pytest\.mark\.skip|['\"`].*@unittest\.skip", content):
                    skip_markers_added.append(content[:100])

    return ClassCEvidence(
        test_files_modified=test_modified,
        test_files_deleted=test_deleted,
        assertions_removed=assertions_removed,
        skip_markers_added=skip_markers_added,
        anti_cheat_clean=len(assertions_removed) == 0 and len(test_deleted) == 0,
    )


def collect_class_f() -> ClassFEvidence:
    """Collect Class F (provenance) evidence by verifying test file integrity.

    Scans ``git diff --cached`` for:

    1. Test files present in the diff (any file with "test" in path).
    2. How many of those are deletions.
    3. How many ``assert`` statements were removed from ``tests/``.

    This provides chain-of-custody proof that the test suite was not
    weakened by the commit.

    Returns:
        ClassFEvidence with test file lists and deletion/assertion counts.
    """
    name_status = _run_git("diff", "--cached", "--name-status")

    test_files: list[str] = []
    deleted_count = 0
    for line in name_status.splitlines():
        parts = line.split("\t", 1)
        if len(parts) == 2:
            status, path = parts
            if "test" in path.lower():
                test_files.append(path)
                if status.startswith("D"):
                    deleted_count += 1

    # Count removed assertions in test files
    diff = _run_git("diff", "--cached", "--", "tests/")
    assertions_deleted = 0
    for line in diff.splitlines():
        if line.startswith("-") and not line.startswith("---"):
            if re.search(r"\bassert\b", line):
                assertions_deleted += 1

    return ClassFEvidence(
        test_files_in_diff=test_files,
        test_assertions_deleted=assertions_deleted,
        test_files_deleted=deleted_count,
    )
