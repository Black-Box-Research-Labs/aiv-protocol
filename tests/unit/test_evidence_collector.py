"""
tests/unit/test_evidence_collector.py

Unit tests for the evidence collector module — verifies that evidence
is COLLECTED from real tool output, not generated from templates.
"""

from __future__ import annotations

from unittest.mock import patch

from aiv.lib.evidence_collector import (
    ClaimVerification,
    ClassAEvidence,
    ClassBEvidence,
    ClassCEvidence,
    ClassFEvidence,
    DownstreamCaller,
    SymbolCoverage,
    TestFileProvenance,
    bind_claims_to_evidence,
    collect_class_b,
    collect_class_c,
    collect_class_f,
    render_claim_matrix,
)

# ---------------------------------------------------------------------------
# Class B — Referential Evidence from git diff
# ---------------------------------------------------------------------------


class TestClassBEvidence:
    """Class B must produce SHA-pinned line-range permalinks, not filenames."""

    def test_to_markdown_includes_sha_pinned_links(self):
        ev = ClassBEvidence(
            head_sha="abc1234def5678",
            owner="org",
            repo="proj",
            hunks=["src/auth.py#L42-L58", "src/auth.py#L100"],
        )
        md = ev.to_markdown()
        assert "abc1234" in md
        assert "src/auth.py#L42-L58" in md
        assert "src/auth.py#L100" in md
        assert "https://github.com/org/proj/blob/abc1234def5678/src/auth.py#L42-L58" in md
        assert "https://github.com/org/proj/blob/abc1234def5678/src/auth.py#L100" in md

    def test_to_markdown_includes_tree_link(self):
        ev = ClassBEvidence(
            head_sha="abc1234def5678",
            owner="org",
            repo="proj",
            hunks=["src/auth.py#L1-L10"],
        )
        md = ev.to_markdown()
        assert "https://github.com/org/proj/tree/abc1234def5678" in md

    @patch("aiv.lib.evidence_collector._run_git")
    def test_collect_parses_diff_hunks(self, mock_git):
        mock_git.side_effect = lambda *args: {
            ("rev-parse", "HEAD"): "abc1234def5678",
            ("diff", "--cached", "-U0", "--", "src/auth.py"): (
                "diff --git a/src/auth.py b/src/auth.py\n"
                "--- a/src/auth.py\n"
                "+++ b/src/auth.py\n"
                "@@ -10,0 +11,5 @@\n"
                "+new line 1\n"
                "@@ -50,3 +56,4 @@\n"
                "+modified\n"
            ),
        }.get(args, "")

        result = collect_class_b("src/auth.py", "org", "proj")
        assert result.head_sha == "abc1234def5678"
        assert len(result.hunks) == 2
        assert "src/auth.py#L11-L15" in result.hunks
        assert "src/auth.py#L56-L59" in result.hunks

    @patch("aiv.lib.evidence_collector._run_git")
    def test_collect_single_line_hunk(self, mock_git):
        mock_git.side_effect = lambda *args: {
            ("rev-parse", "HEAD"): "abc1234",
            ("diff", "--cached", "-U0", "--", "src/x.py"): ("@@ -5,0 +6,1 @@\n+added\n"),
        }.get(args, "")

        result = collect_class_b("src/x.py", "org", "proj")
        assert "src/x.py#L6" in result.hunks

    @patch("aiv.lib.evidence_collector._run_git")
    def test_collect_new_file_fallback(self, mock_git):
        """New files (no diff hunks) should fall back to full line range."""
        mock_git.side_effect = lambda *args: {
            ("rev-parse", "HEAD"): "abc1234",
            ("diff", "--cached", "-U0", "--", "src/new.py"): "",
            ("diff", "-U0", "--", "src/new.py"): "",
        }.get(args, "")

        with patch("pathlib.Path.read_text", return_value="line1\nline2\nline3\n"):
            result = collect_class_b("src/new.py", "org", "proj")
        assert any("L1-L3" in h for h in result.hunks)


# ---------------------------------------------------------------------------
# Class A — Execution Evidence from pytest/ruff/mypy
# ---------------------------------------------------------------------------


