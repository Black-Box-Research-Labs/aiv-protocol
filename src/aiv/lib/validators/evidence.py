"""
aiv/lib/validators/evidence.py

Evidence class-specific validation rules.
"""

from __future__ import annotations

import re

from ..models import (
    ArtifactLink,
    Claim,
    EvidenceClass,
    ValidationFinding,
    VerificationPacket,
)
from .base import BaseValidator


class EvidenceValidator(BaseValidator):
    """
    Validates evidence based on class-specific requirements.

    Each evidence class has different requirements for what
    constitutes valid proof.
    """

    def validate(self, packet: VerificationPacket) -> list[ValidationFinding]:
        """Validate all claims according to their evidence class."""
        errors: list[ValidationFinding] = []

        for claim in packet.claims:
            class_errors = self._validate_claim_evidence(claim)
            errors.extend(class_errors)

        # Check for required Class F on bug fixes
        if self._is_bug_fix(packet) and not packet.has_provenance_evidence:
            errors.append(
                self._make_finding(
                    rule_id="E010",
                    severity="block",
                    message="Bug fixes require Class F (Provenance) evidence",
                    location="Packet-wide",
                    suggestion=(
                        "Add a claim showing that existing tests were preserved. "
                        "Include a link to the test file diff and CI run."
                    ),
                )
            )

        return errors

    def _validate_claim_evidence(self, claim: Claim) -> list[ValidationFinding]:
        """Validate a single claim's evidence against its class requirements."""
        errors: list[ValidationFinding] = []

        # Dispatch to class-specific validator
        validators = {
            EvidenceClass.EXECUTION: self._validate_execution,
            EvidenceClass.REFERENTIAL: self._validate_referential,
            EvidenceClass.NEGATIVE: self._validate_negative,
            EvidenceClass.DIFFERENTIAL: self._validate_differential,
            EvidenceClass.INTENT: self._validate_intent,
            EvidenceClass.PROVENANCE: self._validate_provenance,
        }

        validator = validators.get(claim.evidence_class)
        if validator:
            errors.extend(validator(claim))

        return errors

    def _validate_execution(self, claim: Claim) -> list[ValidationFinding]:
        """
        Class A: Execution Evidence

        Requirements:
        - Must link to CI artifact (preferred) or automation output
        - UI evidence must show state transition (GIF/video)
        - Performance evidence must be differential A/B
        - Code blob links are incoherent for execution evidence
        """
        errors: list[ValidationFinding] = []

        # Check for CI link
        if isinstance(claim.artifact, ArtifactLink):
            if claim.artifact.link_type not in ("github_actions", "external"):
                # Not a CI link - warn but allow
                if "performance" in claim.description.lower():
                    errors.append(
                        self._make_finding(
                            rule_id="E013",
                            severity="block",
                            message="Performance claims require CI-based differential benchmarks",
                            location=f"Section {claim.section_number}",
                            suggestion=("Link to a CI job that runs benchmarks on both main and feature branches"),
                        )
                    )
                elif "ui" in claim.description.lower() or "visual" in claim.description.lower():
                    errors.append(
                        self._make_finding(
                            rule_id="E012",
                            severity="warn",
                            message=("UI evidence should show state transition (GIF/video preferred)"),
                            location=f"Section {claim.section_number}",
                        )
                    )
                elif claim.artifact.link_type == "github_blob":
                    errors.append(
                        self._make_finding(
                            rule_id="E020",
                            severity="warn",
                            message=(
                                "Class A (Execution) evidence links to a code file, "
                                "not a CI run. Execution evidence should prove "
                                "the code was *run*, not just that it *exists*."
                            ),
                            location=f"Section {claim.section_number}",
                            suggestion=(
                                "Link to a GitHub Actions run (e.g. /actions/runs/12345) or external CI artifact."
                            ),
                        )
                    )

        return errors

    def _validate_referential(self, claim: Claim) -> list[ValidationFinding]:
        """
        Class B: Referential Evidence

        Requirements:
        - Must link to specific file/line
        - Must be SHA-pinned
        """
        errors: list[ValidationFinding] = []

        if isinstance(claim.artifact, ArtifactLink):
            if claim.artifact.link_type != "github_blob":
                errors.append(
                    self._make_finding(
                        rule_id="E015",
                        severity="warn",
                        message="Class B evidence should link directly to code (GitHub blob)",
                        location=f"Section {claim.section_number}",
                    )
                )
        elif isinstance(claim.artifact, str):
            # Check if it looks like a file reference or scope inventory
            file_ref_keywords = [
                "line",
                "file",
                "path",
                "created",
                "modified",
                "deleted",
                "scope",
                "inventory",
                "added",
                "removed",
                "changed",
            ]
            if not any(x in claim.artifact.lower() for x in file_ref_keywords):
                errors.append(
                    self._make_finding(
                        rule_id="E016",
                        severity="warn",
                        message="Class B evidence should reference specific file locations",
                        location=f"Section {claim.section_number}",
                    )
                )

        return errors

    def _validate_negative(self, claim: Claim) -> list[ValidationFinding]:
        """
        Class C: Negative Evidence

        Requirements:
        - Must demonstrate absence of something
        - For refactoring, entire regression suite must pass
        """
        errors: list[ValidationFinding] = []

        # Check description mentions what is absent
        negative_keywords = ["not", "no ", "absence", "removed", "clean", "without"]
        has_negative_framing = any(kw in claim.description.lower() for kw in negative_keywords)

        if not has_negative_framing:
            errors.append(
                self._make_finding(
                    rule_id="E017",
                    severity="warn",
                    message="Class C evidence should clearly state what is NOT present",
                    location=f"Section {claim.section_number}",
                    suggestion="Frame claim as 'Does not contain X' or 'Absence of Y'",
                )
            )

        return errors

    def _validate_differential(self, claim: Claim) -> list[ValidationFinding]:
        """
        Class D: Differential Evidence

        Requirements:
        - Must show actual state change (not just logs)
        - Must be generated by automated script
        - Verifier must NOT run manually (Zero-Touch)
        """
        errors: list[ValidationFinding] = []

        # Check that reproduction doesn't require manual DB access
        manual_state_keywords = ["sqlite3", "psql", "mysql", "mongo", "query"]
        repro_lower = claim.reproduction.lower()

        if any(kw in repro_lower for kw in manual_state_keywords):
            errors.append(
                self._make_finding(
                    rule_id="E018",
                    severity="block",
                    message="Class D evidence must not require manual database queries",
                    location=f"Section {claim.section_number}",
                    suggestion=(
                        "Generate state evidence as a CI artifact. "
                        "Example: Script that dumps relevant state to JSON file."
                    ),
                )
            )

        return errors

    def validate_file_type_triggers(
        self,
        packet: VerificationPacket,
        changed_files: list[str],
    ) -> list[ValidationFinding]:
        """
        File-type-aware triggers for Class D evidence.

        Inspects changed files and demands specific evidence types
        when high-risk file patterns are detected.
        """
        errors: list[ValidationFinding] = []

        # Define file-type triggers: pattern → (required evidence, message)
        triggers: list[tuple[list[str], str, str, str]] = [
            # (extensions/patterns, evidence_keyword, rule_message, suggestion)
            (
                [".sql", ".migration", "alembic/", "migrations/"],
                "schema",
                "Database changes detected — Class D must include schema diff or migration plan",
                "Add a before/after schema diff or link to the migration plan artifact",
            ),
            (
                ["pyproject.toml", "setup.py", "setup.cfg", "requirements.txt", "package.json", "Cargo.toml"],
                "dependenc",
                "Dependency file changes detected — Class D must include dependency analysis",
                "Add a dependency diff showing added/removed/changed packages and version ranges",
            ),
            (
                [".proto", "openapi.yaml", "openapi.json", "swagger.", "schema.graphql"],
                "api",
                "API schema changes detected — Class D must include API compatibility analysis",
                "Add before/after API diff showing breaking vs non-breaking changes",
            ),
            (
                ["Dockerfile", "docker-compose", ".dockerignore", "k8s/", "helm/"],
                "deploy",
                "Infrastructure changes detected — Class D should include deployment diff",
                "Show before/after container or orchestration config changes",
            ),
        ]

        # Collect all Class D evidence text from the packet
        class_d_text = ""
        for claim in packet.claims:
            if claim.evidence_class == EvidenceClass.DIFFERENTIAL:
                class_d_text += " " + claim.description.lower()
                if isinstance(claim.artifact, str):
                    class_d_text += " " + claim.artifact.lower()
                elif isinstance(claim.artifact, ArtifactLink):
                    class_d_text += " " + str(claim.artifact.url).lower()

        for extensions, keyword, message, suggestion in triggers:
            # Check if any changed file matches this trigger
            triggered = False
            trigger_files = []
            for f in changed_files:
                f_lower = f.lower()
                for ext in extensions:
                    if (ext.startswith(".") and f_lower.endswith(ext)) or (not ext.startswith(".") and ext in f_lower):
                        triggered = True
                        trigger_files.append(f)
                        break

            if not triggered:
                continue

            # Check if Class D section exists and mentions the expected keyword
            has_class_d = any(c.evidence_class == EvidenceClass.DIFFERENTIAL for c in packet.claims)

            if not has_class_d:
                errors.append(
                    self._make_finding(
                        rule_id="E021",
                        severity="warn",
                        message=f"{message} (triggered by: {', '.join(trigger_files[:3])})",
                        location="Packet-wide",
                        suggestion=suggestion,
                    )
                )
            elif keyword not in class_d_text:
                errors.append(
                    self._make_finding(
                        rule_id="E022",
                        severity="info",
                        message=(
                            f"Class D evidence present but does not mention '{keyword}' — "
                            f"verify it covers: {', '.join(trigger_files[:3])}"
                        ),
                        location="Packet-wide",
                        suggestion=suggestion,
                    )
                )

        return errors

    def _validate_intent(self, claim: Claim) -> list[ValidationFinding]:
        """
        Class E: Intent Alignment

        Requirements:
        - Must link to spec/task/design doc
        - Must be immutable (SHA-pinned)
        """
        errors: list[ValidationFinding] = []

        # Note: Primary Class E validation happens in IntentSection
        # This handles additional Class E claims if any
        if isinstance(claim.artifact, ArtifactLink):
            if not claim.artifact.is_immutable:
                errors.append(
                    self._make_finding(
                        rule_id="E004",
                        severity="block",
                        message="Class E links must be SHA-pinned (immutable)",
                        location=f"Section {claim.section_number}",
                    )
                )

        return errors

    def _validate_provenance(self, claim: Claim) -> list[ValidationFinding]:
        """
        Class F: Provenance Evidence

        Requirements:
        - Must show test file diff (no deleted assertions)
        - Must link to full regression suite CI run
        - Must include justification if tests modified
        """
        errors: list[ValidationFinding] = []

        # Check for justification if this is a test *modification* claim.
        # Provenance claims asserting no tests were changed (negative framing)
        # don't need additional justification — the absence IS the evidence.
        test_keywords = ["test", "assertion", "spec"]
        is_test_related = any(kw in claim.description.lower() for kw in test_keywords)

        negative_keywords = ["no ", "not ", "without", "preserved", "unchanged", "unmodified"]
        has_negative_framing = any(kw in claim.description.lower() for kw in negative_keywords)

        if is_test_related and not has_negative_framing and not claim.justification:
            errors.append(
                self._make_finding(
                    rule_id="E011",
                    severity="warn",
                    message="Class F claims about test modifications should include justification",
                    location=f"Section {claim.section_number}",
                    suggestion="Add **Justification:** explaining why test changes are valid",
                )
            )

        return errors

    def _is_bug_fix(self, packet: VerificationPacket) -> bool:
        """Heuristic to detect if this PR is a bug fix."""
        # Use word-boundary patterns to avoid false positives on substrings
        # like "prefix" matching "fix" or "tissue" matching "issue".
        indicators = [
            r"\bfix(?:ed|es|ing)?\b",
            r"\bbug(?:s|fix)?\b",
            r"\bissue\s*#?\d+",
            r"\bpatch(?:ed|es)?\b",
            r"\bresolve[ds]?\b",
            r"\bcloses\s*#\d+",
            r"\bhotfix\b",
        ]
        combined = "|".join(indicators)

        # Check intent description
        intent_text = packet.intent.verifier_check.lower()
        if re.search(combined, intent_text):
            return True

        # Check claim descriptions
        for claim in packet.claims:
            if re.search(combined, claim.description.lower()):
                return True

        return False
