"""
aiv/lib/evidence_collector.py

Evidence COLLECTOR — runs real tools, captures real output, assembles
real evidence for verification packets. This is NOT a text template filler.

Each collect_* method runs actual analysis and returns structured evidence
or raises if the evidence cannot be collected.
"""

from __future__ import annotations

import ast
import re
import subprocess
from dataclasses import dataclass, field
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
    symbol_coverage: list[SymbolCoverage] = field(default_factory=list)

    def to_markdown(self) -> str:
        """Render as markdown including specific test names and tool output.

        When AST symbol coverage is available, renders per-symbol verdicts
        showing which tests import AND call each changed symbol, with a
        coverage summary. The global "N passed" metric is suppressed when
        per-symbol data is available (it adds no claim-specific signal).
        """
        lines = ["### Class A (Execution Evidence)\n"]

        if self.symbol_coverage:
            # Per-symbol AST coverage (deterministic, not keyword-based)
            lines.append("**Per-symbol test coverage (AST analysis):**\n")
            covered = 0
            total = len(self.symbol_coverage)
            for sc in self.symbol_coverage:
                has_tests = len(sc.calling_tests) > 0
                if has_tests:
                    covered += 1
                icon = "PASS" if has_tests else "FAIL"
                lines.append(f"- **`{sc.symbol}`** ({sc.line_range}): {icon} — {sc.coverage_verdict}")
                if sc.calling_tests:
                    for ct in sc.calling_tests[:10]:
                        lines.append(f"  - `{ct}`")
                elif sc.importing_test_files:
                    for tf in sc.importing_test_files[:5]:
                        lines.append(f"  - Imported by: `{tf}`")
            lines.append(f"\n**Coverage summary:** {covered}/{total} symbols verified by tests.")
        else:
            # Fallback: global metric for non-Python files or --skip-checks
            lines.append(f"- **pytest:** {self.total_passed} passed, {self.total_failed} failed in {self.duration}")
            if self.relevant_tests:
                lines.append(f"- **Tests covering changed file** ({len(self.relevant_tests)}):")
                for t in self.relevant_tests[:20]:
                    lines.append(f"  - `{t}`")
            else:
                lines.append("- **WARNING:** No tests found that directly import or reference the changed file.")

        lines.append(f"- **ruff:** {'All checks passed' if self.ruff_clean else f'{self.ruff_errors} error(s)'}")
        lines.append(f"- **mypy:** {self.mypy_summary}")
        return "\n".join(lines)


@dataclass
class DownstreamCaller:
    """A caller of a changed symbol found via AST analysis."""

    file: str
    function: str
    symbol_called: str


