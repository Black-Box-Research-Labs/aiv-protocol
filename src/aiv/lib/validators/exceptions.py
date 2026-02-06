"""
aiv/lib/validators/exceptions.py

Handlers for protocol exceptions (Addendum 2.3).
"""

from __future__ import annotations

import re

from ..models import (
    ArtifactLink,
    ValidationFinding,
    Severity,
    VerificationPacket,
)


class BootstrapExceptionHandler:
    """
    Handles the Bootstrap Exception for infrastructure PRs.

    When CI cannot run because the infrastructure doesn't exist yet,
    local evidence is accepted if:
    1. Reproducibility is guaranteed via code (Dockerfile, Terraform, etc.)
    2. A "Verifier's Key" command is provided
    """

    # File patterns that indicate infrastructure code
    INFRA_PATTERNS = [
        r"Dockerfile",
        r"docker-compose",
        r"terraform",
        r"\.tf$",
        r"ansible",
        r"cloudformation",
        r"k8s",
        r"kubernetes",
        r"helm",
    ]

    def is_bootstrap_pr(self, packet: VerificationPacket, file_list: list[str]) -> bool:
        """Detect if this PR is bootstrapping infrastructure."""
        for pattern in self.INFRA_PATTERNS:
            for file in file_list:
                if re.search(pattern, file, re.IGNORECASE):
                    return True

        # Also check claim descriptions
        bootstrap_keywords = ["bootstrap", "infrastructure", "initial setup", "first deploy"]
        for claim in packet.claims:
            if any(kw in claim.description.lower() for kw in bootstrap_keywords):
                return True

        return False

    def validate_bootstrap_evidence(
        self,
        packet: VerificationPacket
    ) -> list[ValidationFinding]:
        """
        Validate bootstrap-specific requirements.

        Requires:
        - Link to infrastructure code (Dockerfile, etc.)
        - Single-command reproducibility ("Verifier's Key")
        """
        errors: list[ValidationFinding] = []

        # Check for infrastructure code reference
        has_infra_ref = False
        for claim in packet.claims:
            if claim.evidence_class.value == "B":
                artifact_str = str(claim.artifact)
                if any(p in artifact_str.lower() for p in ["dockerfile", "terraform", ".tf"]):
                    has_infra_ref = True
                    break

        if not has_infra_ref:
            errors.append(ValidationFinding(
                rule_id="E007",
                severity=Severity.WARN,
                message="Bootstrap PRs should include Class B reference to infrastructure code",
                location="Packet-wide",
            ))

        # Check for single-command reproducibility
        has_single_command = False
        for claim in packet.claims:
            repro = claim.reproduction.strip()
            # Single command = no separators and starts with common commands
            if (
                ";" not in repro
                and " && " not in repro
                and any(repro.startswith(cmd) for cmd in ["make ", "docker ", "terraform "])
            ):
                has_single_command = True
                break

        if not has_single_command:
            errors.append(ValidationFinding(
                rule_id="E008",
                severity=Severity.WARN,
                message=(
                    "Bootstrap PRs should include a single-command 'Verifier's Key' "
                    "for reproducibility"
                ),
                suggestion="Example: 'make local-bootstrap' or 'docker compose up'",
            ))

        return errors


class FlakeReportHandler:
    """
    Handles the Flake Report exception for non-deterministic CI.

    When CI fails due to environmental issues (not code bugs),
    acceptance requires:
    1. Links to 3 CI runs for the same commit
    2. Different failure modes in each run (proves flakiness)
    3. Local green evidence
    """

    def validate_flake_claim(
        self,
        claim: object,
        ci_run_urls: list[str]
    ) -> list[ValidationFinding]:
        """
        Validate a flake report claim.

        Args:
            claim: The claim asserting flakiness
            ci_run_urls: URLs to the CI runs being compared
        """
        errors: list[ValidationFinding] = []

        if len(ci_run_urls) < 3:
            section_number = getattr(claim, "section_number", "?")
            errors.append(ValidationFinding(
                rule_id="E014",
                severity=Severity.BLOCK,
                message=f"Flake proof requires 3 CI runs, got {len(ci_run_urls)}",
                location=f"Section {section_number}",
                suggestion="Re-run CI twice more and link all 3 runs",
            ))

        return errors


class FastTrackHandler:
    """
    Handles Fast-Track protocol for trivial changes (Addendum 2.3).

    Documentation-only, styling, and config changes can use
    simplified evidence requirements.
    """

    def __init__(self, fast_track_patterns: list[str] | None = None):
        self.eligible_patterns = fast_track_patterns or [
            r"\.md$",
            r"\.txt$",
            r"\.gitignore$",
            r"\.editorconfig$",
            r"LICENSE",
            r"README",
            r"CHANGELOG",
        ]

    def is_fast_track_eligible(self, file_list: list[str]) -> bool:
        """Check if all changed files are eligible for fast-track."""
        for file in file_list:
            is_eligible = False
            for pattern in self.eligible_patterns:
                if re.search(pattern, file, re.IGNORECASE):
                    is_eligible = True
                    break

            if not is_eligible:
                return False

        return True

    def validate_fast_track(
        self,
        packet: VerificationPacket
    ) -> list[ValidationFinding]:
        """
        Validate fast-track packet.

        Fast-track still requires:
        - Intent alignment (Class E)
        - At least one claim (can be simplified)

        Does NOT require:
        - CI evidence
        - Zero-touch compliance (can be "Visual inspection")
        """
        errors: list[ValidationFinding] = []

        # Check for "Fast-Track" tag
        has_fast_track_tag = False
        for claim in packet.claims:
            if "fast-track" in claim.description.lower():
                has_fast_track_tag = True
                break

        if not has_fast_track_tag:
            errors.append(ValidationFinding(
                rule_id="E005",
                severity=Severity.INFO,
                message=(
                    "This appears to be a trivial change eligible for Fast-Track. "
                    "Tag a claim with 'Fast-Track (Trivial)' to use simplified requirements."
                ),
            ))

        return errors
