"""
aiv/hooks/pre_push.py

Pre-push hook for AIV protocol enforcement.
Installed by ``aiv init``. Works on all platforms.

This hook closes the ``--no-verify`` gap:

- ``git commit --no-verify`` bypasses the pre-commit hook.
- But ``git push`` still runs this pre-push hook.
- This hook scans every commit about to be pushed and blocks the push
  if any commit has functional files without a verification packet.

To bypass THIS hook, someone would need ``git push --no-verify``,
which is a separate, deliberate action. The CI protocol-audit job
(layer 3) catches even that.

Defence-in-depth:
  1. pre-commit hook  — blocks at commit time
  2. pre-push hook    — catches --no-verify commits before they leave
  3. CI protocol-audit — catches --no-verify push (server-side)
  4. Branch protection — require PRs (GitHub settings)
"""

from __future__ import annotations

import subprocess
import sys

# ---------------------------------------------------------------------------
# Constants — mirrors pre_commit.py and auditor.py
# ---------------------------------------------------------------------------

PACKET_PREFIXES = (
    ".github/aiv-packets/VERIFICATION_PACKET_",
    ".github/VERIFICATION_PACKET_",
)
PACKET_SUFFIX = ".md"

FUNCTIONAL_PREFIXES = (
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

FUNCTIONAL_ROOT_FILES = {
    "pyproject.toml",
    "setup.py",
    "setup.cfg",
    "package.json",
    "package-lock.json",
    ".gitignore",
    ".env.example",
}


def _is_packet(path: str) -> bool:
    return any(path.startswith(p) for p in PACKET_PREFIXES) and path.endswith(
        PACKET_SUFFIX
    )


def _is_functional(path: str) -> bool:
    if any(path.startswith(p) for p in FUNCTIONAL_PREFIXES):
        return True
    return path in FUNCTIONAL_ROOT_FILES


def _get_commits_in_range(local_sha: str, remote_sha: str) -> list[str]:
    """Return list of commit SHAs in the push range."""
    # Zero SHA means new branch or deleted branch
    zero = "0" * 40
    if local_sha == zero:
        # Branch deletion — nothing to check
        return []
    if remote_sha == zero:
        # New branch — check all commits not on any remote branch
        try:
            result = subprocess.run(
                [
                    "git",
                    "log",
                    local_sha,
                    "--not",
                    "--remotes",
                    "--format=%H",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if result.returncode == 0:
                return [s for s in result.stdout.strip().split("\n") if s]
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return []

    # Normal push — commits between remote and local
    try:
        result = subprocess.run(
            ["git", "log", f"{remote_sha}..{local_sha}", "--format=%H"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0:
            return [s for s in result.stdout.strip().split("\n") if s]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return []


def _get_commit_files(sha: str) -> list[str]:
    """Return list of files changed in a single commit."""
    try:
        result = subprocess.run(
            ["git", "diff-tree", "--no-commit-id", "--name-only", "-r", sha],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return [f for f in result.stdout.strip().split("\n") if f]
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return []


def check_commits(commits: list[str]) -> list[tuple[str, list[str]]]:
    """Check a list of commit SHAs for protocol violations.

    Returns a list of (short_sha, functional_files) tuples for violating commits.
    """
    violations: list[tuple[str, list[str]]] = []

    for sha in commits:
        files = _get_commit_files(sha)
        functional = [f for f in files if _is_functional(f)]
        packets = [f for f in files if _is_packet(f)]

        # Functional files without a paired packet = HOOK_BYPASS
        if functional and not packets:
            violations.append((sha[:7], functional))

    return violations


def main() -> int:
    """Run the AIV pre-push hook.

    Reads push info from stdin (git provides this):
        <local_ref> <local_sha> <remote_ref> <remote_sha>

    Returns 0 to allow push, 1 to block.
    """
    violations: list[tuple[str, list[str]]] = []

    for line in sys.stdin:
        parts = line.strip().split()
        if len(parts) < 4:
            continue

        local_sha = parts[1]
        remote_sha = parts[3]

        commits = _get_commits_in_range(local_sha, remote_sha)
        violations.extend(check_commits(commits))

    if not violations:
        return 0

    # Block the push
    print()
    print("=" * 79)
    print("[BLOCK] AIV Pre-Push Hook: Protocol Violation Detected")
    print("=" * 79)
    print()
    print("WHAT HAPPENED:")
    print(f"  {len(violations)} commit(s) contain functional files without a verification packet.")
    print("  This means `git commit --no-verify` was used to bypass the pre-commit hook.")
    print()
    print("WHY THIS IS BLOCKED:")
    print("  Every functional file change MUST have a paired verification packet.")
    print("  The `--no-verify` flag skips the pre-commit hook, but this pre-push hook")
    print("  catches the violation before it reaches the remote repository.")
    print()

    print("VIOLATING COMMITS:")
    for short_sha, func_files in violations:
        print(f"  {short_sha}:")
        for f in func_files[:5]:
            print(f"    - {f}")
        if len(func_files) > 5:
            print(f"    ... and {len(func_files) - 5} more")
    print()

    num = sum(len(f) for _, f in violations)
    print("HOW TO FIX:")
    print(f"  1. git reset --soft HEAD~{len(violations)}")
    print("  2. git reset HEAD -- .")
    print("  3. For EACH functional file, run:")
    print("       aiv commit <file> -m '<message>' -t R1 -c '<claim>' \\")
    print("         -i '<intent-url>' --requirement '<req>' \\")
    print("         -r '<rationale>' -s '<summary>'")
    print("  4. git push")
    print()
    print("DO NOT use `--no-verify` on git commit or git push.")
    print("DO NOT hand-write verification packets. Use `aiv commit`.")
    print("=" * 79)

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
