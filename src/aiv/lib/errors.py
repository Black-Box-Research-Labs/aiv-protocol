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


class PacketValidationError(AIVError):
    """
    Raised when a parsed packet fails validation rules.

    The packet was structurally valid but contains evidence or
    compliance violations (e.g., mutable links, zero-touch failures).
    """

    def __init__(self, message: str, rule_id: str | None = None):
        super().__init__(message)
        self.rule_id = rule_id


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


class EvidenceResolutionError(AIVError):
    """
    Raised when evidence artifacts cannot be resolved.

    This covers broken links, missing CI artifacts, and
    inaccessible external resources.
    """

    def __init__(self, message: str, url: str | None = None):
        super().__init__(message)
        self.url = url
