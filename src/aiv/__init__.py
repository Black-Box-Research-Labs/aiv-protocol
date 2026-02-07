"""
AIV Protocol Suite — Auditable Verification Standard for AI-Assisted Code Changes.

This package provides the core library (aiv-lib), CLI tooling (aiv-cli),
and GitHub Action support (aiv-guard) for enforcing the AIV Verification Protocol.
"""

__version__ = "1.0.0"

from aiv.lib.config import AIVConfig
from aiv.lib.models import (
    ArtifactLink,
    Claim,
    EvidenceClass,
    IntentSection,
    RiskTier,
    Severity,
    ValidationFinding,
    ValidationResult,
    ValidationStatus,
    VerificationPacket,
)
from aiv.lib.parser import PacketParser
from aiv.lib.validators.pipeline import ValidationPipeline

__all__ = [
    "AIVConfig",
    "ArtifactLink",
    "Claim",
    "EvidenceClass",
    "IntentSection",
    "PacketParser",
    "RiskTier",
    "Severity",
    "ValidationFinding",
    "ValidationPipeline",
    "ValidationResult",
    "ValidationStatus",
    "VerificationPacket",
]