class TestClassAEvidence:
    """Class A must include specific test names, not just 'N passed'."""

    def test_to_markdown_includes_test_names(self):
        ev = ClassAEvidence(
            total_passed=100,
            total_failed=0,
            total_warnings=2,
            duration="5.0s",
            relevant_tests=[
                "tests/test_auth.py::test_login",
                "tests/test_auth.py::test_expired_token",
            ],
            ruff_clean=True,
            ruff_errors=0,
            mypy_clean=True,
            mypy_summary="Success: no issues found in 5 source files",
        )
        md = ev.to_markdown()
        assert "test_login" in md
        assert "test_expired_token" in md
        # Global "N passed" is no longer in Class A (it's theater — identical for no-op)
        assert "100 passed" not in md
        assert "Tests covering changed file" in md
        # ruff/mypy now in separate code_quality_markdown(), not to_markdown()
        assert "ruff" not in md
        assert "mypy" not in md
        cq = ev.code_quality_markdown()
        assert "ruff" in cq
        assert "mypy" in cq
        assert "Code Quality" in cq

    def test_to_markdown_warns_no_tests(self):
        ev = ClassAEvidence(
            total_passed=100,
            total_failed=0,
            total_warnings=0,
            duration="5.0s",
            relevant_tests=[],
            ruff_clean=True,
            ruff_errors=0,
            mypy_clean=True,
            mypy_summary="Success",
        )
        md = ev.to_markdown()
        assert "WARNING" in md
        assert "No tests found" in md

    def test_to_markdown_ruff_errors(self):
        ev = ClassAEvidence(
            total_passed=50,
            total_failed=0,
            total_warnings=0,
            duration="2.0s",
            relevant_tests=[],
            ruff_clean=False,
            ruff_errors=3,
            mypy_clean=True,
            mypy_summary="Success",
        )
        # ruff errors now in code_quality_markdown(), not to_markdown()
        md = ev.to_markdown()
        assert "ruff" not in md  # Not in Class A
        cq = ev.code_quality_markdown()
        assert "3 error(s)" in cq


# ---------------------------------------------------------------------------
# Class C — Negative Evidence from anti-cheat scan
# ---------------------------------------------------------------------------


class TestClassCEvidence:
    """Class C must report what was searched for and what was NOT found."""

    def test_to_markdown_clean(self):
        ev = ClassCEvidence(
            test_files_modified=[],
            test_files_deleted=[],
            assertions_removed=[],
            skip_markers_added=[],
            anti_cheat_clean=True,
        )
        md = ev.to_markdown()
        assert "Search methodology" in md
        assert "git diff --cached" in md
        assert "none" in md.lower()

    def test_to_markdown_alerts_on_deletions(self):
        ev = ClassCEvidence(
            test_files_modified=[],
            test_files_deleted=["tests/test_auth.py"],
            assertions_removed=["assert user.is_admin"],
            skip_markers_added=[],
            anti_cheat_clean=False,
        )
        md = ev.to_markdown()
        assert "ALERT" in md
        assert "test_auth.py" in md
        assert "assert user.is_admin" in md

    def test_to_markdown_alerts_on_skip_markers(self):
        ev = ClassCEvidence(
            test_files_modified=[],
            test_files_deleted=[],
            assertions_removed=[],
            skip_markers_added=["@pytest.mark.skip(reason='flaky')"],
            anti_cheat_clean=True,
        )
        md = ev.to_markdown()
        assert "ALERT" in md
        assert "skip marker" in md

    @patch("aiv.lib.evidence_collector._run_git")
    def test_collect_detects_deleted_test_file(self, mock_git):
        mock_git.side_effect = lambda *args: {
            ("diff", "--cached"): "",
            ("diff", "--cached", "--name-status"): "D\ttests/test_auth.py\n",
        }.get(args, "")

        result = collect_class_c()
        assert "tests/test_auth.py" in result.test_files_deleted
        assert not result.anti_cheat_clean

    @patch("aiv.lib.evidence_collector._run_git")
    def test_collect_detects_removed_assertion(self, mock_git):
        mock_git.side_effect = lambda *args: {
            ("diff", "--cached"): ("-    assert response.status == 200\n+    pass\n"),
            ("diff", "--cached", "--name-status"): "",
        }.get(args, "")

        result = collect_class_c()
        assert len(result.assertions_removed) == 1
        assert "assert response.status == 200" in result.assertions_removed[0]

    @patch("aiv.lib.evidence_collector._run_git")
    def test_collect_clean_diff(self, mock_git):
        mock_git.side_effect = lambda *args: {
            ("diff", "--cached"): "+    x = 1\n",
            ("diff", "--cached", "--name-status"): "M\tsrc/feature.py\n",
        }.get(args, "")

        result = collect_class_c()
        assert result.anti_cheat_clean
        assert len(result.assertions_removed) == 0
        assert len(result.test_files_deleted) == 0


# ---------------------------------------------------------------------------
# Class F — Provenance Evidence from test file integrity
# ---------------------------------------------------------------------------


