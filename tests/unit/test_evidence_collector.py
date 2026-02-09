"""
tests/unit/test_evidence_collector.py

Unit tests for the evidence collector module — verifies that evidence
is COLLECTED from real tool output, not generated from templates.
"""

from __future__ import annotations

import re
from unittest.mock import patch

import pytest

from aiv.lib.evidence_collector import (
    ClassAEvidence,
    ClassBEvidence,
    ClassCEvidence,
    ClassFEvidence,
    collect_class_b,
    collect_class_c,
    collect_class_f,
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
            ("diff", "--cached", "-U0", "--", "src/x.py"): (
                "@@ -5,0 +6,1 @@\n+added\n"
            ),
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
        assert "100 passed" in md
        assert "0 failed" in md
        assert "5.0s" in md
        assert "Tests covering changed file" in md

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
        md = ev.to_markdown()
        assert "3 error(s)" in md


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
            ("diff", "--cached"): (
                "-    assert response.status == 200\n"
                "+    pass\n"
            ),
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
    """Class F must scan test file integrity from the actual diff."""

    def test_to_markdown_clean(self):
        ev = ClassFEvidence(
            test_files_in_diff=[],
            test_assertions_deleted=0,
            test_files_deleted=0,
        )
        md = ev.to_markdown()
        assert "No test files deleted" in md
        assert "No assertions removed" in md

    def test_to_markdown_alerts(self):
        ev = ClassFEvidence(
            test_files_in_diff=["tests/test_auth.py"],
            test_assertions_deleted=3,
            test_files_deleted=1,
        )
        md = ev.to_markdown()
        assert "ALERT" in md
        assert "1 test file(s) deleted" in md
        assert "3 assertion(s) removed" in md

    @patch("aiv.lib.evidence_collector._run_git")
    def test_collect_detects_deleted_test(self, mock_git):
        mock_git.side_effect = lambda *args: {
            ("diff", "--cached", "--name-status"): "D\ttests/test_auth.py\nM\tsrc/main.py\n",
            ("diff", "--cached", "--", "tests/"): "-    assert x == 1\n-    assert y == 2\n",
        }.get(args, "")

        result = collect_class_f()
        assert result.test_files_deleted == 1
        assert result.test_assertions_deleted == 2
        assert "tests/test_auth.py" in result.test_files_in_diff

    @patch("aiv.lib.evidence_collector._run_git")
    def test_collect_clean(self, mock_git):
        mock_git.side_effect = lambda *args: {
            ("diff", "--cached", "--name-status"): "M\tsrc/main.py\n",
            ("diff", "--cached", "--", "tests/"): "",
        }.get(args, "")

        result = collect_class_f()
        assert result.test_files_deleted == 0
        assert result.test_assertions_deleted == 0