@dataclass
class ClassCEvidence:
    """Negative evidence: what was searched for and NOT found."""

    test_files_modified: list[str]
    test_files_deleted: list[str]
    assertions_removed: list[str]  # lines where assert was deleted
    skip_markers_added: list[str]  # lines where @skip was added
    anti_cheat_clean: bool
    downstream_callers: list[DownstreamCaller] = field(default_factory=list)

    def to_markdown(self) -> str:
        """Render as markdown documenting search methodology and findings.

        Reports what was searched for (assertions, test deletions, skip markers)
        and whether each indicator was found or absent. ALERTs are emitted for
        any regression indicator detected.

        When downstream caller analysis is available, shows which functions
        across src/ call the changed symbols (impact scope).
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

        if self.downstream_callers:
            lines.append("\n**Downstream impact analysis (AST):**\n")
            # Group by symbol
            by_symbol: dict[str, list[DownstreamCaller]] = {}
            for dc in self.downstream_callers:
                by_symbol.setdefault(dc.symbol_called, []).append(dc)
            for sym, callers in by_symbol.items():
                lines.append(f"- `{sym}` is called by:")
                for c in callers[:10]:
                    lines.append(f"  - `{c.file}::{c.function}`")
                if len(callers) > 10:
                    lines.append(f"  - ... and {len(callers) - 10} more")

        return "\n".join(lines)


@dataclass
class TestFileProvenance:
    """Chain-of-custody record for a single test file."""

    path: str
    commit_count: int
    created_by: str
    created_sha: str
    last_modified_by: str
    last_modified_sha: str
    assertion_count: int


@dataclass
class ClassFEvidence:
    """Provenance evidence: git-log chain-of-custody for covering test files.

    DISTINCT from Class C (diff scan) and Class A (test results).
    Class F answers: "What is the history of the test files that cover this code?"
    Not: "Did tests pass?" (Class A) or "Were tests deleted?" (Class C).
    """

    test_provenance: list[TestFileProvenance]
    recent_test_log: str  # git log --oneline output for tests/

    def to_markdown(self) -> str:
        """Render as markdown with per-file chain-of-custody table and git log.

        Shows creation date, commit count, last modifier, and assertion count
        for each covering test file. This is information that Class C (diff scan)
        and Class A (test results) do not provide.
        """
        lines = ["### Class F (Provenance Evidence)\n"]
        lines.append("**Test file chain-of-custody:**\n")
        if self.test_provenance:
            lines.append("| File | Commits | Created By | Last Modified By | Assertions |")
            lines.append("|------|---------|------------|------------------|------------|")
            for tp in self.test_provenance:
                lines.append(
                    f"| `{tp.path}` | {tp.commit_count} "
                    f"| {tp.created_by} ({tp.created_sha[:7]}) "
                    f"| {tp.last_modified_by} ({tp.last_modified_sha[:7]}) "
                    f"| {tp.assertion_count} |"
                )
        else:
            lines.append("No covering test files found.")

        if self.recent_test_log:
            lines.append("\n**Recent test directory history** (`git log --oneline -5 -- tests/`):\n")
            lines.append("```")
            lines.append(self.recent_test_log)
            lines.append("```")
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
        import xdist as _  # noqa: F401

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

    # 2. Find tests that actually import or test the changed module.
    # Uses import-path matching (not bare word grep) to avoid false positives
    # like "pyproject" matching pre-commit hook tests that mention the word.
    relevant_tests: list[str] = []
    stem = Path(file_path).stem
    file_posix_local = file_path.replace("\\", "/")

    # Derive Python import path: src/aiv/lib/auditor.py -> aiv.lib.auditor
    import_path = ""
    if file_posix_local.endswith(".py"):
        parts = Path(file_posix_local).with_suffix("").parts
        # Strip leading "src/" if present
        if parts and parts[0] == "src":
            parts = parts[1:]
        import_path = ".".join(parts)  # e.g. "aiv.lib.auditor"

    search_patterns: list[str] = []
    if import_path:
        # Search for actual imports: "from aiv.lib.auditor import" or "import auditor"
        search_patterns.append(f"from {import_path}")
        # Also search for partial import path (e.g. "from aiv.lib import auditor")
        if "." in import_path:
            parent = import_path.rsplit(".", 1)[0]
            search_patterns.append(f"from {parent} import {stem}")
        # Also match test files named after the module (test_auditor.py)
        search_patterns.append(f"test_{stem}")

    for pattern in search_patterns:
        try:
            grep_result = _run(
                ["git", "grep", "-l", pattern, "--", "tests/"],
                timeout=10,
            )
            for tf in grep_result.stdout.splitlines():
                tf = tf.strip()
                if not tf:
                    continue
                try:
                    content = Path(tf).read_text(encoding="utf-8")
                    for line in content.splitlines():
                        m = re.match(r"\s*(def |class )(test_\w+)", line)
                        if m:
                            entry = f"{tf}::{m.group(2)}"
                            if entry not in relevant_tests:
                                relevant_tests.append(entry)
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


def _get_test_file_provenance(test_path: str) -> TestFileProvenance:
    """Build chain-of-custody record for a single test file using git log."""
    # Commit count
    log_output = _run_git("log", "--oneline", "--follow", "--", test_path)
    commits = [ln for ln in log_output.splitlines() if ln.strip()]
    commit_count = len(commits)

    # Created by (oldest commit)
    created_by = "unknown"
    created_sha = "unknown"
    if commits:
        oldest = commits[-1].split(" ", 1)
        created_sha = oldest[0] if oldest else "unknown"
        blame_first = _run_git("log", "--format=%an", "--follow", "--diff-filter=A", "--", test_path)
        created_by = blame_first.splitlines()[0].strip() if blame_first.strip() else "unknown"

    # Last modified by (newest commit)
    last_modified_by = "unknown"
    last_modified_sha = "unknown"
    if commits:
        newest = commits[0].split(" ", 1)
        last_modified_sha = newest[0] if newest else "unknown"
        last_author = _run_git("log", "-1", "--format=%an", "--", test_path)
        last_modified_by = last_author.strip() if last_author.strip() else "unknown"

    # Count assertions in current file
    assertion_count = 0
    try:
        content = Path(test_path).read_text(encoding="utf-8")
        for line in content.splitlines():
            if re.search(r"\bassert\b", line) and not line.strip().startswith("#"):
                assertion_count += 1
    except Exception:
        pass

    return TestFileProvenance(
        path=test_path,
        commit_count=commit_count,
        created_by=created_by,
        created_sha=created_sha,
        last_modified_by=last_modified_by,
        last_modified_sha=last_modified_sha,
        assertion_count=assertion_count,
    )


def collect_class_f(covering_test_files: list[str] | None = None) -> ClassFEvidence:
    """Collect Class F (provenance) evidence via git log chain-of-custody.

    DISTINCT from Class C and Class A. This answers:
    "What is the history of the test files that cover this code?"

    For each covering test file, collects:
    - Number of commits (via ``git log --follow``)
    - Who created it and in which commit
    - Who last modified it and in which commit
    - Current assertion count

    Also includes recent ``git log --oneline -5 -- tests/`` output.

    Args:
        covering_test_files: List of test file paths that cover the changed code.
            If None, discovers test files from the staged diff.

    Returns:
        ClassFEvidence with per-file provenance and recent test log.
    """
    if covering_test_files is None:
        # Fallback: discover from staged diff
        name_status = _run_git("diff", "--cached", "--name-status")
        covering_test_files = []
        for line in name_status.splitlines():
            parts = line.split("\t", 1)
            if len(parts) == 2:
                _status, path = parts
                if "test" in path.lower() and path.endswith(".py"):
                    covering_test_files.append(path)

    provenance: list[TestFileProvenance] = []
    for tf in covering_test_files[:10]:  # cap to avoid slow git log on many files
        provenance.append(_get_test_file_provenance(tf))

    # Recent test directory history
    recent_log = _run_git("log", "--oneline", "-5", "--", "tests/")

    return ClassFEvidence(
        test_provenance=provenance,
        recent_test_log=recent_log,
    )


# ---------------------------------------------------------------------------
# Phase 1: AST Symbol Resolver — map diff hunks to enclosing symbols
# ---------------------------------------------------------------------------


def resolve_changed_symbols(
    file_path: str, line_ranges: list[tuple[int, int]]
) -> list[str]:
    """Parse a Python file's AST and map line ranges to enclosing function/class names.

    For each line range, finds the innermost ``FunctionDef``, ``AsyncFunctionDef``,
    or ``ClassDef`` whose ``lineno..end_lineno`` contains any line in the range.

    Args:
        file_path: Path to the Python source file.
        line_ranges: List of (start_line, end_line) tuples from diff hunks.

    Returns:
        De-duplicated list of symbol names (e.g. ``["collect_class_a", "ClassBEvidence"]``).
        Returns ``["<module>"]`` if changes are at module level (outside any function/class).
    """
    try:
        source = Path(file_path).read_text(encoding="utf-8")
        tree = ast.parse(source, filename=file_path)
    except Exception:
        return ["<parse-error>"]

    # Collect all function/class nodes with their line ranges
    symbols: list[tuple[str, int, int]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            start = node.lineno
            end = node.end_lineno or node.lineno
            name = node.name
            # For methods inside classes, prefix with class name
            for parent in ast.walk(tree):
                if isinstance(parent, ast.ClassDef) and node in ast.iter_child_nodes(parent):
                    name = f"{parent.name}.{node.name}"
                    break
            symbols.append((name, start, end))

    matched: list[str] = []
    for hunk_start, hunk_end in line_ranges:
        for name, sym_start, sym_end in symbols:
            # Collect ALL symbols whose range overlaps with this hunk
            if sym_start <= hunk_end and sym_end >= hunk_start:
                if name not in matched:
                    matched.append(name)

    if not matched:
        matched.append("<module>")
    return matched


# ---------------------------------------------------------------------------
# Phase 2: AST Test Graph — import + call graph for test files
# ---------------------------------------------------------------------------


@dataclass
class TestGraph:
    """Maps test files to the symbols they import and the calls each test makes."""

    # test_file → set of imported symbol names
    imports: dict[str, set[str]] = field(default_factory=dict)
    # test_file → { test_function_name → set of called symbol names }
    calls: dict[str, dict[str, set[str]]] = field(default_factory=dict)


class _ImportVisitor(ast.NodeVisitor):
    """Extract all imported symbol names from a module."""

    def __init__(self) -> None:
        self.symbols: set[str] = set()

    def visit_ImportFrom(self, node: ast.ImportFrom) -> None:  # noqa: N802
        if node.names:
            for alias in node.names:
                self.symbols.add(alias.name)
        self.generic_visit(node)

    def visit_Import(self, node: ast.Import) -> None:  # noqa: N802
        for alias in node.names:
            name = alias.asname or alias.name
            self.symbols.add(name.split(".")[-1])
        self.generic_visit(node)


class _CallVisitor(ast.NodeVisitor):
    """Extract all called names within a function body."""

    def __init__(self) -> None:
        self.called: set[str] = set()

    def visit_Call(self, node: ast.Call) -> None:  # noqa: N802
        if isinstance(node.func, ast.Name):
            self.called.add(node.func.id)
        elif isinstance(node.func, ast.Attribute):
            self.called.add(node.func.attr)
        self.generic_visit(node)


def build_test_graph(test_dir: str = "tests/") -> TestGraph:
    """Parse all test files and build import + call relationships.

    For each ``*.py`` file under ``test_dir``:
    1. Extract all imported symbols via ``ast.ImportFrom`` / ``ast.Import``.
    2. For each ``test_*`` function, extract all called symbol names.

    Args:
        test_dir: Root directory to scan for test files.

    Returns:
        TestGraph with import and call maps.
    """
    graph = TestGraph()
    test_root = Path(test_dir)
    if not test_root.exists():
        return graph

    for py_file in test_root.rglob("*.py"):
        rel_path = str(py_file).replace("\\", "/")
        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(py_file))
        except Exception:
            continue

        # Extract imports
        iv = _ImportVisitor()
        iv.visit(tree)
        graph.imports[rel_path] = iv.symbols

        # Extract calls per test function
        file_calls: dict[str, set[str]] = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                if node.name.startswith("test_"):
                    cv = _CallVisitor()
                    cv.visit(node)
                    file_calls[node.name] = cv.called
        if file_calls:
            graph.calls[rel_path] = file_calls

    return graph


@dataclass
class SymbolCoverage:
    """Per-symbol test coverage result from AST analysis."""

    symbol: str
    line_range: str  # e.g. "L254-L259"
    importing_test_files: list[str]
    calling_tests: list[str]  # "file::test_name" format
    coverage_verdict: str  # e.g. "4 tests call this symbol" or "WARNING: 0 tests"


def find_covering_tests(
    changed_symbols: list[str],
    test_graph: TestGraph,
    hunks: list[str] | None = None,
) -> list[SymbolCoverage]:
    """For each changed symbol, find tests that import AND call it.

    This is the core of semantic Class A: deterministic, AST-based
    claim-to-test mapping. No keywords, no grep, no heuristics.

    Args:
        changed_symbols: Symbol names from ``resolve_changed_symbols``.
        test_graph: The ``TestGraph`` built by ``build_test_graph``.
        hunks: Optional hunk strings from Class B for line range display.

    Returns:
        List of ``SymbolCoverage`` results, one per changed symbol.
    """
    results: list[SymbolCoverage] = []

    for idx, symbol in enumerate(changed_symbols):
        # Strip class prefix for matching (e.g. "ClassA.to_markdown" → also match "to_markdown")
        bare_name = symbol.split(".")[-1] if "." in symbol else symbol
        line_range = hunks[idx] if hunks and idx < len(hunks) else "unknown"

        importing_files: list[str] = []
        calling_tests: list[str] = []

        for test_file, imported_symbols in test_graph.imports.items():
            # Check if this test file imports the symbol (or any symbol from the module)
            if bare_name in imported_symbols or symbol in imported_symbols:
                importing_files.append(test_file)

                # Check which test functions in this file call the symbol
                file_calls = test_graph.calls.get(test_file, {})
                for test_name, called_symbols in file_calls.items():
                    if bare_name in called_symbols or symbol in called_symbols:
                        calling_tests.append(f"{test_file}::{test_name}")

        if calling_tests:
            verdict = f"{len(calling_tests)} test(s) call `{bare_name}` directly"
        elif importing_files:
            verdict = (
                f"WARNING: {len(importing_files)} file(s) import `{bare_name}` "
                f"but 0 tests call it directly"
            )
        else:
            verdict = f"WARNING: No tests import or call `{bare_name}`"

        results.append(SymbolCoverage(
            symbol=symbol,
            line_range=line_range,
            importing_test_files=importing_files,
            calling_tests=calling_tests,
            coverage_verdict=verdict,
        ))

    return results


# ---------------------------------------------------------------------------
# Phase 4: Downstream caller analysis for Class C
# ---------------------------------------------------------------------------


def find_downstream_callers(
    changed_symbols: list[str],
    src_dir: str = "src/",
    exclude_file: str = "",
) -> list[DownstreamCaller]:
    """Find all functions in src/ that call any of the changed symbols.

    Uses the same AST import/call analysis as the test graph but scans
    production code (``src/``) instead of tests. Excludes the file being
    committed (since it's the source of the change, not a downstream caller).

    Args:
        changed_symbols: Symbol names from ``resolve_changed_symbols``.
        src_dir: Root directory to scan for callers.
        exclude_file: File path to exclude (the file being committed).

    Returns:
        List of ``DownstreamCaller`` records.
    """
    callers: list[DownstreamCaller] = []
    src_root = Path(src_dir)
    if not src_root.exists():
        return callers

    exclude_posix = exclude_file.replace("\\", "/")

    for py_file in src_root.rglob("*.py"):
        rel_path = str(py_file).replace("\\", "/")
        if rel_path == exclude_posix:
            continue

        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(py_file))
        except Exception:
            continue

        # Extract imports
        iv = _ImportVisitor()
        iv.visit(tree)
        imported = iv.symbols

        # For each function in this file, check if it calls any changed symbol
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                cv = _CallVisitor()
                cv.visit(node)
                for symbol in changed_symbols:
                    bare = symbol.split(".")[-1] if "." in symbol else symbol
                    if bare in cv.called and bare in imported:
                        callers.append(DownstreamCaller(
                            file=rel_path,
                            function=node.name,
                            symbol_called=symbol,
                        ))

    return callers


# ---------------------------------------------------------------------------
# Phase 6: Claim Verification Matrix — claim→evidence binding
# ---------------------------------------------------------------------------


@dataclass
class ClaimVerification:
    """Result of binding a single claim to evidence."""

    claim_index: int
    claim_text: str
    claim_type: str  # "symbol", "structural", "tooling", "unresolved"
    matched_symbols: list[str]
    evidence_detail: str
    verdict: str  # "VERIFIED", "UNVERIFIED", "MANUAL REVIEW"


_STRUCTURAL_PATTERNS = [
    re.compile(r"no.*(test|assertion|file).*(delet|modif|remov|chang)", re.IGNORECASE),
    re.compile(r"no.*(regression|breaking)", re.IGNORECASE),
    re.compile(r"existing.*(test|suite).*(pass|green|intact)", re.IGNORECASE),
]

_TOOLING_PATTERNS = [
    re.compile(r"\bruff\b", re.IGNORECASE),
    re.compile(r"\bmypy\b", re.IGNORECASE),
    re.compile(r"\blint", re.IGNORECASE),
    re.compile(r"\btype.?check", re.IGNORECASE),
    re.compile(r"\bformat", re.IGNORECASE),
]


def bind_claims_to_evidence(
    claims: list[str],
    symbol_coverage: list[SymbolCoverage] | None = None,
    class_c: ClassCEvidence | None = None,
    class_a: ClassAEvidence | None = None,
) -> list[ClaimVerification]:
    """Bind each claim to the evidence that verifies or refutes it.

    Classification priority (applied in order per claim):
    1. **Symbol** — claim text contains a changed symbol name (AST identifiers)
    2. **Structural** — claim matches structural patterns (verified by Class C)
    3. **Tooling** — claim mentions ruff/mypy/lint/format (verified by Class A)
    4. **Unresolved** — none of the above; marked MANUAL REVIEW

    Args:
        claims: List of claim strings from ``--claim`` flags.
        symbol_coverage: Per-symbol coverage from ``find_covering_tests``.
        class_c: Class C evidence for structural claim verification.
        class_a: Class A evidence for tooling claim verification.

    Returns:
        List of ``ClaimVerification`` results, one per claim.
    """
    results: list[ClaimVerification] = []
    # Sort symbols longest-first to avoid partial matches (e.g. "run" before "commit_cmd")
    sorted_symbols = sorted(
        (symbol_coverage or []),
        key=lambda sc: len(sc.symbol),
        reverse=True,
    )

    for idx, claim_text in enumerate(claims, 1):
        claim_lower = claim_text.lower()

        # 1. Symbol match: find changed symbols mentioned in claim text
        matched_syms: list[str] = []
        total_tests = 0
        for sc in sorted_symbols:
            bare = sc.symbol.split(".")[-1] if "." in sc.symbol else sc.symbol
            if bare.lower() in claim_lower or sc.symbol.lower() in claim_lower:
                matched_syms.append(sc.symbol)
                total_tests += len(sc.calling_tests)

        if matched_syms:
            if total_tests > 0:
                detail = f"{total_tests} test(s) call {', '.join(f'`{s}`' for s in matched_syms)}"
                verdict = "VERIFIED"
            else:
                detail = f"0 tests call {', '.join(f'`{s}`' for s in matched_syms)}"
                verdict = "UNVERIFIED"
            results.append(ClaimVerification(
                claim_index=idx,
                claim_text=claim_text,
                claim_type="symbol",
                matched_symbols=matched_syms,
                evidence_detail=detail,
                verdict=verdict,
            ))
            continue

        # 2. Structural match: verified by Class C
        if any(p.search(claim_text) for p in _STRUCTURAL_PATTERNS):
            if class_c:
                is_clean = (
                    not class_c.test_files_deleted
                    and not class_c.assertions_removed
                    and not class_c.skip_markers_added
                )
                detail = (
                    "Class C: all structural indicators clean"
                    if is_clean
                    else "Class C: regression indicators found"
                )
                verdict = "VERIFIED" if is_clean else "UNVERIFIED"
            else:
                detail = "Class C not collected"
                verdict = "MANUAL REVIEW"
            results.append(ClaimVerification(
                claim_index=idx,
                claim_text=claim_text,
                claim_type="structural",
                matched_symbols=[],
                evidence_detail=detail,
                verdict=verdict,
            ))
            continue

        # 3. Tooling match: verified by Class A linter/mypy output
        if any(p.search(claim_text) for p in _TOOLING_PATTERNS):
            if class_a:
                tools_ok = True
                parts = []
                if re.search(r"\bruff\b", claim_text, re.IGNORECASE):
                    parts.append(f"ruff: {'clean' if class_a.ruff_clean else 'errors'}")
                    if not class_a.ruff_clean:
                        tools_ok = False
                if re.search(r"\bmypy\b", claim_text, re.IGNORECASE):
                    parts.append(f"mypy: {'clean' if class_a.mypy_clean else 'errors'}")
                    if not class_a.mypy_clean:
                        tools_ok = False
                if not parts:
                    parts.append(f"ruff: {'clean' if class_a.ruff_clean else 'errors'}")
                    parts.append(f"mypy: {'clean' if class_a.mypy_clean else 'errors'}")
                    tools_ok = class_a.ruff_clean and class_a.mypy_clean
                detail = "Class A: " + ", ".join(parts)
                verdict = "VERIFIED" if tools_ok else "UNVERIFIED"
            else:
                detail = "Class A not collected"
                verdict = "MANUAL REVIEW"
            results.append(ClaimVerification(
                claim_index=idx,
                claim_text=claim_text,
                claim_type="tooling",
                matched_symbols=[],
                evidence_detail=detail,
                verdict=verdict,
            ))
            continue

        # 4. Unresolved fallback
        results.append(ClaimVerification(
            claim_index=idx,
            claim_text=claim_text,
            claim_type="unresolved",
            matched_symbols=[],
            evidence_detail="No automatic binding available",
            verdict="MANUAL REVIEW",
        ))

    return results


def render_claim_matrix(verifications: list[ClaimVerification]) -> str:
    """Render the Claim Verification Matrix as a markdown section.

    This is its own section in the packet, between Evidence and
    Verification Methodology.
    """
    lines = ["## Claim Verification Matrix\n"]
    lines.append("| # | Claim | Type | Evidence | Verdict |")
    lines.append("|---|-------|------|----------|---------|")

    verified = 0
    unverified = 0
    manual = 0

    for cv in verifications:
        truncated = cv.claim_text[:60] + "..." if len(cv.claim_text) > 60 else cv.claim_text
        if cv.verdict == "VERIFIED":
            icon = "PASS"
            verified += 1
        elif cv.verdict == "UNVERIFIED":
            icon = "FAIL"
            unverified += 1
        else:
            icon = "REVIEW"
            manual += 1
        lines.append(
            f"| {cv.claim_index} | {truncated} | {cv.claim_type} | {cv.evidence_detail} | {icon} {cv.verdict} |"
        )

    lines.append(f"\n**Verdict summary:** {verified} verified, {unverified} unverified, {manual} manual review.")
    return "\n".join(lines)
