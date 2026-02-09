"""Tests for --skip-checks / --skip-reason enforcement on `aiv commit`.

Verifies the anti-theater gates:
  1. --skip-checks is blocked for R1+ tiers
  2. --skip-checks requires --skip-reason
  3. --skip-reason is stamped into the evidence file
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture()
def staged_repo(tmp_path: Path) -> Path:
    """Create a git repo with a staged functional file."""
    subprocess.run(["git", "init", str(tmp_path)], capture_output=True, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@test.com"],
        cwd=str(tmp_path), capture_output=True, check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"],
        cwd=str(tmp_path), capture_output=True, check=True,
    )
    # Create and commit a file so HEAD exists
    readme = tmp_path / "README.md"
    readme.write_text("# test\n", encoding="utf-8")
    subprocess.run(["git", "add", "."], cwd=str(tmp_path), capture_output=True, check=True)
    subprocess.run(
        ["git", "commit", "-m", "init"],
        cwd=str(tmp_path), capture_output=True, check=True,
    )
    # Create a functional file to commit
    src = tmp_path / "src"
    src.mkdir()
    func_file = src / "hello.py"
    func_file.write_text('print("hello")\n', encoding="utf-8")
    subprocess.run(["git", "add", str(func_file)], cwd=str(tmp_path), capture_output=True, check=True)
    return tmp_path


def _run_aiv_commit(cwd: Path, extra_args: list[str] | None = None) -> subprocess.CompletedProcess:
    """Run aiv commit with standard required flags plus any extras."""
    base = [
        sys.executable, "-m", "aiv", "commit", "src/hello.py",
        "-m", "test commit",
        "-c", "hello prints hello to stdout",
        "-i", "https://github.com/org/repo/issues/1",
        "--requirement", "Issue #1",
        "-r", "trivial test",
        "-s", "test summary",
    ]
    if extra_args:
        base.extend(extra_args)
    return subprocess.run(
        base,
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(cwd),
    )


class TestSkipChecksBlockedForR1Plus:
    """--skip-checks is only allowed for R0."""

    @pytest.mark.parametrize("tier", ["R1", "R2", "R3"])
    def test_skip_checks_rejected_for_higher_tiers(self, staged_repo: Path, tier: str) -> None:
        result = _run_aiv_commit(staged_repo, ["-t", tier, "--skip-checks", "--skip-reason", "test"])
        assert result.returncode != 0
        assert "only allowed for R0" in result.stdout


class TestSkipReasonRequired:
    """--skip-checks requires --skip-reason."""

    def test_skip_checks_without_reason_fails(self, staged_repo: Path) -> None:
        result = _run_aiv_commit(staged_repo, ["-t", "R0", "--skip-checks"])
        assert result.returncode != 0
        assert "--skip-reason" in result.stdout

    def test_skip_checks_with_reason_succeeds(self, staged_repo: Path) -> None:
        result = _run_aiv_commit(
            staged_repo,
            ["-t", "R0", "--skip-checks", "--skip-reason", "Docs-only change", "--dry-run"],
        )
        assert result.returncode == 0


class TestSkipReasonStampedInEvidence:
    """--skip-reason text appears in the generated evidence file."""

    def test_reason_in_class_a(self, staged_repo: Path) -> None:
        reason = "Help text only, no logic changes"
        _run_aiv_commit(
            staged_repo,
            ["-t", "R0", "--skip-checks", "--skip-reason", reason, "--dry-run"],
        )
        evidence_dir = staged_repo / ".github" / "aiv-evidence"
        evidence_files = list(evidence_dir.glob("EVIDENCE_*.md"))
        assert len(evidence_files) == 1, f"Expected 1 evidence file, got {len(evidence_files)}"
        content = evidence_files[0].read_text(encoding="utf-8")
        assert reason in content, "Skip reason not found in evidence file"
        assert "**Skip reason:**" in content, "Skip reason not properly labeled"

    def test_reason_in_methodology(self, staged_repo: Path) -> None:
        reason = "Formatting only"
        _run_aiv_commit(
            staged_repo,
            ["-t", "R0", "--skip-checks", "--skip-reason", reason, "--dry-run"],
        )
        evidence_dir = staged_repo / ".github" / "aiv-evidence"
        evidence_files = list(evidence_dir.glob("EVIDENCE_*.md"))
        content = evidence_files[0].read_text(encoding="utf-8")
        assert "**Reason:** Formatting only" in content