class TestClassFEvidence:
    """Class F must provide chain-of-custody history DISTINCT from Class C and A."""

    def test_to_markdown_shows_provenance_table(self):
        """Class F must render a per-file provenance table, not restate Class C/A."""
        ev = ClassFEvidence(
            test_provenance=[
                TestFileProvenance(
                    path="tests/unit/test_auth.py",
                    commit_count=5,
                    created_by="alice",
                    created_sha="abc1234",
                    last_modified_by="bob",
                    last_modified_sha="def5678",
                    assertion_count=12,
                )
            ],
            recent_test_log="abc1234 test(auth): add login tests\ndef5678 fix(auth): update assertion",
        )
        md = ev.to_markdown()
        assert "chain-of-custody" in md.lower()
        assert "test_auth.py" in md
        assert "alice" in md
        assert "bob" in md
        assert "12" in md  # assertion count
        assert "5" in md  # commit count
        # Must NOT contain Class A/C language
        assert "Full test suite passes" not in md
        assert "No assertions removed" not in md

    def test_to_markdown_no_covering_tests(self):
        """When no covering tests exist, say so honestly."""
        ev = ClassFEvidence(test_provenance=[], recent_test_log="")
        md = ev.to_markdown()
        assert "No covering test files found" in md

    def test_to_markdown_includes_git_log(self):
        """Recent git log for tests/ must appear in the output."""
        ev = ClassFEvidence(
            test_provenance=[],
            recent_test_log="abc1234 test(auth): add tests\ndef5678 fix: update",
        )
        md = ev.to_markdown()
        assert "abc1234" in md
        assert "git log" in md.lower()

    @patch("aiv.lib.evidence_collector._run_git")
    def test_collect_with_covering_files(self, mock_git):
        """collect_class_f with explicit covering files runs git log per file."""
        mock_git.side_effect = lambda *args: {
            ("log", "--oneline", "--follow", "--", "tests/test_auth.py"): "abc1234 initial commit",
            ("log", "--format=%an", "--follow", "--diff-filter=A", "--", "tests/test_auth.py"): "alice\n",
            ("log", "-1", "--format=%an", "--", "tests/test_auth.py"): "alice\n",
            ("log", "--oneline", "-5", "--", "tests/"): "abc1234 initial commit",
        }.get(args, "")

        result = collect_class_f(covering_test_files=["tests/test_auth.py"])
        assert len(result.test_provenance) == 1
        assert result.test_provenance[0].path == "tests/test_auth.py"
        assert result.test_provenance[0].created_by == "alice"
        assert result.test_provenance[0].commit_count == 1

    @patch("aiv.lib.evidence_collector._run_git")
    def test_collect_no_covering_files_discovers_from_diff(self, mock_git):
        """When no covering files passed, discover from staged diff."""
        mock_git.side_effect = lambda *args: {
            ("diff", "--cached", "--name-status"): "M\tsrc/main.py\n",
            ("log", "--oneline", "-5", "--", "tests/"): "",
        }.get(args, "")

        result = collect_class_f()
        assert len(result.test_provenance) == 0


# ---------------------------------------------------------------------------
# Phase 1: AST Symbol Resolver
# ---------------------------------------------------------------------------


class TestASTSymbolResolver:
    """resolve_changed_symbols must map line ranges to enclosing Python symbols."""

    def test_resolves_function(self, tmp_path):
        """A change inside a function body maps to that function name."""
        src = tmp_path / "example.py"
        src.write_text(
            "def foo():\n    x = 1\n    return x\n\ndef bar():\n    return 2\n",
            encoding="utf-8",
        )
        from aiv.lib.evidence_collector import resolve_changed_symbols

        result = resolve_changed_symbols(str(src), [(2, 2)])
        assert "foo" in result
        assert "bar" not in result

    def test_resolves_class(self, tmp_path):
        """A change inside a class body maps to that class name."""
        src = tmp_path / "example.py"
        src.write_text(
            "class MyClass:\n    def method(self):\n        pass\n\ndef standalone():\n    pass\n",
            encoding="utf-8",
        )
        from aiv.lib.evidence_collector import resolve_changed_symbols

        result = resolve_changed_symbols(str(src), [(3, 3)])
        # Should resolve to the method inside the class
        assert any("method" in s for s in result)

    def test_module_level_change(self, tmp_path):
        """A change at module level (outside any function) returns '<module>'."""
        src = tmp_path / "example.py"
        src.write_text("X = 1\nY = 2\n\ndef foo():\n    pass\n", encoding="utf-8")
        from aiv.lib.evidence_collector import resolve_changed_symbols

        result = resolve_changed_symbols(str(src), [(1, 2)])
        assert "<module>" in result

    def test_nonexistent_file(self):
        """A nonexistent file returns '<parse-error>'."""
        from aiv.lib.evidence_collector import resolve_changed_symbols

        result = resolve_changed_symbols("/nonexistent/file.py", [(1, 5)])
        assert "<parse-error>" in result

    def test_multi_symbol_hunk(self, tmp_path):
        """A hunk spanning multiple functions reports ALL of them, not just the smallest."""
        src = tmp_path / "multi.py"
        src.write_text(
            "def alpha():\n"  # L1-2
            "    return 1\n"
            "\n"  # L3
            "def beta():\n"  # L4-5
            "    return 2\n"
            "\n"  # L6
            "def gamma():\n"  # L7-8
            "    return 3\n",
            encoding="utf-8",
        )
        from aiv.lib.evidence_collector import resolve_changed_symbols

        # Hunk spans all three functions
        result = resolve_changed_symbols(str(src), [(1, 8)])
        assert "alpha" in result
        assert "beta" in result
        assert "gamma" in result

    def test_multi_symbol_class_methods(self, tmp_path):
        """A hunk spanning multiple methods in a class reports all methods."""
        src = tmp_path / "cls.py"
        src.write_text(
            "class Auditor:\n"  # L1
            "    def check(self):\n"  # L2-3
            "        pass\n"
            "\n"  # L4
            "    def scan(self):\n"  # L5-6
            "        pass\n"
            "\n"  # L7
            "    def report(self):\n"  # L8-9
            "        return []\n",
            encoding="utf-8",
        )
        from aiv.lib.evidence_collector import resolve_changed_symbols

        result = resolve_changed_symbols(str(src), [(2, 9)])
        assert any("check" in s for s in result)
        assert any("scan" in s for s in result)
        assert any("report" in s for s in result)


