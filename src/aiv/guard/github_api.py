"""
aiv/guard/github_api.py

GitHub API wrapper for AIV Guard.
Uses GITHUB_TOKEN and environment variables from the Actions runtime.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from ..lib.errors import GitHubAPIError
from .models import GuardContext


@dataclass
class ChangedFile:
    """A file changed in the PR."""

    filename: str
    status: str  # "added", "modified", "removed", "renamed"
    patch: str = ""


class GitHubAPI:
    """
    Minimal GitHub REST API client for guard operations.

    Uses only urllib (no external dependencies) so the guard
    can run in any GitHub Actions environment without pip install.
    """

    def __init__(self, token: str | None = None) -> None:
        self.token = token or os.environ.get("GITHUB_TOKEN", "")
        self.base_url = "https://api.github.com"

    def _request(self, url: str, accept: str = "application/vnd.github+json") -> Any:
        """Make an authenticated GET request."""
        headers = {
            "Accept": accept,
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        req = Request(url, headers=headers)
        try:
            with urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except HTTPError as e:
            raise GitHubAPIError(
                f"GitHub API request failed: {url} ({e.code})",
                status_code=e.code,
            ) from e

    def _request_bytes(self, url: str) -> bytes:
        """Make an authenticated GET request returning raw bytes."""
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        req = Request(url, headers=headers)
        try:
            with urlopen(req, timeout=60) as resp:
                result: bytes = resp.read()
                return result
        except HTTPError as e:
            raise GitHubAPIError(
                f"GitHub API request failed: {url} ({e.code})",
                status_code=e.code,
            ) from e

    @staticmethod
    def context_from_env() -> GuardContext:
        """
        Build GuardContext from GitHub Actions environment variables.

        Reads GITHUB_EVENT_PATH for the event payload, plus standard env vars.
        """
        event_path = os.environ.get("GITHUB_EVENT_PATH", "")
        event: dict[str, Any] = {}
        if event_path and Path(event_path).exists():
            event = json.loads(Path(event_path).read_text(encoding="utf-8"))

        pr = event.get("pull_request", {})
        repo_full = os.environ.get("GITHUB_REPOSITORY", "owner/repo")
        owner, repo = repo_full.split("/", 1) if "/" in repo_full else (repo_full, "")

        return GuardContext(
            pr_number=pr.get("number", 0),
            head_sha=pr.get("head", {}).get("sha", ""),
            base_sha=pr.get("base", {}).get("sha", ""),
            owner=owner,
            repo=repo,
            pr_body=pr.get("body", "") or "",
            is_draft=pr.get("draft", False),
            run_id=os.environ.get("GITHUB_RUN_ID", ""),
            run_url=(f"https://github.com/{repo_full}/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}"),
        )

    def list_pr_files(self, ctx: GuardContext) -> list[ChangedFile]:
        """List all files changed in the PR (handles pagination)."""
        files: list[ChangedFile] = []
        page = 1
        max_pages = 100

        while page <= max_pages:
            url = f"{self.base_url}/repos/{ctx.owner}/{ctx.repo}/pulls/{ctx.pr_number}/files?per_page=100&page={page}"
            try:
                data = self._request(url)
            except GitHubAPIError:
                break

            if not data:
                break

            for f in data:
                files.append(
                    ChangedFile(
                        filename=f.get("filename", ""),
                        status=f.get("status", ""),
                        patch=f.get("patch", "") or "",
                    )
                )

            if len(data) < 100:
                break
            page += 1

        return files

    def get_workflow_run(self, ctx: GuardContext, run_id: int) -> dict[str, Any] | None:
        """Fetch a workflow run by ID."""
        url = f"{self.base_url}/repos/{ctx.owner}/{ctx.repo}/actions/runs/{run_id}"
        try:
            result: dict[str, Any] = self._request(url)
            return result
        except GitHubAPIError:
            return None

    def list_run_artifacts(self, ctx: GuardContext, run_id: int) -> list[dict[str, Any]]:
        """List all artifacts for a workflow run."""
        artifacts: list[dict[str, Any]] = []
        page = 1
        max_pages = 20

        while page <= max_pages:
            url = (
                f"{self.base_url}/repos/{ctx.owner}/{ctx.repo}/actions/runs/{run_id}/artifacts?per_page=100&page={page}"
            )
            try:
                data = self._request(url)
            except GitHubAPIError:
                break

            batch = data.get("artifacts", [])
            artifacts.extend(batch)
            if len(batch) < 100:
                break
            page += 1

        return artifacts

    def download_artifact_zip(self, ctx: GuardContext, artifact_id: int) -> bytes:
        """Download an artifact as a zip file."""
        url = f"{self.base_url}/repos/{ctx.owner}/{ctx.repo}/actions/artifacts/{artifact_id}/zip"
        return self._request_bytes(url)

    def get_file_content(self, ctx: GuardContext, path: str, ref: str) -> str | None:
        """Get file content at a specific ref."""
        url = f"{self.base_url}/repos/{ctx.owner}/{ctx.repo}/contents/{path}?ref={ref}"
        try:
            data = self._request(url)
        except GitHubAPIError:
            return None

        if isinstance(data, list):
            return None
        if data.get("encoding") != "base64" or not data.get("content"):
            return None

        import base64

        return base64.b64decode(data["content"]).decode("utf-8")

    def search_code(self, ctx: GuardContext, query: str) -> int:
        """Search code in the repository. Returns total_count."""
        import urllib.parse

        q = urllib.parse.quote(f"{query} repo:{ctx.owner}/{ctx.repo}")
        url = f"{self.base_url}/search/code?q={q}&per_page=1"
        try:
            data = self._request(url)
            count: int = data.get("total_count", 0)
            return count
        except GitHubAPIError:
            return 0
