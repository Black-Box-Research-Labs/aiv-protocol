"""
aiv/lib/change.py

Change lifecycle management for the Two-Layer Verification Architecture.

Manages .aiv/change.json — the local (gitignored) state file that tracks
an active change context. A "change" is a logical grouping of commits
that will be packaged into a single Layer 2 verification packet.

Lifecycle:
    aiv begin <name>   → creates change.json
    git commit ...     → pre-commit hook appends commit to change.json
    aiv close          → generates packet, clears change.json
    aiv abandon        → clears change.json without packet
    aiv status         → prints current change state
"""

from __future__ import annotations

import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from pydantic import BaseModel, Field


class CommitRecord(BaseModel):
    """A single commit within a change."""

    sha: str
    message: str
    files: list[str] = Field(default_factory=list)
    evidence: list[str] = Field(default_factory=list)
    timestamp: str  # ISO-8601


class ChangeContext(BaseModel):
    """The active change context persisted in .aiv/change.json."""

    name: str
    description: str = ""
    started_at: str  # ISO-8601
    mode: str = "direct"  # "direct" or "pr"
    commits: list[CommitRecord] = Field(default_factory=list)
    files_changed: list[str] = Field(default_factory=list)
    evidence_files: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------


def _aiv_dir(repo_root: Path | None = None) -> Path:
    """Return the .aiv/ directory, creating it if needed."""
    root = repo_root or Path(".")
    aiv = root / ".aiv"
    aiv.mkdir(parents=True, exist_ok=True)
    return aiv


def _change_path(repo_root: Path | None = None) -> Path:
    """Return the path to .aiv/change.json."""
    return _aiv_dir(repo_root) / "change.json"


# ---------------------------------------------------------------------------
# Read / write
# ---------------------------------------------------------------------------


def load_change(repo_root: Path | None = None) -> ChangeContext | None:
    """Load the active change context, or None if no change is active."""
    path = _change_path(repo_root)
    if not path.exists():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return ChangeContext(**data)
    except (json.JSONDecodeError, Exception):
        return None


def save_change(ctx: ChangeContext, repo_root: Path | None = None) -> Path:
    """Persist the change context to .aiv/change.json."""
    path = _change_path(repo_root)
    path.write_text(
        ctx.model_dump_json(indent=2),
        encoding="utf-8",
    )
    return path


def clear_change(repo_root: Path | None = None) -> None:
    """Remove .aiv/change.json (end of lifecycle)."""
    path = _change_path(repo_root)
    if path.exists():
        path.unlink()


# ---------------------------------------------------------------------------
# Lifecycle operations
# ---------------------------------------------------------------------------

_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9\-]*$")


def begin_change(
    name: str,
    description: str = "",
    mode: str = "direct",
    repo_root: Path | None = None,
) -> ChangeContext:
    """
    Open a new change context.

    Raises ValueError if a change is already active or the name is invalid.
    """
    existing = load_change(repo_root)
    if existing is not None:
        raise ValueError(
            f"Change '{existing.name}' is already active "
            f"(started {existing.started_at}). "
            f"Run `aiv close` or `aiv abandon` first."
        )

    if not _NAME_RE.match(name):
        raise ValueError(
            f"Invalid change name '{name}'. Must be lowercase alphanumeric + hyphens, starting with alphanumeric."
        )

    ctx = ChangeContext(
        name=name,
        description=description,
        started_at=datetime.now(timezone.utc).isoformat(),
        mode=mode,
    )
    save_change(ctx, repo_root)
    return ctx


def record_commit(
    sha: str,
    message: str,
    files: list[str],
    evidence: list[str],
    repo_root: Path | None = None,
) -> ChangeContext | None:
    """
    Append a commit to the active change context.

    Called by the pre-commit hook after evidence generation.
    Returns the updated context, or None if no change is active.
    """
    ctx = load_change(repo_root)
    if ctx is None:
        return None

    record = CommitRecord(
        sha=sha,
        message=message,
        files=files,
        evidence=evidence,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
    ctx.commits.append(record)

    # Update aggregate lists (deduplicated)
    for f in files:
        if f not in ctx.files_changed:
            ctx.files_changed.append(f)
    for e in evidence:
        if e not in ctx.evidence_files:
            ctx.evidence_files.append(e)

    save_change(ctx, repo_root)
    return ctx


def close_change(repo_root: Path | None = None) -> ChangeContext:
    """
    Close the active change and return its context for packet generation.

    Raises ValueError if no change is active or the change has no commits.
    Does NOT clear the change file — the caller should do that after
    successfully generating and committing the packet.
    """
    ctx = load_change(repo_root)
    if ctx is None:
        raise ValueError("No active change context. Run `aiv begin <name>` first.")
    if not ctx.commits:
        raise ValueError(
            f"Change '{ctx.name}' has no commits. Nothing to verify.\n"
            "Run `aiv abandon` to discard, or make commits first."
        )
    return ctx


def abandon_change(repo_root: Path | None = None) -> ChangeContext | None:
    """
    Abandon the active change without generating a packet.

    Returns the abandoned context (for reporting), or None if no change was active.
    """
    ctx = load_change(repo_root)
    clear_change(repo_root)
    return ctx


def detect_untracked_commits(
    ctx: ChangeContext,
    repo_root: Path | None = None,
) -> list[dict[str, str]]:
    """
    Detect commits on the current branch since `aiv begin` that are NOT
    tracked in change.json. These may have been made with --no-verify.

    Returns list of {sha, message} dicts for untracked commits.
    """
    if not ctx.commits:
        return []

    # Get the base: the commit just before the first tracked commit
    first_sha = ctx.commits[0].sha
    tracked_shas = {c.sha for c in ctx.commits}

    try:
        # Get all commits from first tracked commit's parent to HEAD
        result = subprocess.run(
            ["git", "log", "--format=%H %s", f"{first_sha}^..HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(repo_root) if repo_root else None,
        )
        if result.returncode != 0:
            return []

        untracked = []
        for line in result.stdout.strip().split("\n"):
            if not line.strip():
                continue
            parts = line.split(" ", 1)
            sha = parts[0]
            msg = parts[1] if len(parts) > 1 else ""
            if sha not in tracked_shas:
                untracked.append({"sha": sha, "message": msg})

        return untracked

    except (subprocess.TimeoutExpired, FileNotFoundError):
        return []


def get_base_sha(ctx: ChangeContext, repo_root: Path | None = None) -> str:
    """Get the base SHA (parent of first commit in the change)."""
    if not ctx.commits:
        return ""
    try:
        result = subprocess.run(
            ["git", "rev-parse", f"{ctx.commits[0].sha}^"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(repo_root) if repo_root else None,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return ""


def get_head_sha(repo_root: Path | None = None) -> str:
    """Get the current HEAD SHA."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(repo_root) if repo_root else None,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return ""


def get_current_branch(repo_root: Path | None = None) -> str:
    """Get the current branch name."""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            timeout=5,
            cwd=str(repo_root) if repo_root else None,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return ""


def is_protected_branch(
    branch: str | None = None,
    protected: list[str] | None = None,
    repo_root: Path | None = None,
) -> bool:
    """Check if the current (or given) branch is a protected branch."""
    if branch is None:
        branch = get_current_branch(repo_root)
    if not branch:
        return False

    if protected is None:
        protected = ["main", "master"]

    import fnmatch

    for pattern in protected:
        if fnmatch.fnmatch(branch, pattern):
            return True
    return False