# ---------------------------------------------------------------------------
# Phase 2: AST Test Graph
# ---------------------------------------------------------------------------


class TestASTTestGraph:
    """build_test_graph must parse test files for imports and calls."""

    def test_builds_import_map(self, tmp_path):
        """Import map captures imported symbols from test files."""
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        (test_dir / "test_foo.py").write_text(
            "from mymodule import foo_func, FooClass\n\ndef test_foo_works():\n    foo_func()\n",
            encoding="utf-8",
        )
        from aiv.lib.evidence_collector import build_test_graph

        graph = build_test_graph(str(test_dir))
        # Find the test file in the graph
        test_file = [k for k in graph.imports if "test_foo" in k][0]
        assert "foo_func" in graph.imports[test_file]
        assert "FooClass" in graph.imports[test_file]

    def test_builds_call_map(self, tmp_path):
        """Call map captures which symbols each test function calls."""
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        (test_dir / "test_bar.py").write_text(
            "from mymodule import bar_func\n\n"
            "def test_bar_returns_true():\n"
            "    result = bar_func()\n"
            "    assert result is True\n",
            encoding="utf-8",
        )
        from aiv.lib.evidence_collector import build_test_graph

        graph = build_test_graph(str(test_dir))
        test_file = [k for k in graph.calls if "test_bar" in k][0]
        assert "bar_func" in graph.calls[test_file]["test_bar_returns_true"]

    def test_empty_dir(self, tmp_path):
        """Empty test directory returns empty graph."""
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        from aiv.lib.evidence_collector import build_test_graph

        graph = build_test_graph(str(test_dir))
        assert len(graph.imports) == 0

    def test_nonexistent_dir(self):
        """Nonexistent directory returns empty graph."""
        from aiv.lib.evidence_collector import build_test_graph

        graph = build_test_graph("/nonexistent/tests/")
        assert len(graph.imports) == 0


# ---------------------------------------------------------------------------
# Phase 3: find_covering_tests (semantic Class A)
# ---------------------------------------------------------------------------


