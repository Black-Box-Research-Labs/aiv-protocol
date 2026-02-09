"""
Tests for aiv.hooks.pre_commit — the portable pre-commit hook.

Tests the rule engine directly by mocking _staged_files and _run_git,
without requiring an actual git repository.
"""

from __future__ import annotations

from unittest.mock import patch

from aiv.hooks.pre_commit import (
    _is_functional,
    _is_gitkeep,
    _is_packet,
    _is_submodule_path,
    main,
)

# ---------------------------------------------------------------------------
# Classification tests
# ---------------------------------------------------------------------------


class TestIsPacket:
    def test_standard_packet(self) -> None:
        assert _is_packet(".github/aiv-packets/VERIFICATION_PACKET_AUTH_FIX.md") is True

    def test_legacy_location(self) -> None:
        assert _is_packet(".github/VERIFICATION_PACKET_OLD.md") is True

    def test_template_is_not_packet(self) -> None:
        # Templates match the pattern — they ARE packets structurally
        assert _is_packet(".github/aiv-packets/VERIFICATION_PACKET_TEMPLATE.md") is True

    def test_random_markdown_not_packet(self) -> None:
        assert _is_packet("README.md") is False
        assert _is_packet(".github/aiv-packets/README.md") is False

    def test_non_md_not_packet(self) -> None:
        assert _is_packet(".github/aiv-packets/VERIFICATION_PACKET_FOO.txt") is False


class TestIsFunctional:
    def test_src_file(self) -> None:
        assert _is_functional("src/aiv/cli/main.py") is True

    def test_test_file(self) -> None:
        assert _is_functional("tests/unit/test_parser.py") is True

    def test_workflow(self) -> None:
        assert _is_functional(".github/workflows/ci.yml") is True

    def test_scripts(self) -> None:
        assert _is_functional("scripts/map_packets.py") is True

    def test_engine(self) -> None:
        assert _is_functional("engine/cli.ts") is True

    def test_root_config(self) -> None:
        assert _is_functional("pyproject.toml") is True
        assert _is_functional("package.json") is True
        assert _is_functional(".gitignore") is True

    def test_readme_not_functional(self) -> None:
        assert _is_functional("README.md") is False

    def test_docs_not_functional(self) -> None:
        assert _is_functional("docs/guide.md") is False

    def test_changelog_not_functional(self) -> None:
        assert _is_functional("CHANGELOG.md") is False

    def test_packet_not_functional(self) -> None:
        assert _is_functional(".github/aiv-packets/VERIFICATION_PACKET_FOO.md") is False


class TestIsGitkeep:
    def test_gitkeep(self) -> None:
        assert _is_gitkeep(".github/aiv-packets/.gitkeep") is True

    def test_other_gitkeep(self) -> None:
        assert _is_gitkeep("data/.gitkeep") is False


class TestIsSubmodulePath:
    def test_exact_match(self) -> None:
        assert _is_submodule_path("aiv-protocol", ["aiv-protocol"]) is True

    def test_nested_file(self) -> None:
        assert _is_submodule_path("aiv-protocol/src/foo.py", ["aiv-protocol"]) is True

    def test_no_match(self) -> None:
        assert _is_submodule_path("src/foo.py", ["aiv-protocol"]) is False

    def test_empty_submodules(self) -> None:
        assert _is_submodule_path("anything", []) is False


# ---------------------------------------------------------------------------
# Rule engine tests (mock git)
# ---------------------------------------------------------------------------


def _mock_main(staged: list[str], submodule_paths: list[str] | None = None) -> int:
    """Run main() with mocked staged files and no packet validation."""
    with (
        patch("aiv.hooks.pre_commit._staged_files", return_value=staged),
        patch("aiv.hooks.pre_commit._write_safety_snapshot"),
        patch("aiv.hooks.pre_commit._run_git", return_value=""),
        patch("aiv.hooks.pre_commit._validate_packet", return_value=True),
        patch(
            "aiv.hooks.pre_commit._get_submodule_paths",
            return_value=submodule_paths or [],
        ),
    ):
        return main()


class TestRule1DependencyPair:
    def test_package_json_pair_allowed(self) -> None:
        assert _mock_main(["package.json", "package-lock.json"]) == 0

    def test_package_json_alone_needs_packet(self) -> None:
        # package.json is functional → needs a packet
        assert _mock_main(["package.json"]) == 1


