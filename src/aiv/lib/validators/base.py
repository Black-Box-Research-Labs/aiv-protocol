"""
aiv/lib/validators/base.py

Validator protocol defining the interface all validators must implement.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Protocol, runtime_checkable

from ..models import ValidationFinding, VerificationPacket


@runtime_checkable
class Validator(Protocol):
    """
    Protocol that all AIV validators must satisfy.

    Each validator inspects a VerificationPacket and returns
    a list of findings (errors, warnings, or info).
    """

    def validate(self, packet: VerificationPacket) -> list[ValidationFinding]:
        """
        Validate a packet and return findings.

        Args:
            packet: The parsed verification packet to validate.

        Returns:
            List of validation findings (may be empty if valid).
        """
        ...


class BaseValidator(ABC):
    """
    Abstract base class providing common validator utilities.

    Concrete validators should inherit from this and implement validate().
    """

    @abstractmethod
    def validate(self, packet: VerificationPacket) -> list[ValidationFinding]:
        """Validate a packet and return findings."""
        ...

    def _make_finding(
        self,
        rule_id: str,
        severity: str,
        message: str,
        location: str | None = None,
        suggestion: str | None = None,
    ) -> ValidationFinding:
        """Helper to construct a ValidationFinding with less boilerplate."""
        from ..models import Severity

        return ValidationFinding(
            rule_id=rule_id,
            severity=Severity(severity),
            message=message,
            location=location,
            suggestion=suggestion,
        )