class TestFindCoveringTests:
    """find_covering_tests must deterministically map symbols to tests via AST."""

    def test_finds_direct_caller(self, tmp_path):
        """A test that imports AND calls a symbol is reported as covering."""
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        (test_dir / "test_calc.py").write_text(
            "from mymodule import calculate\n\ndef test_calculate_adds():\n    assert calculate(1, 2) == 3\n",
            encoding="utf-8",
        )
        from aiv.lib.evidence_collector import (
            build_test_graph,
            find_covering_tests,
        )

        graph = build_test_graph(str(test_dir))
        results = find_covering_tests(["calculate"], graph)
        assert len(results) == 1
        assert len(results[0].calling_tests) == 1
        assert "test_calculate_adds" in results[0].calling_tests[0]
        assert "WARNING" not in results[0].coverage_verdict

    def test_import_without_call_warns(self, tmp_path):
        """A test that imports but never calls a symbol triggers WARNING."""
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        (test_dir / "test_unused.py").write_text(
            "from mymodule import unused_func\n\ndef test_something_else():\n    assert True\n",
            encoding="utf-8",
        )
        from aiv.lib.evidence_collector import build_test_graph, find_covering_tests

        graph = build_test_graph(str(test_dir))
        results = find_covering_tests(["unused_func"], graph)
        assert len(results) == 1
        assert "WARNING" in results[0].coverage_verdict
        assert "0 tests call it" in results[0].coverage_verdict

    def test_no_import_warns(self, tmp_path):
        """A symbol not imported by any test triggers WARNING."""
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        (test_dir / "test_other.py").write_text(
            "def test_unrelated():\n    assert True\n",
            encoding="utf-8",
        )
        from aiv.lib.evidence_collector import build_test_graph, find_covering_tests

        graph = build_test_graph(str(test_dir))
        results = find_covering_tests(["totally_unknown_func"], graph)
        assert len(results) == 1
        assert "WARNING" in results[0].coverage_verdict
        assert "No tests import" in results[0].coverage_verdict

    def test_retro_xdist_bug(self, tmp_path):
        """Retro-test: xdist bug. Tests import ClassAEvidence but never call collect_class_a.

        This is the exact scenario that let the `import pytest_xdist` bug ship.
        The AST approach must correctly identify that collect_class_a is uncovered.
        """
        test_dir = tmp_path / "tests"
        test_dir.mkdir()
        (test_dir / "test_evidence.py").write_text(
            "from aiv.lib.evidence_collector import ClassAEvidence\n\n"
            "def test_markdown_output():\n"
            "    ev = ClassAEvidence(\n"
            "        total_passed=10, total_failed=0, total_warnings=0,\n"
            "        duration='1s', relevant_tests=[], ruff_clean=True,\n"
            "        ruff_errors=0, mypy_clean=True, mypy_summary='ok'\n"
            "    )\n"
            "    assert 'Class A' in ev.to_markdown()\n",
            encoding="utf-8",
        )
        from aiv.lib.evidence_collector import build_test_graph, find_covering_tests

        graph = build_test_graph(str(test_dir))
        # collect_class_a is the function that was buggy, not ClassAEvidence
        results = find_covering_tests(["collect_class_a"], graph)
        assert len(results) == 1
        # The test imports ClassAEvidence, NOT collect_class_a
        assert "WARNING" in results[0].coverage_verdict


# ---------------------------------------------------------------------------
# AST-wired Class A to_markdown (per-symbol coverage)
# ---------------------------------------------------------------------------


class TestClassAWithSymbolCoverage:
    """Class A to_markdown must render per-symbol AST coverage when available."""

    def test_renders_per_symbol_coverage(self):
        """When symbol_coverage is set, render per-symbol analysis instead of flat list."""
        ev = ClassAEvidence(
            total_passed=100,
            total_failed=0,
            total_warnings=0,
            duration="5s",
            relevant_tests=["tests/test_foo.py::test_bar"],
            ruff_clean=True,
            ruff_errors=0,
            mypy_clean=True,
            mypy_summary="ok",
            symbol_coverage=[
                SymbolCoverage(
                    symbol="my_func",
                    line_range="L42-L58",
                    importing_test_files=["tests/test_foo.py"],
                    calling_tests=["tests/test_foo.py::test_bar"],
                    coverage_verdict="1 test(s) call `my_func` directly",
                )
            ],
        )
        md = ev.to_markdown()
        assert "Per-symbol test coverage" in md
        assert "`my_func`" in md
        assert "L42-L58" in md
        assert "test_bar" in md
        # Should NOT fall back to flat test list
        assert "Tests covering changed file" not in md

    def test_renders_warning_for_uncovered_symbol(self):
        """When a symbol has 0 callers, render WARNING."""
        ev = ClassAEvidence(
            total_passed=100,
            total_failed=0,
            total_warnings=0,
            duration="5s",
            relevant_tests=[],
            ruff_clean=True,
            ruff_errors=0,
            mypy_clean=True,
            mypy_summary="ok",
            symbol_coverage=[
                SymbolCoverage(
                    symbol="untested_func",
                    line_range="L10",
                    importing_test_files=[],
                    calling_tests=[],
                    coverage_verdict="WARNING: No tests import or call `untested_func`",
                )
            ],
        )
        md = ev.to_markdown()
        assert "WARNING" in md
        assert "untested_func" in md

    def test_falls_back_to_grep_when_no_ast(self):
        """Without symbol_coverage, falls back to grep-based test list."""
        ev = ClassAEvidence(
            total_passed=100,
            total_failed=0,
            total_warnings=0,
            duration="5s",
            relevant_tests=["tests/test_foo.py::test_bar"],
            ruff_clean=True,
            ruff_errors=0,
            mypy_clean=True,
            mypy_summary="ok",
        )
        md = ev.to_markdown()
        assert "Tests covering changed file" in md
        assert "Per-symbol" not in md


