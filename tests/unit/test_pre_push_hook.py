"""
tests/unit/test_pre_push_hook.py

Unit tests for the pre-push hook — verifies detection of commits
that bypassed the pre-commit hook via ``git commit --no-verify``.
"""

from unittest.mock import patch

from aiv.hooks.pre_push import (
    _is_functional,
    _is_packet,
    check_commits,
    main,
)

# ---------------------------------------------------------------------------
# Helper classification tests
# ---------------------------------------------------------------------------


class TestIsPacket:
    def test_standard_packet(self) -> None:
        assert _is_packet(".github/aiv-packets/VERIFICATION_PACKET_FOO.md") is True

    def test_legacy_packet(self) -> None:
        assert _is_packet(".github/VERIFICATION_PACKET_OLD.md") is True

    def test_not_a_packet(self) -> None:
        assert _is_packet("README.md") is False
        assert _is_packet("src/main.py") is False


class TestIsFunctional:
    def test_src_functional(self) -> None:
        assert _is_functional("src/aiv/cli/main.py") is True

    def test_tests_functional(self) -> None:
        assert _is_functional("tests/unit/test_foo.py") is True

    def test_root_file(self) -> None:
        assert _is_functional("pyproject.toml") is True

    def test_docs_not_functional(self) -> None:
        assert _is_functional("docs/guide.md") is False
        assert _is_functional("README.md") is False


# ---------------------------------------------------------------------------
# check_commits tests
# ---------------------------------------------------------------------------


class TestCheckCommits:
    def test_violation_detected(self) -> None:
        """Commit with functional files but no packet is a violation."""
        with patch("aiv.hooks.pre_push._get_commit_files") as mock_files:
            mock_files.return_value = ["src/aiv/cli/main.py"]
            violations = check_commits(["a" * 40])

        assert len(violations) == 1
        assert violations[0][0] == "a" * 7
        assert "src/aiv/cli/main.py" in violations[0][1]

    def test_clean_commit(self) -> None:
        """Commit with functional file + packet has no violation."""
        with patch("aiv.hooks.pre_push._get_commit_files") as mock_files:
            mock_files.return_value = [
                "src/aiv/cli/main.py",
                ".github/aiv-packets/VERIFICATION_PACKET_MAIN.md",
            ]
            violations = check_commits(["b" * 40])

        assert len(violations) == 0

    def test_docs_only_skipped(self) -> None:
        """Commit with only docs files has no violation."""
        with patch("aiv.hooks.pre_push._get_commit_files") as mock_files:
            mock_files.return_value = ["README.md", "docs/guide.md"]
            violations = check_commits(["c" * 40])

        assert len(violations) == 0

    def test_multiple_commits_covered_by_range_packet(self) -> None:
        """Two-Layer: functional-only commit is covered by a packet elsewhere in the range."""
        with patch("aiv.hooks.pre_push._get_commit_files") as mock_files:
            mock_files.side_effect = [
                # Commit 1: has a packet (covers the range)
                ["src/foo.py", ".github/aiv-packets/VERIFICATION_PACKET_FOO.md"],
                # Commit 2: functional-only, but covered by range evidence
                ["src/bar.py"],
            ]
            violations = check_commits(["d" * 40, "e" * 40])

        assert len(violations) == 0

    def test_multiple_commits_no_evidence_anywhere(self) -> None:
        """No evidence in range: all functional-only commits are violations."""
        with patch("aiv.hooks.pre_push._get_commit_files") as mock_files:
            mock_files.side_effect = [
                ["src/foo.py"],
                ["src/bar.py"],
            ]
            violations = check_commits(["d" * 40, "e" * 40])

        assert len(violations) == 2

    def test_layer2_packet_covers_range(self) -> None:
        """A PACKET_*.md in the range covers functional-only commits."""
        with patch("aiv.hooks.pre_push._get_commit_files") as mock_files:
            mock_files.side_effect = [
                # Commit 1: functional-only
                ["src/aiv/lib/change.py"],
                # Commit 2: functional-only
                ["src/aiv/hooks/pre_commit.py"],
                # Commit 3: Layer 2 packet only
                [".github/aiv-packets/PACKET_feature.md"],
            ]
            violations = check_commits(["a" * 40, "b" * 40, "c" * 40])

        assert len(violations) == 0

    def test_evidence_file_covers_range(self) -> None:
        """An EVIDENCE_*.md in the range covers functional-only commits."""
        with patch("aiv.hooks.pre_push._get_commit_files") as mock_files:
            mock_files.side_effect = [
                # Commit 1: functional + evidence (aiv commit)
                ["src/foo.py", ".github/aiv-evidence/EVIDENCE_FOO.md"],
                # Commit 2: functional-only, covered by range evidence
                ["src/bar.py"],
            ]
            violations = check_commits(["d" * 40, "e" * 40])

        assert len(violations) == 0


# ---------------------------------------------------------------------------
# main() tests — stdin parsing + exit code
# ---------------------------------------------------------------------------


class TestMain:
    def test_clean_push_returns_0(self) -> None:
        """Push with all clean commits returns 0."""
        stdin_line = f"refs/heads/main {'b' * 40} refs/heads/main {'a' * 40}\n"
        with (
            patch("aiv.hooks.pre_push.sys.stdin", [stdin_line]),
            patch("aiv.hooks.pre_push._get_commits_in_range") as mock_range,
            patch("aiv.hooks.pre_push._get_commit_files") as mock_files,
        ):
            mock_range.return_value = ["b" * 40]
            mock_files.return_value = [
                "src/foo.py",
                ".github/aiv-packets/VERIFICATION_PACKET_FOO.md",
            ]
            result = main()

        assert result == 0

    def test_violation_returns_1(self) -> None:
        """Push with a violating commit returns 1."""
        stdin_line = f"refs/heads/main {'b' * 40} refs/heads/main {'a' * 40}\n"
        with (
            patch("aiv.hooks.pre_push.sys.stdin", [stdin_line]),
            patch("aiv.hooks.pre_push._get_commits_in_range") as mock_range,
            patch("aiv.hooks.pre_push._get_commit_files") as mock_files,
        ):
            mock_range.return_value = ["b" * 40]
            mock_files.return_value = ["src/aiv/cli/main.py"]
            result = main()

        assert result == 1

    def test_empty_stdin_returns_0(self) -> None:
        """No push refs = nothing to check."""
        with patch("aiv.hooks.pre_push.sys.stdin", []):
            result = main()

        assert result == 0

    def test_branch_deletion_returns_0(self) -> None:
        """Deleting a branch (local sha = 0*40) should pass."""
        zero = "0" * 40
        stdin_line = f"refs/heads/old {zero} refs/heads/old {'a' * 40}\n"
        with (
            patch("aiv.hooks.pre_push.sys.stdin", [stdin_line]),
            patch("aiv.hooks.pre_push._get_commits_in_range") as mock_range,
        ):
            mock_range.return_value = []
            result = main()

        assert result == 0
