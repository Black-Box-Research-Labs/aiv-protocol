"""
aiv/guard/models.py

Data models for the AIV Guard — GitHub Action PR validation.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class GuardSeverity(str, Enum):
    """Finding severity levels for guard output."""

    BLOCK = "BLOCK"
    WARN = "WARN"
    INFO = "INFO"


class DecisionType(str, Enum):
    """Attestation decision types."""

    COMPLIANT = "COMPLIANT"
    CONDITIONAL = "CONDITIONAL"
    NON_COMPLIANT = "NON-COMPLIANT"


class OverallResult(str, Enum):
    """Overall validation result."""

    PASS = "PASS"
    FAIL = "FAIL"


@dataclass
class GuardFinding:
    """A single guard finding (maps to JS findings array)."""

    id: str
    severity: GuardSeverity
    rule_id: str
    description: str
    remediation: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "severity": self.severity.value,
            "rule_id": self.rule_id,
            "description": self.description,
            "remediation": self.remediation,
        }


@dataclass
class RuleResult:
    """Result for a single validation rule."""

    rule_id: str
    result: str  # "PASS", "FAIL", "SKIP"
    finding_id: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d: dict[str, Any] = {"rule_id": self.rule_id, "result": self.result}
        if self.result == "FAIL" and self.finding_id:
            d["finding_id"] = self.finding_id
        return d


@dataclass
class EvidenceClassResult:
    """Validation result for a single evidence class."""

    evidence_class: str  # "A", "B", "C", "D", "E", "F"
    required: bool
    present: bool
    valid: bool
    findings: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "class": self.evidence_class,
            "required": self.required,
            "present": self.present,
            "valid": self.valid,
            "findings": self.findings,
        }


@dataclass
class GuardContext:
    """Context from GitHub Actions environment."""

    pr_number: int
    head_sha: str
    base_sha: str
    owner: str
    repo: str
    pr_body: str
    is_draft: bool = False
    run_id: str = ""
    run_url: str = ""

    @property
    def full_repo(self) -> str:
        return f"{self.owner}/{self.repo}"


@dataclass
class GuardResult:
    """Complete guard validation output (maps to aiv_validation_result.json)."""

    validator_id: str = "aiv-guard@2.0.0"
    packet_id: str = ""
    repository: str = ""
    pr_id: int = 0
    head_sha: str = ""
    validated_at: str = ""
    overall_result: OverallResult = OverallResult.FAIL
    compliance_level: str = "L1"
    risk_tier_validated: str = "R0"
    evidence_class_results: list[EvidenceClassResult] = field(default_factory=list)
    validation_rule_results: list[RuleResult] = field(default_factory=list)
    findings: list[GuardFinding] = field(default_factory=list)

    # Computed from findings
    canonical_enabled: bool = False

    def add_finding(
        self,
        rule_id: str,
        severity: GuardSeverity,
        description: str,
        remediation: str = "",
    ) -> GuardFinding:
        """Add a finding and return it."""
        fid = f"F-{rule_id}-{severity.value}-{len(self.findings) + 1}"
        finding = GuardFinding(
            id=fid,
            severity=severity,
            rule_id=rule_id,
            description=description,
            remediation=remediation,
        )
        self.findings.append(finding)
        return finding

    def add_block(self, rule_id: str, description: str, remediation: str = "") -> GuardFinding:
        """Shorthand to add a BLOCK finding and set overall to FAIL."""
        self.overall_result = OverallResult.FAIL
        return self.add_finding(rule_id, GuardSeverity.BLOCK, description, remediation)

    def add_warn(self, rule_id: str, description: str, remediation: str = "") -> GuardFinding:
        """Shorthand to add a WARN finding."""
        return self.add_finding(rule_id, GuardSeverity.WARN, description, remediation)

    def upsert_rule_result(self, rule_id: str, result: str, finding_id: str | None = None) -> None:
        """Insert or update a rule result."""
        for rr in self.validation_rule_results:
            if rr.rule_id == rule_id:
                rr.result = result
                if result == "FAIL" and finding_id:
                    rr.finding_id = finding_id
                return
        self.validation_rule_results.append(RuleResult(rule_id, result, finding_id))

    @property
    def block_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == GuardSeverity.BLOCK)

    @property
    def warn_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == GuardSeverity.WARN)

    @property
    def info_count(self) -> int:
        return sum(1 for f in self.findings if f.severity == GuardSeverity.INFO)

    def finalize(self) -> None:
        """Compute overall result and compliance level from findings."""
        if self.block_count > 0:
            self.overall_result = OverallResult.FAIL
            self.compliance_level = "NON-COMPLIANT"
        else:
            self.overall_result = OverallResult.PASS

    def to_dict(self) -> dict[str, Any]:
        """Serialize to the aiv_validation_result.json format."""
        return {
            "validation_result": {
                "validator_id": self.validator_id,
                "packet_id": self.packet_id,
                "repository": self.repository,
                "pr_id": self.pr_id,
                "head_sha": self.head_sha,
                "validated_at": self.validated_at,
                "overall_result": self.overall_result.value,
                "compliance_level": self.compliance_level,
                "risk_tier_validated": self.risk_tier_validated,
                "evidence_class_results": [e.to_dict() for e in self.evidence_class_results],
                "validation_rule_results": [r.to_dict() for r in self.validation_rule_results],
                "findings": [f.to_dict() for f in self.findings],
                "block_count": self.block_count,
                "warn_count": self.warn_count,
                "info_count": self.info_count,
            }
        }


# Regex helpers ported from the JS guard
HEX_SHA_40_OR_64 = re.compile(r"^[0-9a-f]{40}([0-9a-f]{24})?$", re.IGNORECASE)
MUTABLE_BRANCH_PATTERN = re.compile(r"/(blob|tree)/(main|master|develop|dev|staging)/")
GITHUB_BLOB_OR_TREE = re.compile(r"github\.com/[^/]+/[^/]+/(blob|tree)/")
GITHUB_BLOB_FULL_SHA = re.compile(
    r"github\.com/[^/]+/[^/]+/(blob|tree)/[0-9a-f]{40}([0-9a-f]{24})?(/|$)", re.IGNORECASE
)
GITHUB_ACTIONS_RUN = re.compile(r"github\.com/[^/]+/[^/]+/actions/runs/\d+")
LINE_ANCHOR = re.compile(r"#L\d+(-L\d+)?$")