# ---------------------------------------------------------------------------
# Class C downstream caller rendering
# ---------------------------------------------------------------------------


class TestClassCDownstreamCallers:
    """Class C to_markdown must render downstream impact analysis when available."""

    def test_renders_downstream_callers(self):
        ev = ClassCEvidence(
            test_files_modified=[],
            test_files_deleted=[],
            assertions_removed=[],
            skip_markers_added=[],
            anti_cheat_clean=True,
            downstream_callers=[
                DownstreamCaller(file="src/cli/main.py", function="commit_cmd", symbol_called="collect_class_a"),
                DownstreamCaller(file="src/cli/main.py", function="run_checks", symbol_called="collect_class_a"),
            ],
        )
        md = ev.to_markdown()
        assert "Downstream impact analysis" in md
        assert "collect_class_a" in md
        assert "commit_cmd" in md
        assert "run_checks" in md

    def test_no_downstream_callers_omits_section(self):
        ev = ClassCEvidence(
            test_files_modified=[],
            test_files_deleted=[],
            assertions_removed=[],
            skip_markers_added=[],
            anti_cheat_clean=True,
        )
        md = ev.to_markdown()
        assert "Downstream impact" not in md


# ---------------------------------------------------------------------------
# Phase 4: find_downstream_callers
# ---------------------------------------------------------------------------


class TestFindDownstreamCallers:
    """find_downstream_callers must find functions in src/ that call changed symbols."""

    def test_finds_caller_in_src(self, tmp_path):
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "caller.py").write_text(
            "from mymodule import target_func\n\ndef run():\n    target_func()\n",
            encoding="utf-8",
        )
        from aiv.lib.evidence_collector import find_downstream_callers

        callers = find_downstream_callers(["target_func"], src_dir=str(src_dir))
        assert len(callers) == 1
        assert callers[0].function == "run"
        assert callers[0].symbol_called == "target_func"

    def test_excludes_committed_file(self, tmp_path):
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        # The committed file itself should be excluded
        committed = src_dir / "target.py"
        committed.write_text(
            "from mymodule import helper\n\ndef target_func():\n    helper()\n",
            encoding="utf-8",
        )
        from aiv.lib.evidence_collector import find_downstream_callers

        callers = find_downstream_callers(
            ["helper"],
            src_dir=str(src_dir),
            exclude_file=str(committed).replace("\\", "/"),
        )
        assert len(callers) == 0

    def test_no_callers_returns_empty(self, tmp_path):
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "other.py").write_text(
            "def unrelated():\n    pass\n",
            encoding="utf-8",
        )
        from aiv.lib.evidence_collector import find_downstream_callers

        callers = find_downstream_callers(["nonexistent_func"], src_dir=str(src_dir))
        assert len(callers) == 0


# ---------------------------------------------------------------------------
# Phase 5: Class A global metric suppression
# ---------------------------------------------------------------------------


class TestClassAGlobalMetricSuppression:
    """When symbol_coverage is populated, the global 'N passed' line must
    be suppressed. Per-symbol verdicts + coverage summary replace it."""

    def test_global_metric_suppressed_when_ast_available(self):
        ev = ClassAEvidence(
            total_passed=551,
            total_failed=0,
            total_warnings=0,
            duration="29s",
            relevant_tests=[],
            ruff_clean=True,
            ruff_errors=0,
            mypy_clean=True,
            mypy_summary="clean",
            symbol_coverage=[
                SymbolCoverage(
                    symbol="foo",
                    line_range="L10",
                    importing_test_files=["t.py"],
                    calling_tests=["t.py::test_foo"],
                    coverage_verdict="1 test(s) call `foo` directly",
                ),
            ],
        )
        md = ev.to_markdown()
        assert "551 passed" not in md
        assert "PASS" in md
        assert "1/1 symbols verified" in md

    def test_global_metric_absent_when_no_ast(self):
        """Global 'N passed' is theater — must NOT appear even without AST data."""
        ev = ClassAEvidence(
            total_passed=200,
            total_failed=0,
            total_warnings=0,
            duration="10s",
            relevant_tests=["t.py::test_a"],
            ruff_clean=True,
            ruff_errors=0,
            mypy_clean=True,
            mypy_summary="clean",
            symbol_coverage=[],
        )
        md = ev.to_markdown()
        assert "200 passed" not in md
        assert "test_a" in md  # Shows relevant tests, not global count

    def test_coverage_summary_counts_correctly(self):
        ev = ClassAEvidence(
            total_passed=100,
            total_failed=0,
            total_warnings=0,
            duration="5s",
            relevant_tests=[],
            ruff_clean=True,
            ruff_errors=0,
            mypy_clean=True,
            mypy_summary="clean",
            symbol_coverage=[
                SymbolCoverage(
                    symbol="covered",
                    line_range="L1",
                    importing_test_files=["t.py"],
                    calling_tests=["t.py::test_x"],
                    coverage_verdict="1 test(s) call `covered` directly",
                ),
                SymbolCoverage(
                    symbol="uncovered",
                    line_range="L20",
                    importing_test_files=[],
                    calling_tests=[],
                    coverage_verdict="WARNING: No tests import or call `uncovered`",
                ),
            ],
        )
        md = ev.to_markdown()
        assert "1/2 symbols verified" in md
        assert "PASS" in md
        assert "FAIL" in md

    def test_uncovered_symbol_shows_fail(self):
        ev = ClassAEvidence(
            total_passed=100,
            total_failed=0,
            total_warnings=0,
            duration="5s",
            relevant_tests=[],
            ruff_clean=True,
            ruff_errors=0,
            mypy_clean=True,
            mypy_summary="clean",
            symbol_coverage=[
                SymbolCoverage(
                    symbol="to_markdown",
                    line_range="L67",
                    importing_test_files=[],
                    calling_tests=[],
                    coverage_verdict="WARNING: No tests import or call `to_markdown`",
                ),
            ],
        )
        md = ev.to_markdown()
        assert "FAIL" in md
        assert "0/1 symbols verified" in md