class TestRule2AtomicUnit:
    def test_functional_plus_packet_allowed(self) -> None:
        assert (
            _mock_main(
                [
                    "src/aiv/cli/main.py",
                    ".github/aiv-packets/VERIFICATION_PACKET_CLI_FIX.md",
                ]
            )
            == 0
        )

    def test_test_plus_packet_allowed(self) -> None:
        assert (
            _mock_main(
                [
                    "tests/unit/test_parser.py",
                    ".github/aiv-packets/VERIFICATION_PACKET_PARSER.md",
                ]
            )
            == 0
        )

    def test_functional_plus_packet_validates(self) -> None:
        """When packet validation fails, commit is rejected."""
        with (
            patch(
                "aiv.hooks.pre_commit._staged_files",
                return_value=[
                    "src/aiv/cli/main.py",
                    ".github/aiv-packets/VERIFICATION_PACKET_CLI_FIX.md",
                ],
            ),
            patch("aiv.hooks.pre_commit._write_safety_snapshot"),
            patch("aiv.hooks.pre_commit._run_git", return_value=""),
            patch("aiv.hooks.pre_commit._validate_packet", return_value=False),
            patch("aiv.hooks.pre_commit._get_submodule_paths", return_value=[]),
        ):
            assert main() == 1


class TestRule3PacketPlusGitkeep:
    def test_packet_plus_gitkeep_allowed(self) -> None:
        assert (
            _mock_main(
                [
                    ".github/aiv-packets/.gitkeep",
                    ".github/aiv-packets/VERIFICATION_PACKET_INIT.md",
                ]
            )
            == 0
        )


class TestRule4SubmoduleUpdate:
    def test_submodule_plus_packet_allowed(self) -> None:
        assert (
            _mock_main(
                ["aiv-protocol", ".github/aiv-packets/VERIFICATION_PACKET_SUBMOD.md"],
                submodule_paths=["aiv-protocol"],
            )
            == 0
        )


class TestRule5SubmoduleAdd:
    def test_gitmodules_plus_submodule_plus_packet_allowed(self) -> None:
        assert (
            _mock_main(
                [
                    ".gitmodules",
                    "aiv-protocol",
                    ".github/aiv-packets/VERIFICATION_PACKET_SUBMOD_ADD.md",
                ],
                submodule_paths=["aiv-protocol"],
            )
            == 0
        )


class TestRule6PacketOnly:
    def test_single_packet_allowed(self) -> None:
        assert _mock_main([".github/aiv-packets/VERIFICATION_PACKET_DOCS.md"]) == 0


class TestRule7DocsOnly:
    def test_readme_only_allowed(self) -> None:
        assert _mock_main(["README.md"]) == 0

    def test_changelog_only_allowed(self) -> None:
        assert _mock_main(["CHANGELOG.md"]) == 0

    def test_docs_file_allowed(self) -> None:
        assert _mock_main(["docs/guide.md"]) == 0

    def test_multiple_docs_allowed(self) -> None:
        assert _mock_main(["README.md", "CHANGELOG.md", "docs/guide.md"]) == 0


class TestRule8TooManyFiles:
    def test_three_functional_files_rejected(self) -> None:
        assert (
            _mock_main(
                [
                    "src/a.py",
                    "src/b.py",
                    ".github/aiv-packets/VERIFICATION_PACKET_FOO.md",
                ]
            )
            == 1
        )


class TestRule9FunctionalWithoutPacket:
    def test_src_without_packet_rejected(self) -> None:
        assert _mock_main(["src/aiv/cli/main.py"]) == 1

    def test_pyproject_without_packet_rejected(self) -> None:
        assert _mock_main(["pyproject.toml"]) == 1

    def test_workflow_without_packet_rejected(self) -> None:
        assert _mock_main([".github/workflows/ci.yml"]) == 1


class TestRule10InvalidTwoFileCombination:
    def test_two_functional_files_rejected(self) -> None:
        assert _mock_main(["src/a.py", "src/b.py"]) == 1

    def test_two_docs_files_allowed(self) -> None:
        # Two non-functional files → Rule 7 (docs-only) allows
        assert _mock_main(["README.md", "CHANGELOG.md"]) == 0


class TestEmptyStaged:
    def test_nothing_staged_allowed(self) -> None:
        assert _mock_main([]) == 0
