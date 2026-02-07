"""
aiv.guard — GitHub Action support for the AIV Protocol Suite.

Provides security utilities and reporting for automated PR enforcement.
"""

from .github_api import GitHubAPI
from .models import GuardContext, GuardFinding, GuardResult, GuardSeverity
from .runner import GuardRunner

__all__ = [
    "GuardContext",
    "GuardFinding",
    "GuardResult",
    "GuardRunner",
    "GuardSeverity",
    "GitHubAPI",
]