# ---------------------------------------------------------------------------
# Phase 6: Claim Verification Matrix — bind_claims_to_evidence
# ---------------------------------------------------------------------------


class TestBindClaimsToEvidence:
    """Tests for the claim→evidence binding function."""

    def test_symbol_claim_verified(self):
        sym_cov = [
            SymbolCoverage(
                symbol="find_downstream_callers",
                line_range="L100",
                importing_test_files=["t.py"],
                calling_tests=["t.py::test_finds_caller"],
                coverage_verdict="1 test(s) call `find_downstream_callers` directly",
            ),
        ]
        results = bind_claims_to_evidence(
            claims=["find_downstream_callers scans src/ AST"],
            symbol_coverage=sym_cov,
        )
        assert len(results) == 1
        assert results[0].claim_type == "symbol"
        assert results[0].verdict == "VERIFIED"
        assert "find_downstream_callers" in results[0].matched_symbols

    def test_symbol_claim_unverified_when_zero_tests(self):
        sym_cov = [
            SymbolCoverage(
                symbol="to_markdown",
                line_range="L67",
                importing_test_files=[],
                calling_tests=[],
                coverage_verdict="WARNING: No tests import or call `to_markdown`",
            ),
        ]
        results = bind_claims_to_evidence(
            claims=["to_markdown renders per-symbol coverage"],
            symbol_coverage=sym_cov,
        )
        assert len(results) == 1
        assert results[0].verdict == "UNVERIFIED"

    def test_structural_claim_verified_when_clean(self):
        class_c = ClassCEvidence(
            test_files_modified=[],
            test_files_deleted=[],
            assertions_removed=[],
            skip_markers_added=[],
            anti_cheat_clean=True,
        )
        results = bind_claims_to_evidence(
            claims=["No existing tests were modified or deleted"],
            class_c=class_c,
        )
        assert len(results) == 1
        assert results[0].claim_type == "structural"
        assert results[0].verdict == "VERIFIED"

    def test_structural_claim_unverified_when_deletions(self):
        class_c = ClassCEvidence(
            test_files_modified=[],
            test_files_deleted=["test_foo.py"],
            assertions_removed=[],
            skip_markers_added=[],
            anti_cheat_clean=False,
        )
        results = bind_claims_to_evidence(
            claims=["No test files deleted"],
            class_c=class_c,
        )
        assert results[0].verdict == "UNVERIFIED"

    def test_tooling_claim_verified_ruff(self):
        class_a = ClassAEvidence(
            total_passed=100,
            total_failed=0,
            total_warnings=0,
            duration="5s",
            relevant_tests=[],
            ruff_clean=True,
            ruff_errors=0,
            mypy_clean=True,
            mypy_summary="clean",
        )
        results = bind_claims_to_evidence(
            claims=["All ruff checks pass"],
            class_a=class_a,
        )
        assert results[0].claim_type == "tooling"
        assert results[0].verdict == "VERIFIED"

    def test_tooling_claim_unverified_mypy_errors(self):
        class_a = ClassAEvidence(
            total_passed=100,
            total_failed=0,
            total_warnings=0,
            duration="5s",
            relevant_tests=[],
            ruff_clean=True,
            ruff_errors=0,
            mypy_clean=False,
            mypy_summary="1 error",
        )
        results = bind_claims_to_evidence(
            claims=["mypy type checks pass"],
            class_a=class_a,
        )
        assert results[0].verdict == "UNVERIFIED"

    def test_unresolved_claim_gets_manual_review(self):
        results = bind_claims_to_evidence(
            claims=["Improved developer experience"],
        )
        assert results[0].claim_type == "unresolved"
        assert results[0].verdict == "MANUAL REVIEW"

    def test_mixed_claims_classified_correctly(self):
        sym_cov = [
            SymbolCoverage(
                symbol="ClassAEvidence",
                line_range="L50",
                importing_test_files=["t.py"],
                calling_tests=["t.py::test_a"],
                coverage_verdict="1 test(s) call `ClassAEvidence` directly",
            ),
        ]
        class_c = ClassCEvidence(
            test_files_modified=[],
            test_files_deleted=[],
            assertions_removed=[],
            skip_markers_added=[],
            anti_cheat_clean=True,
        )
        class_a = ClassAEvidence(
            total_passed=100,
            total_failed=0,
            total_warnings=0,
            duration="5s",
            relevant_tests=[],
            ruff_clean=True,
            ruff_errors=0,
            mypy_clean=True,
            mypy_summary="clean",
        )
        results = bind_claims_to_evidence(
            claims=[
                "ClassAEvidence renders per-symbol coverage",
                "No existing tests were modified or deleted",
                "All ruff checks pass",
                "Improved code quality",
            ],
            symbol_coverage=sym_cov,
            class_c=class_c,
            class_a=class_a,
        )
        assert len(results) == 4
        assert results[0].claim_type == "symbol"
        assert results[1].claim_type == "structural"
        assert results[2].claim_type == "tooling"
        assert results[3].claim_type == "unresolved"

    def test_longest_symbol_matched_first(self):
        """Ensures 'ClassAEvidence.to_markdown' matches before 'to_markdown'."""
        sym_cov = [
            SymbolCoverage(
                symbol="ClassAEvidence.to_markdown",
                line_range="L67",
                importing_test_files=[],
                calling_tests=[],
                coverage_verdict="WARNING: 0 tests",
            ),
            SymbolCoverage(
                symbol="run",
                line_range="L10",
                importing_test_files=["t.py"],
                calling_tests=["t.py::test_run"],
                coverage_verdict="1 test(s)",
            ),
        ]
        results = bind_claims_to_evidence(
            claims=["ClassAEvidence.to_markdown renders coverage"],
            symbol_coverage=sym_cov,
        )
        assert "ClassAEvidence.to_markdown" in results[0].matched_symbols


