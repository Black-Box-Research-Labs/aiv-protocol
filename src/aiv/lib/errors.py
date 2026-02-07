"""
aiv.lib.errors — Exception hierarchy for the AIV Protocol Suite.

All exceptions inherit from AIVError to allow broad catching.
Specific exceptions map to distinct failure modes in the validation pipeline.
"""

from __future__ import annotations


class AIVError(Exception):
    """Base exception for all AIV Protocol errors."""


class PacketParseError(AIVError):
    """
    Raised when a Verification Packet cannot be parsed.

    This indicates the markdown is missing required structural elements
    (header, intent section, claims) rather than validation failures.
    """


class ConfigurationError(AIVError):
    """
    Raised when AIV configuration is invalid or missing.

    This covers .aiv.yml parse failures and invalid option combinations.
    """


class GitHubAPIError(AIVError):
    """
    Raised when GitHub API calls fail.

    Wraps HTTP errors, rate limits, and authentication failures
    from the GitHub REST API.
    """

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