# ---------------------------------------------------------------------------
# Phase 6: render_claim_matrix
# ---------------------------------------------------------------------------


class TestRenderClaimMatrix:
    """Tests for the markdown rendering of the Claim Verification Matrix."""

    def test_renders_table_headers(self):
        verifications = [
            ClaimVerification(
                claim_index=1,
                claim_text="foo does bar",
                claim_type="symbol",
                matched_symbols=["foo"],
                evidence_detail="1 test(s) call `foo`",
                verdict="VERIFIED",
            ),
        ]
        md = render_claim_matrix(verifications)
        assert "## Claim Verification Matrix" in md
        assert "| # | Claim | Type | Evidence | Verdict |" in md

    def test_renders_verdict_icons(self):
        verifications = [
            ClaimVerification(
                claim_index=1,
                claim_text="verified claim",
                claim_type="symbol",
                matched_symbols=["x"],
                evidence_detail="1 test",
                verdict="VERIFIED",
            ),
            ClaimVerification(
                claim_index=2,
                claim_text="unverified claim",
                claim_type="symbol",
                matched_symbols=["y"],
                evidence_detail="0 tests",
                verdict="UNVERIFIED",
            ),
            ClaimVerification(
                claim_index=3,
                claim_text="review claim",
                claim_type="unresolved",
                matched_symbols=[],
                evidence_detail="No binding",
                verdict="MANUAL REVIEW",
            ),
        ]
        md = render_claim_matrix(verifications)
        assert "PASS VERIFIED" in md
        assert "FAIL UNVERIFIED" in md
        assert "REVIEW MANUAL REVIEW" in md
        assert "1 verified, 1 unverified, 1 manual review" in md

    def test_truncates_long_claims(self):
        long_claim = "A" * 80
        verifications = [
            ClaimVerification(
                claim_index=1,
                claim_text=long_claim,
                claim_type="unresolved",
                matched_symbols=[],
                evidence_detail="No binding",
                verdict="MANUAL REVIEW",
            ),
        ]
        md = render_claim_matrix(verifications)
        assert "A" * 60 + "..." in md
        assert "A" * 80 not in md
