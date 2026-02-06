# AIV Protocol Suite: Definitive Technical Specification

**Document ID:** AIV-SUITE-SPEC-V1.0-CANONICAL
**Version:** 1.0.0
**Status:** Canonical Reference Implementation
**Date:** 2025-12-19
**Purpose:** To provide the complete, authoritative technical specification for automating the AIV Verification Protocol, suitable for implementation as an industry-standard open-source project.

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Foundational Protocol Reference](#2-foundational-protocol-reference)
3. [System Architecture](#3-system-architecture)
4. [Data Models](#4-data-models)
5. [Core Algorithms](#5-core-algorithms)
6. [Component Specifications](#6-component-specifications)
7. [Implementation Reference](#7-implementation-reference)
8. [Security Model](#8-security-model)
9. [Edge Case Handling](#9-edge-case-handling)
10. [Testing Strategy](#10-testing-strategy)
11. [Deployment & Integration](#11-deployment--integration)
12. [Application to PR #2](#12-application-to-pr-2)
13. [Appendices](#13-appendices)

---

## 1. Executive Summary

### 1.1 Problem Statement

The Architect-Implementer-Verifier (AIV) model provides a rigorous framework for software verification, but manual enforcement creates three critical failure modes:

1. **Verification Toil:** Human verifiers spend cognitive energy on mechanical checks (running scripts, checking links) instead of deep logic analysis.
2. **Inconsistent Enforcement:** Without automation, protocol adherence varies by reviewer mood, time pressure, and familiarity.
3. **Evidence Drift:** Claims made in PRs have no automated validation against actual artifacts.

### 1.2 Solution Overview

The **AIV Protocol Suite** is a standalone automation system that enforces the AIV Verification Protocol (v2.0 + Addendums 2.1-2.7) on GitHub Pull Requests. It consists of:

| Component | Role                                    | Deployment      |
| --------- | --------------------------------------- | --------------- |
| aiv-lib   | Core validation logic and data models   | Python library  |
| aiv-cli   | Developer tooling for packet generation | CLI application |
| aiv-guard | Automated PR enforcement                | GitHub Action   |
| aiv-api   | Optional webhook/reporting service      | REST API        |

### 1.3 Design Principles

These principles are non-negotiable constraints on all implementation decisions:

1. **Zero-Touch Enforcement:** The system must never require the human verifier to execute code locally. All execution evidence must be artifact-based.

2. **Falsifiability:** Every validation rule must produce a deterministic pass/fail result with explicit reasoning. No "soft warnings" for protocol violations.

3. **Defense in Depth:** The system assumes adversarial inputs. All external data (PR bodies, URLs, CI responses) is untrusted until validated.

4. **Separation of Concerns:** The AIV Protocol Suite validates _evidence quality_, not _code quality_. It gates PRs for SVP (Systematic Verifier Protocol) readiness, not correctness.

5. **Auditability:** Every validation decision must produce a structured audit trail suitable for compliance and debugging.

### 1.4 Success Criteria

| Metric              | Target                                | Measurement Method          |
| ------------------- | ------------------------------------- | --------------------------- |
| Protocol Compliance | 100% of merged PRs have valid packets | Audit log analysis          |
| Validation Latency  | P95 < 30 seconds                      | GitHub Action timing        |
| False Positive Rate | < 2%                                  | Manual review of rejections |
| False Negative Rate | 0% for critical rules                 | Adversarial testing         |
| Security Incidents  | 0                                     | Security audit              |

---

## 2. Foundational Protocol Reference

This section provides a condensed, machine-parseable reference of the AIV Protocol v2.0 + Addendums. The full prose documents remain authoritative; this section extracts the rules into implementable specifications.

### 2.1 Evidence Class Taxonomy

Every claim in a Verification Packet must be supported by evidence from exactly one of these classes:

```yaml
evidence_classes:
  A:
    name: "Execution Evidence"
    description: "Raw, unedited logs, screenshots, or metrics from a live run"
    proves: "Behavior"
    required_artifacts:
      - CI job permalink (preferred)
      - Automated script output (acceptable)
      - Screenshot/recording (UI only)
    validation_rules:
      - Must link to immutable artifact (SHA-pinned or artifact ID)
      - For UI: Must be GIF/video showing state transition (Addendum 2.2)
      - For performance: Must be differential A/B in same CI context (Addendum 2.2)

  B:
    name: "Referential Evidence"
    description: "Direct file paths and line numbers"
    proves: "Structure"
    required_artifacts:
      - GitHub blob permalink with line range
      - Diff view permalink
    validation_rules:
      - Must include specific line numbers or ranges
      - Must be SHA-pinned (no branch references)

  C:
    name: "Negative Evidence"
    description: "Clean diffs or searches showing absence of defect"
    proves: "Safety and non-regression"
    required_artifacts:
      - grep/search command output
      - Diff showing removal of problematic code
      - CI run showing regression suite passes
    validation_rules:
      - Must demonstrate what is NOT present
      - For refactoring: entire regression suite must pass

  D:
    name: "State Evidence"
    description: "Database queries, file dumps, or API responses"
    proves: "Impact on persistent state"
    required_artifacts:
      - Query output (as CI artifact, not manual paste)
      - API response capture
      - File diff showing state change
    validation_rules:
      - Must be generated by automated script
      - Must be reproducible via linked script
      - Verifier must NOT run the script manually (Zero-Touch)

  E:
    name: "Intent Alignment"
    description: "Links to originating specification"
    proves: "Correct problem is being solved"
    required_artifacts:
      - Task tracker link (GitHub Issue, Jira, etc.)
      - Design document permalink
      - Architecture diagram reference
    validation_rules:
      - MANDATORY for every packet (Addendum 2.1)
      - Must be SHA-pinned for docs (no mutable branches)
      - Must appear as Section 0

  F:
    name: "Conservation Evidence"
    description: "Proof that existing constraints are preserved"
    proves: "Non-regression and anti-cheat"
    required_artifacts:
      - Test file diff showing no deleted assertions
      - Full regression suite CI run
      - Justification for any test modifications
    validation_rules:
      - Required for all bug fixes (Addendum 2.4)
      - Must show test file history if tests modified
      - Deleted assertions require explicit justification
```

### 2.2 Verification Packet Schema

The Verification Packet is the structured evidence document attached to every PR. This schema defines the required format:

```yaml
packet_schema:
  version: "2.1"

  header:
    pattern: "# AIV Verification Packet"
    version_pattern: "\\(v[\\d.]+\\)"
    required: true

  sections:
    - id: 0
      name: "Intent Alignment"
      required: true
      evidence_class: E
      fields:
        - name: "Class E Evidence"
          required: true
          type: url
          validation: immutable_reference
        - name: "Verifier Check"
          required: true
          type: text
          min_length: 10

    - id: "1+"
      name: "Claim"
      required: true
      min_count: 1
      fields:
        - name: "Claim"
          location: section_title
          required: true
          type: text
          min_length: 10
        - name: "Evidence Class"
          required: true
          type: enum
          values: [A, B, C, D, E, F]
        - name: "Evidence Artifact"
          required: true
          type: url_or_text
          validation: evidence_class_specific
        - name: "Reproduction"
          required: true
          type: text
          validation: zero_touch_compliant

  footer:
    pattern: "_This packet certifies.*_"
    required: false
```

### 2.3 Validation Rules Matrix

This matrix maps each Addendum to specific, testable rules:

| Rule ID | Source | Description                             | Severity | Auto-Fixable |
| ------- | ------ | --------------------------------------- | -------- | ------------ |
| E001    | v2.0   | Packet header must exist                | BLOCK    | No           |
| E002    | 2.1    | Section 0 (Intent) must exist           | BLOCK    | No           |
| E003    | 2.1    | Class E link must be present            | BLOCK    | No           |
| E004    | 2.2    | Class E link must be immutable (SHA)    | BLOCK    | No           |
| E005    | v2.0   | At least one Claim section required     | BLOCK    | No           |
| E006    | v2.0   | Each claim must have Evidence Class     | BLOCK    | No           |
| E007    | v2.0   | Each claim must have Evidence Artifact  | BLOCK    | No           |
| E008    | 2.7    | Reproduction must be Zero-Touch         | WARN     | Yes          |
| E009    | 2.2    | All artifact links must be immutable    | BLOCK    | No           |
| E010    | 2.4    | Bug fixes must include Class F evidence | BLOCK    | No           |
| E011    | 2.4    | Test modifications must be justified    | BLOCK    | No           |
| E012    | 2.2    | UI evidence must show state transition  | WARN     | No           |
| E013    | 2.2    | Performance claims need A/B CI evidence | BLOCK    | No           |
| E014    | 2.3    | Flaky CI needs 3-run proof              | WARN     | No           |
| E015    | 2.5    | Spec changes must be atomic with code   | WARN     | No           |

### 2.4 Zero-Touch Compliance Specification

The Zero-Touch mandate (Addendum 2.7) requires specific analysis of reproduction instructions:

```yaml
zero_touch_rules:
  prohibited_patterns:
    - pattern: "^(git clone|git checkout|git pull)"
      reason: "Requires local repository operations"
    - pattern: "(npm|yarn|pip|poetry|uv) install"
      reason: "Requires local dependency installation"
    - pattern: "(python|node|npm run|yarn|pytest|cargo|go run)"
      reason: "Requires local code execution"
    - pattern: "^cd\\s+"
      reason: "Requires local directory navigation"
    - pattern: "(docker|podman) run"
      reason: "Requires local container execution"
    - pattern: "open (browser|terminal|app)"
      reason: "Requires manual GUI interaction"
    - pattern: "click|tap|press|select"
      reason: "Requires manual GUI interaction"

  allowed_patterns:
    - "N/A"
    - "CI Automation"
    - "See CI artifact"
    - "Link above"
    - "Automated via"
    - url_pattern # Any HTTPS URL

  multi_step_detection:
    separators: [";", " && ", " then ", "\\d+\\.", "step \\d"]
    threshold: 1 # More than 1 step = high friction

  severity:
    prohibited_pattern_match: BLOCK
    multi_step_detected: WARN
```

---

## 3. System Architecture

### 3.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AIV Protocol Suite                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌────────────┐│
│  │   aiv-cli    │    │  aiv-guard   │    │   aiv-api    │    │  aiv-lib   ││
│  │              │    │              │    │              │    │            ││
│  │ • generate   │    │ • GitHub     │    │ • Webhooks   │    │ • Models   ││
│  │ • check      │    │   Action     │    │ • Reporting  │    │ • Parser   ││
│  │ • init       │    │ • Status     │    │ • Metrics    │    │ • Validate ││
│  │              │    │   Checks     │    │              │    │ • Analyze  ││
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘    └─────┬──────┘│
│         │                   │                   │                   │       │
│         └───────────────────┴───────────────────┴───────────────────┘       │
│                                     │                                        │
│                            ┌────────┴────────┐                              │
│                            │   Shared Core   │                              │
│                            │                 │                              │
│                            │ • Evidence      │                              │
│                            │   Validators    │                              │
│                            │ • Link          │                              │
│                            │   Analyzers     │                              │
│                            │ • Anti-Cheat    │                              │
│                            │   Scanner       │                              │
│                            │ • Friction      │                              │
│                            │   Calculator    │                              │
│                            └─────────────────┘                              │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                            External Systems                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐                   │
│  │   GitHub     │    │   CI/CD      │    │   Task       │                   │
│  │   API        │    │   Systems    │    │   Trackers   │                   │
│  │              │    │              │    │              │                   │
│  │ • PRs        │    │ • Actions    │    │ • Issues     │                   │
│  │ • Commits    │    │ • Artifacts  │    │ • Jira       │                   │
│  │ • Diffs      │    │ • Logs       │    │ • Linear     │                   │
│  │ • Statuses   │    │              │    │              │                   │
│  └──────────────┘    └──────────────┘    └──────────────┘                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Component Interaction Flow

```mermaid
sequenceDiagram
    autonumber
    participant Dev as Developer
    participant CLI as aiv-cli
    participant GH as GitHub
    participant Guard as aiv-guard
    participant Lib as aiv-lib
    participant API as GitHub API

    Note over Dev,API: Phase 1: Packet Generation (Developer Responsibility)

    Dev->>CLI: aiv generate --pr 2
    CLI->>API: GET /repos/{owner}/{repo}/pulls/2
    API-->>CLI: PR metadata + diff
    CLI->>API: GET /repos/{owner}/{repo}/actions/runs?head_sha={sha}
    API-->>CLI: CI run data
    CLI->>Lib: generate_packet(pr_data, ci_data)
    Lib-->>CLI: Formatted markdown packet
    CLI-->>Dev: Packet ready for PR description

    Dev->>GH: Update PR description with packet

    Note over Dev,API: Phase 2: Automated Validation (Guard Responsibility)

    GH->>Guard: pull_request event (opened/edited/synchronize)
    Guard->>API: GET PR body + diff
    API-->>Guard: PR data
    Guard->>Lib: parse_packet(body)
    Lib-->>Guard: Parsed packet or parse errors

    alt Packet Missing or Malformed
        Guard->>GH: POST check_run (failure)
        Guard->>GH: POST comment (instructions)
    else Packet Valid Structure
        Guard->>Lib: validate_evidence(packet)
        Lib->>API: Verify artifact links exist
        API-->>Lib: Link validation results
        Lib->>Lib: Check immutability (SHA detection)
        Lib->>Lib: Analyze zero-touch compliance
        Lib-->>Guard: ValidationResult

        Guard->>Lib: scan_anticheat(diff)
        Lib-->>Guard: AntiCheatResult

        alt All Validations Pass
            Guard->>GH: POST check_run (success)
            Note over GH: PR ready for human SVP
        else Validation Failures
            Guard->>GH: POST check_run (failure)
            Guard->>GH: POST comment (detailed errors)
        end
    end

    Note over Dev,API: Phase 3: Human Verification (SVP - Out of Scope for Automation)

    Dev->>GH: Human reviews logic, performs mental trace
    Dev->>GH: Ownership commit (renames, docstrings)
    Dev->>GH: Merge
```

### 3.3 Repository Structure

```
aiv-protocol/
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                    # Self-testing pipeline
│   │   ├── release.yml               # Semantic versioning
│   │   └── guard.yml                 # Reusable workflow (public interface)
│   └── ISSUE_TEMPLATE/
│       └── false_positive.yml        # Report incorrect rejections
│
├── src/
│   └── aiv/
│       ├── __init__.py
│       ├── py.typed                  # PEP 561 marker
│       │
│       ├── lib/                      # Core library (aiv-lib)
│       │   ├── __init__.py
│       │   ├── models.py             # Pydantic data models
│       │   ├── parser.py             # Markdown AST parser
│       │   ├── validators/
│       │   │   ├── __init__.py
│       │   │   ├── base.py           # Validator protocol
│       │   │   ├── structure.py      # Packet structure validation
│       │   │   ├── evidence.py       # Evidence class validation
│       │   │   ├── links.py          # URL and immutability validation
│       │   │   ├── zero_touch.py     # Reproduction instruction analysis
│       │   │   └── anti_cheat.py     # Test modification detection
│       │   ├── analyzers/
│       │   │   ├── __init__.py
│       │   │   ├── diff.py           # Git diff analysis
│       │   │   ├── ci.py             # CI artifact validation
│       │   │   └── friction.py       # Toil calculation
│       │   └── errors.py             # Exception hierarchy
│       │
│       ├── cli/                      # CLI application (aiv-cli)
│       │   ├── __init__.py
│       │   ├── main.py               # Typer application
│       │   ├── commands/
│       │   │   ├── __init__.py
│       │   │   ├── generate.py       # Packet generation
│       │   │   ├── check.py          # Local validation
│       │   │   └── init.py           # Repository setup
│       │   └── formatters.py         # Output formatting
│       │
│       └── guard/                    # GitHub Action (aiv-guard)
│           ├── __init__.py
│           ├── action.py             # Main entry point
│           ├── github_client.py      # Safe GitHub API wrapper
│           └── reporters.py          # Check run and comment formatting
│
├── tests/
│   ├── conftest.py                   # Shared fixtures
│   ├── unit/
│   │   ├── test_models.py
│   │   ├── test_parser.py
│   │   ├── test_validators/
│   │   │   ├── test_structure.py
│   │   │   ├── test_evidence.py
│   │   │   ├── test_links.py
│   │   │   ├── test_zero_touch.py
│   │   │   └── test_anti_cheat.py
│   │   └── test_analyzers/
│   ├── integration/
│   │   ├── test_cli.py
│   │   ├── test_guard.py
│   │   └── test_full_workflow.py
│   └── fixtures/
│       ├── packets/                  # Sample packets (valid and invalid)
│       ├── diffs/                    # Sample git diffs
│       └── prs/                      # Mock PR data
│
├── docs/
│   ├── protocol/                     # SOP reference
│   ├── integration/                  # Setup guides
│   └── api/                          # Generated API docs
│
├── pyproject.toml
├── README.md
├── LICENSE                           # MIT
└── CHANGELOG.md
```

---

## 4. Data Models

All data models use Pydantic v2 for validation, serialization, and documentation.

### 4.1 Core Models

```python
"""
aiv/lib/models.py

Core data models for the AIV Protocol Suite.
All models are immutable (frozen) to ensure validation integrity.
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Annotated, Literal
from urllib.parse import urlparse

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    HttpUrl,
    field_validator,
    model_validator,
)


class EvidenceClass(str, Enum):
    """
    The six classes of evidence defined by the AIV Protocol.

    Each class proves a different aspect of the change:
    - A: Behavior (execution)
    - B: Structure (code references)
    - C: Safety (negative evidence)
    - D: Impact (state changes)
    - E: Alignment (intent)
    - F: Conservation (non-regression)
    """
    EXECUTION = "A"
    REFERENTIAL = "B"
    NEGATIVE = "C"
    STATE = "D"
    INTENT = "E"
    CONSERVATION = "F"

    @classmethod
    def from_string(cls, value: str) -> EvidenceClass:
        """Parse evidence class from various string formats."""
        normalized = value.strip().upper()

        # Handle "A", "Class A", "A (Execution)", etc.
        for member in cls:
            if normalized == member.value:
                return member
            if normalized == member.name:
                return member
            if normalized.startswith(member.value):
                return member

        raise ValueError(f"Unknown evidence class: {value}")


class Severity(str, Enum):
    """Validation result severity levels."""
    BLOCK = "block"      # PR cannot be merged
    WARN = "warn"        # Flagged but not blocking
    INFO = "info"        # Informational only


class ValidationStatus(str, Enum):
    """Overall validation status."""
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"


class ArtifactLink(BaseModel):
    """
    A validated URL reference to evidence.

    Performs structural validation and immutability detection.
    """
    model_config = ConfigDict(frozen=True)

    url: HttpUrl
    is_immutable: bool = Field(description="Whether the link is SHA-pinned")
    immutability_reason: str | None = Field(
        default=None,
        description="Why the link is/isn't immutable"
    )
    link_type: Literal["github_blob", "github_actions", "github_pr", "external"] = Field(
        description="Categorized link type"
    )

    @classmethod
    def from_url(cls, url: str) -> ArtifactLink:
        """
        Parse and validate a URL, detecting immutability.

        Immutability rules:
        - GitHub blob/tree URLs must contain a 40-char SHA, not branch names
        - GitHub Actions URLs are immutable (run IDs are permanent)
        - External URLs are assumed mutable unless they contain version/hash
        """
        parsed = urlparse(url)

        # Detect GitHub URLs
        if "github.com" in parsed.netloc:
            path_parts = parsed.path.strip("/").split("/")

            # Check for actions run
            if "actions" in path_parts and "runs" in path_parts:
                return cls(
                    url=url,
                    is_immutable=True,
                    immutability_reason="GitHub Actions run IDs are permanent",
                    link_type="github_actions"
                )

            # Check for blob/tree references
            if "blob" in path_parts or "tree" in path_parts:
                # Find the ref (comes after blob/tree)
                try:
                    idx = path_parts.index("blob") if "blob" in path_parts else path_parts.index("tree")
                    ref = path_parts[idx + 1] if idx + 1 < len(path_parts) else None
                except (ValueError, IndexError):
                    ref = None

                if ref:
                    # Check if ref is a SHA (40 hex chars) or short SHA (7+ hex chars)
                    is_sha = (
                        len(ref) >= 7 and
                        all(c in "0123456789abcdef" for c in ref.lower())
                    )

                    # Check for known mutable refs
                    mutable_refs = {"main", "master", "develop", "staging", "trunk", "dev", "HEAD"}
                    is_mutable_branch = ref.lower() in mutable_refs

                    if is_sha:
                        return cls(
                            url=url,
                            is_immutable=True,
                            immutability_reason=f"SHA-pinned reference: {ref[:7]}...",
                            link_type="github_blob"
                        )
                    elif is_mutable_branch:
                        return cls(
                            url=url,
                            is_immutable=False,
                            immutability_reason=f"Mutable branch reference: {ref}",
                            link_type="github_blob"
                        )
                    else:
                        # Could be a tag or custom branch - warn but don't block
                        return cls(
                            url=url,
                            is_immutable=False,
                            immutability_reason=f"Non-SHA reference: {ref} (may be tag or branch)",
                            link_type="github_blob"
                        )

            # GitHub PR
            if "pull" in path_parts:
                return cls(
                    url=url,
                    is_immutable=True,
                    immutability_reason="PR numbers are permanent",
                    link_type="github_pr"
                )

        # External URL - assume mutable
        return cls(
            url=url,
            is_immutable=False,
            immutability_reason="External URL (immutability unknown)",
            link_type="external"
        )


class Claim(BaseModel):
    """
    A single claim within a Verification Packet.

    Each claim asserts something about the change and provides
    evidence to support that assertion.
    """
    model_config = ConfigDict(frozen=True)

    section_number: int = Field(ge=1, description="Section number in packet")
    description: str = Field(min_length=10, description="The claim statement")
    evidence_class: EvidenceClass
    artifact: ArtifactLink | str = Field(
        description="Evidence artifact (URL or description)"
    )
    reproduction: str = Field(description="How to reproduce/verify the evidence")

    # Optional fields for specific evidence classes
    fallback_artifact: str | None = Field(
        default=None,
        description="Fallback if primary artifact unavailable"
    )
    justification: str | None = Field(
        default=None,
        description="Required for Class F when tests are modified"
    )


class IntentSection(BaseModel):
    """
    Section 0: Intent Alignment (Mandatory).

    Must contain a Class E evidence link to the originating spec.
    """
    model_config = ConfigDict(frozen=True)

    evidence_link: ArtifactLink
    verifier_check: str = Field(
        min_length=10,
        description="Description of what the verifier should confirm"
    )


class VerificationPacket(BaseModel):
    """
    Complete parsed Verification Packet.

    This is the structured representation of the markdown packet
    attached to a Pull Request.
    """
    model_config = ConfigDict(frozen=True)

    version: str = Field(default="2.1", pattern=r"^\d+\.\d+$")
    intent: IntentSection
    claims: list[Claim] = Field(min_length=1)
    raw_markdown: str = Field(description="Original markdown for reference")

    @property
    def all_links(self) -> list[ArtifactLink]:
        """Extract all artifact links for bulk validation."""
        links = [self.intent.evidence_link]
        for claim in self.claims:
            if isinstance(claim.artifact, ArtifactLink):
                links.append(claim.artifact)
        return links

    @property
    def has_conservation_evidence(self) -> bool:
        """Check if packet includes Class F evidence."""
        return any(c.evidence_class == EvidenceClass.CONSERVATION for c in self.claims)


class ValidationError(BaseModel):
    """A single validation error or warning."""
    model_config = ConfigDict(frozen=True)

    rule_id: str = Field(pattern=r"^E\d{3}$", description="Rule identifier")
    severity: Severity
    message: str
    location: str | None = Field(
        default=None,
        description="Where in the packet the error occurred"
    )
    suggestion: str | None = Field(
        default=None,
        description="How to fix the issue"
    )


class ValidationResult(BaseModel):
    """Complete validation result for a packet."""
    model_config = ConfigDict(frozen=True)

    status: ValidationStatus
    packet: VerificationPacket | None = Field(
        default=None,
        description="Parsed packet if parsing succeeded"
    )
    errors: list[ValidationError] = Field(default_factory=list)
    warnings: list[ValidationError] = Field(default_factory=list)
    info: list[ValidationError] = Field(default_factory=list)

    # Metadata
    validated_at: datetime = Field(default_factory=datetime.utcnow)
    validator_version: str = Field(default="1.0.0")

    @property
    def blocking_errors(self) -> list[ValidationError]:
        """Get only errors that block merge."""
        return [e for e in self.errors if e.severity == Severity.BLOCK]

    @property
    def is_valid(self) -> bool:
        """Check if packet passes all blocking validations."""
        return len(self.blocking_errors) == 0


class AntiCheatFinding(BaseModel):
    """A potential anti-cheat violation detected in the diff."""
    model_config = ConfigDict(frozen=True)

    finding_type: Literal[
        "deleted_assertion",
        "skipped_test",
        "mock_bypass",
        "relaxed_condition",
        "removed_test_file"
    ]
    file_path: str
    line_number: int | None = None
    original_content: str | None = None
    severity: Severity = Severity.BLOCK
    requires_justification: bool = True


class AntiCheatResult(BaseModel):
    """Results of anti-cheat analysis on a diff."""
    model_config = ConfigDict(frozen=True)

    findings: list[AntiCheatFinding] = Field(default_factory=list)
    files_analyzed: int
    test_files_modified: int

    @property
    def has_violations(self) -> bool:
        """Check if any blocking violations were found."""
        return any(f.severity == Severity.BLOCK for f in self.findings)

    @property
    def requires_justification(self) -> bool:
        """Check if any findings require justification in packet."""
        return any(f.requires_justification for f in self.findings)


class FrictionScore(BaseModel):
    """Quantified measure of reproduction instruction complexity."""
    model_config = ConfigDict(frozen=True)

    score: int = Field(ge=0, description="Higher = more friction")
    step_count: int = Field(ge=0)
    prohibited_patterns_found: list[str] = Field(default_factory=list)
    is_zero_touch_compliant: bool
    recommendation: str | None = None
```

### 4.2 Configuration Models

```python
"""
aiv/lib/config.py

Configuration models for customizing validation behavior.
"""

from pathlib import Path
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class ZeroTouchConfig(BaseModel):
    """Configuration for Zero-Touch validation."""

    # Patterns that indicate non-zero-touch reproduction
    prohibited_patterns: list[str] = Field(default=[
        r"^(git clone|git checkout|git pull)",
        r"(npm|yarn|pip|poetry|uv)\s+install",
        r"(python|node|npm run|yarn|pytest|cargo|go run)\s+",
        r"^cd\s+",
        r"(docker|podman)\s+run",
        r"open\s+(browser|terminal|app)",
        r"(click|tap|press|select)\s+",
    ])

    # Patterns that are always acceptable
    allowed_patterns: list[str] = Field(default=[
        r"^N/?A$",
        r"^CI\s+(Automation|automation)",
        r"^See\s+CI",
        r"^Link\s+above",
        r"^Automated\s+via",
        r"^https?://",
    ])

    # Multi-step separators
    step_separators: list[str] = Field(default=[
        ";",
        " && ",
        " then ",
        r"\d+\.",
        r"step\s+\d",
    ])

    max_steps: int = Field(default=1, ge=1)


class AntiCheatConfig(BaseModel):
    """Configuration for Anti-Cheat detection."""

    # File patterns to analyze for test modifications
    test_file_patterns: list[str] = Field(default=[
        r"test_.*\.py$",
        r".*_test\.py$",
        r"tests?/.*\.py$",
        r".*\.test\.(js|ts|jsx|tsx)$",
        r".*\.spec\.(js|ts|jsx|tsx)$",
    ])

    # Patterns indicating assertion deletion
    assertion_patterns: list[str] = Field(default=[
        r"^\-\s*assert\s+",
        r"^\-\s*self\.assert",
        r"^\-\s*expect\(",
        r"^\-\s*should\.",
    ])

    # Patterns indicating test skipping
    skip_patterns: list[str] = Field(default=[
        r"@pytest\.mark\.skip",
        r"@unittest\.skip",
        r"\.skip\(",
        r"xit\(",
        r"xdescribe\(",
    ])

    # Patterns indicating mock/bypass
    bypass_patterns: list[str] = Field(default=[
        r"MOCK[_\s]*=\s*True",
        r"SKIP[_\s]*=\s*True",
        r"--force",
        r"--no-verify",
        r"if\s+DEBUG",
    ])


class MutableBranchConfig(BaseModel):
    """Configuration for immutability checking."""

    # Branch names that are always mutable
    mutable_branches: set[str] = Field(default={
        "main",
        "master",
        "develop",
        "dev",
        "staging",
        "trunk",
        "HEAD",
    })

    # Minimum SHA length to accept
    min_sha_length: int = Field(default=7, ge=7, le=40)


class AIVConfig(BaseSettings):
    """
    Main configuration for the AIV Protocol Suite.

    Can be loaded from environment variables or .aiv.yml file.
    """
    model_config = {"env_prefix": "AIV_"}

    # Validation strictness
    strict_mode: bool = Field(
        default=True,
        description="If True, warnings are treated as errors"
    )

    # Component configs
    zero_touch: ZeroTouchConfig = Field(default_factory=ZeroTouchConfig)
    anti_cheat: AntiCheatConfig = Field(default_factory=AntiCheatConfig)
    mutable_branches: MutableBranchConfig = Field(default_factory=MutableBranchConfig)

    # Fast-track configuration
    fast_track_patterns: list[str] = Field(
        default=[
            r"\.md$",
            r"\.txt$",
            r"\.gitignore$",
            r"\.editorconfig$",
            r"LICENSE",
            r"README",
        ],
        description="File patterns eligible for fast-track (Addendum 2.3)"
    )

    @classmethod
    def from_file(cls, path: Path) -> "AIVConfig":
        """Load configuration from YAML file."""
        import yaml

        if not path.exists():
            return cls()

        with open(path) as f:
            data = yaml.safe_load(f) or {}

        return cls(**data)
```

---

## 5. Core Algorithms

### 5.1 Markdown Packet Parser

The parser uses a proper Markdown AST approach rather than fragile regex:

```python
"""
aiv/lib/parser.py

Markdown packet parser using AST analysis.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterator

from mistune import create_markdown, Markdown
from mistune.renderers import BaseRenderer

from .models import (
    ArtifactLink,
    Claim,
    EvidenceClass,
    IntentSection,
    VerificationPacket,
    ValidationError,
    Severity,
)
from .errors import PacketParseError


@dataclass
class ParsedSection:
    """Intermediate representation of a parsed section."""
    level: int
    title: str
    content: list[str]
    raw_start: int
    raw_end: int


class SectionExtractor(BaseRenderer):
    """
    Custom Mistune renderer that extracts section structure.

    Rather than rendering to HTML, we extract the AST into
    a list of sections for further processing.
    """

    def __init__(self):
        self.sections: list[ParsedSection] = []
        self.current_section: ParsedSection | None = None
        self.current_content: list[str] = []

    def heading(self, text: str, level: int, **attrs) -> str:
        """Handle heading elements."""
        # Save previous section
        if self.current_section is not None:
            self.current_section.content = self.current_content
            self.sections.append(self.current_section)

        # Start new section
        self.current_section = ParsedSection(
            level=level,
            title=text,
            content=[],
            raw_start=attrs.get("raw_start", 0),
            raw_end=attrs.get("raw_end", 0),
        )
        self.current_content = []
        return ""

    def paragraph(self, text: str) -> str:
        """Handle paragraph elements."""
        self.current_content.append(text)
        return ""

    def list(self, text: str, ordered: bool, **attrs) -> str:
        """Handle list elements."""
        self.current_content.append(text)
        return ""

    def list_item(self, text: str, **attrs) -> str:
        """Handle list item elements."""
        return text + "\n"

    def finalize(self) -> list[ParsedSection]:
        """Finalize parsing and return sections."""
        if self.current_section is not None:
            self.current_section.content = self.current_content
            self.sections.append(self.current_section)
        return self.sections


class PacketParser:
    """
    Parser for AIV Verification Packets.

    Converts markdown text into structured VerificationPacket objects.
    """

    # Regex patterns for field extraction
    FIELD_PATTERNS = {
        "evidence_class": re.compile(
            r"\*\*Evidence\s+Class:\*\*\s*([A-F](?:\s*\([^)]+\))?)",
            re.IGNORECASE
        ),
        "evidence_artifact": re.compile(
            r"\*\*Evidence\s+Artifact:\*\*\s*(.+?)(?=\n\*\*|\n##|\Z)",
            re.IGNORECASE | re.DOTALL
        ),
        "reproduction": re.compile(
            r"\*\*Reproduction(?:\s+Instructions)?:\*\*\s*(.+?)(?=\n\*\*|\n##|\Z)",
            re.IGNORECASE | re.DOTALL
        ),
        "class_e_evidence": re.compile(
            r"\*\*Class\s+E\s+Evidence:\*\*\s*(.+?)(?=\n\*\*|\n##|\Z)",
            re.IGNORECASE | re.DOTALL
        ),
        "verifier_check": re.compile(
            r"\*\*Verifier\s+Check:\*\*\s*(.+?)(?=\n\*\*|\n##|\Z)",
            re.IGNORECASE | re.DOTALL
        ),
        "justification": re.compile(
            r"\*\*Justification:\*\*\s*(.+?)(?=\n\*\*|\n##|\Z)",
            re.IGNORECASE | re.DOTALL
        ),
    }

    # Pattern for extracting URLs from markdown links
    URL_PATTERN = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")

    # Pattern for packet header
    HEADER_PATTERN = re.compile(
        r"#\s*AIV\s+Verification\s+Packet(?:\s*\(v?([\d.]+)\))?",
        re.IGNORECASE
    )

    # Pattern for claim section title
    CLAIM_PATTERN = re.compile(
        r"(?:Claim(?:\s*\d+)?:?\s*)?(.+)",
        re.IGNORECASE
    )

    def __init__(self):
        self.renderer = SectionExtractor()
        self.markdown = create_markdown(renderer=self.renderer)
        self.errors: list[ValidationError] = []

    def parse(self, markdown_text: str) -> VerificationPacket | None:
        """
        Parse markdown text into a VerificationPacket.

        Args:
            markdown_text: Raw markdown content from PR description

        Returns:
            Parsed packet if successful, None if critical parse failure

        Raises:
            PacketParseError: If packet is missing or fundamentally malformed
        """
        self.errors = []

        # Reset renderer state
        self.renderer = SectionExtractor()
        self.markdown = create_markdown(renderer=self.renderer)

        # Check for packet header
        header_match = self.HEADER_PATTERN.search(markdown_text)
        if not header_match:
            raise PacketParseError(
                "Missing packet header. Expected '# AIV Verification Packet'"
            )

        version = header_match.group(1) or "2.1"

        # Parse into sections
        self.markdown(markdown_text)
        sections = self.renderer.finalize()

        # Find Section 0 (Intent Alignment)
        intent = self._parse_intent_section(sections, markdown_text)
        if intent is None:
            raise PacketParseError(
                "Missing Section 0: Intent Alignment (required by Addendum 2.1)"
            )

        # Parse claim sections
        claims = self._parse_claim_sections(sections, markdown_text)
        if not claims:
            raise PacketParseError(
                "No valid claims found. At least one claim is required."
            )

        return VerificationPacket(
            version=version,
            intent=intent,
            claims=claims,
            raw_markdown=markdown_text,
        )

    def _parse_intent_section(
        self,
        sections: list[ParsedSection],
        raw_text: str
    ) -> IntentSection | None:
        """Parse Section 0: Intent Alignment."""

        # Find section with "Intent" or "0." in title
        intent_section = None
        for section in sections:
            title_lower = section.title.lower()
            if "intent" in title_lower or section.title.startswith("0"):
                intent_section = section
                break

        if intent_section is None:
            return None

        content = "\n".join(intent_section.content)

        # Extract Class E Evidence link
        class_e_match = self.FIELD_PATTERNS["class_e_evidence"].search(content)
        if not class_e_match:
            self.errors.append(ValidationError(
                rule_id="E003",
                severity=Severity.BLOCK,
                message="Missing Class E Evidence link in Intent section",
                location="Section 0",
                suggestion="Add '**Class E Evidence:** [Link](url)'"
            ))
            return None

        # Extract URL from the field
        url = self._extract_url(class_e_match.group(1))
        if not url:
            self.errors.append(ValidationError(
                rule_id="E003",
                severity=Severity.BLOCK,
                message="Class E Evidence must contain a valid URL",
                location="Section 0",
            ))
            return None

        # Extract Verifier Check
        verifier_match = self.FIELD_PATTERNS["verifier_check"].search(content)
        verifier_check = verifier_match.group(1).strip() if verifier_match else ""

        if len(verifier_check) < 10:
            self.errors.append(ValidationError(
                rule_id="E002",
                severity=Severity.WARN,
                message="Verifier Check description is too brief",
                location="Section 0",
                suggestion="Describe what the verifier should confirm (min 10 chars)"
            ))
            verifier_check = verifier_check or "See linked specification"

        return IntentSection(
            evidence_link=ArtifactLink.from_url(url),
            verifier_check=verifier_check,
        )

    def _parse_claim_sections(
        self,
        sections: list[ParsedSection],
        raw_text: str
    ) -> list[Claim]:
        """Parse numbered claim sections."""

        claims = []

        for section in sections:
            # Skip non-claim sections
            if section.level != 2:  # Claims should be ## level
                continue

            # Skip Section 0
            if "intent" in section.title.lower() or section.title.startswith("0"):
                continue

            # Try to extract section number
            number_match = re.match(r"(\d+)\.", section.title)
            if not number_match:
                continue

            section_number = int(number_match.group(1))

            # Extract claim description from title
            claim_match = self.CLAIM_PATTERN.search(
                section.title[number_match.end():].strip()
            )
            description = claim_match.group(1).strip() if claim_match else section.title

            content = "\n".join(section.content)

            # Extract Evidence Class
            class_match = self.FIELD_PATTERNS["evidence_class"].search(content)
            if not class_match:
                self.errors.append(ValidationError(
                    rule_id="E006",
                    severity=Severity.BLOCK,
                    message=f"Missing Evidence Class in Section {section_number}",
                    location=f"Section {section_number}",
                ))
                continue

            try:
                evidence_class = EvidenceClass.from_string(class_match.group(1))
            except ValueError as e:
                self.errors.append(ValidationError(
                    rule_id="E006",
                    severity=Severity.BLOCK,
                    message=f"Invalid Evidence Class: {e}",
                    location=f"Section {section_number}",
                ))
                continue

            # Extract Evidence Artifact
            artifact_match = self.FIELD_PATTERNS["evidence_artifact"].search(content)
            if not artifact_match:
                self.errors.append(ValidationError(
                    rule_id="E007",
                    severity=Severity.BLOCK,
                    message=f"Missing Evidence Artifact in Section {section_number}",
                    location=f"Section {section_number}",
                ))
                continue

            artifact_text = artifact_match.group(1).strip()
            artifact_url = self._extract_url(artifact_text)

            if artifact_url:
                artifact = ArtifactLink.from_url(artifact_url)
            else:
                artifact = artifact_text

            # Extract Reproduction
            repro_match = self.FIELD_PATTERNS["reproduction"].search(content)
            reproduction = repro_match.group(1).strip() if repro_match else "N/A"

            # Extract Justification (for Class F)
            justification = None
            if evidence_class == EvidenceClass.CONSERVATION:
                just_match = self.FIELD_PATTERNS["justification"].search(content)
                justification = just_match.group(1).strip() if just_match else None

            claims.append(Claim(
                section_number=section_number,
                description=description,
                evidence_class=evidence_class,
                artifact=artifact,
                reproduction=reproduction,
                justification=justification,
            ))

        return sorted(claims, key=lambda c: c.section_number)

    def _extract_url(self, text: str) -> str | None:
        """Extract URL from markdown link or plain text."""

        # Try markdown link format first
        match = self.URL_PATTERN.search(text)
        if match:
            return match.group(2)

        # Try plain URL
        url_match = re.search(r"https?://[^\s\)]+", text)
        if url_match:
            return url_match.group(0)

        return None
```

### 5.2 Zero-Touch Validator

```python
"""
aiv/lib/validators/zero_touch.py

Zero-Touch compliance validation (Addendum 2.7).
"""

import re
from typing import Pattern

from ..models import (
    Claim,
    FrictionScore,
    ValidationError,
    Severity,
    VerificationPacket,
)
from ..config import ZeroTouchConfig


class ZeroTouchValidator:
    """
    Validates reproduction instructions for Zero-Touch compliance.

    The Zero-Touch mandate requires that verifiers never need to
    execute code locally. All verification must be artifact-based.
    """

    def __init__(self, config: ZeroTouchConfig | None = None):
        self.config = config or ZeroTouchConfig()

        # Compile patterns once
        self.prohibited_patterns: list[Pattern] = [
            re.compile(p, re.IGNORECASE) for p in self.config.prohibited_patterns
        ]
        self.allowed_patterns: list[Pattern] = [
            re.compile(p, re.IGNORECASE) for p in self.config.allowed_patterns
        ]
        self.step_patterns: list[Pattern] = [
            re.compile(p, re.IGNORECASE) for p in self.config.step_separators
        ]

    def validate_claim(self, claim: Claim) -> tuple[list[ValidationError], FrictionScore]:
        """
        Validate a single claim's reproduction instructions.

        Returns:
            Tuple of (errors, friction_score)
        """
        errors = []
        reproduction = claim.reproduction.strip()

        # Check if reproduction matches allowed patterns (early exit)
        for pattern in self.allowed_patterns:
            if pattern.match(reproduction):
                return errors, FrictionScore(
                    score=0,
                    step_count=0,
                    prohibited_patterns_found=[],
                    is_zero_touch_compliant=True,
                    recommendation=None
                )

        # Check for prohibited patterns
        prohibited_found = []
        for pattern in self.prohibited_patterns:
            if pattern.search(reproduction):
                prohibited_found.append(pattern.pattern)

        if prohibited_found:
            errors.append(ValidationError(
                rule_id="E008",
                severity=Severity.BLOCK,
                message=(
                    f"Reproduction instructions require local execution. "
                    f"Zero-Touch mandate violated."
                ),
                location=f"Section {claim.section_number}",
                suggestion=(
                    "Replace manual steps with a link to CI artifacts. "
                    "Example: 'See CI artifact: test_output.log'"
                )
            ))

        # Count steps
        step_count = 1  # Start with 1 (the instruction itself)
        for pattern in self.step_patterns:
            matches = pattern.findall(reproduction)
            step_count += len(matches)

        if step_count > self.config.max_steps:
            errors.append(ValidationError(
                rule_id="E008",
                severity=Severity.WARN,
                message=(
                    f"High-friction reproduction: {step_count} steps detected. "
                    f"Maximum recommended: {self.config.max_steps}"
                ),
                location=f"Section {claim.section_number}",
                suggestion="Consolidate into a single automated script or CI artifact link"
            ))

        # Calculate friction score
        friction_score = FrictionScore(
            score=len(prohibited_found) * 10 + max(0, step_count - 1) * 2,
            step_count=step_count,
            prohibited_patterns_found=prohibited_found,
            is_zero_touch_compliant=len(prohibited_found) == 0,
            recommendation=self._generate_recommendation(prohibited_found, step_count)
        )

        return errors, friction_score

    def validate_packet(self, packet: VerificationPacket) -> list[ValidationError]:
        """Validate all claims in a packet."""
        all_errors = []
        total_friction = 0

        for claim in packet.claims:
            errors, friction = self.validate_claim(claim)
            all_errors.extend(errors)
            total_friction += friction.score

        # Aggregate warning if total friction is high
        if total_friction > 20:
            all_errors.append(ValidationError(
                rule_id="E008",
                severity=Severity.WARN,
                message=f"Total packet friction score: {total_friction}. Consider simplifying.",
                location="Packet-wide",
            ))

        return all_errors

    def _generate_recommendation(
        self,
        prohibited: list[str],
        step_count: int
    ) -> str | None:
        """Generate actionable recommendation based on findings."""

        if not prohibited and step_count <= 1:
            return None

        recommendations = []

        if any("git" in p for p in prohibited):
            recommendations.append(
                "Replace git commands with GitHub file permalinks"
            )

        if any("install" in p for p in prohibited):
            recommendations.append(
                "Dependencies should be handled by CI; link to successful CI run"
            )

        if any("run" in p.lower() or "pytest" in p for p in prohibited):
            recommendations.append(
                "Execution evidence should be a CI artifact link, not a command"
            )

        if step_count > 1:
            recommendations.append(
                f"Consolidate {step_count} steps into single CI job"
            )

        return "; ".join(recommendations) if recommendations else None
```

### 5.3 Anti-Cheat Scanner

```python
"""
aiv/lib/validators/anti_cheat.py

Anti-cheat detection for test modifications (Addendum 2.4).
"""

import re
from pathlib import Path
from typing import Pattern

from ..models import (
    AntiCheatFinding,
    AntiCheatResult,
    Severity,
)
from ..config import AntiCheatConfig


class AntiCheatScanner:
    """
    Scans git diffs for potential test manipulation.

    Detects:
    - Deleted assertions
    - Skipped tests
    - Mock/bypass flags
    - Relaxed conditions
    - Removed test files
    """

    def __init__(self, config: AntiCheatConfig | None = None):
        self.config = config or AntiCheatConfig()

        # Compile patterns
        self.test_file_patterns: list[Pattern] = [
            re.compile(p) for p in self.config.test_file_patterns
        ]
        self.assertion_patterns: list[Pattern] = [
            re.compile(p, re.IGNORECASE) for p in self.config.assertion_patterns
        ]
        self.skip_patterns: list[Pattern] = [
            re.compile(p, re.IGNORECASE) for p in self.config.skip_patterns
        ]
        self.bypass_patterns: list[Pattern] = [
            re.compile(p, re.IGNORECASE) for p in self.config.bypass_patterns
        ]

    def scan_diff(self, diff_text: str) -> AntiCheatResult:
        """
        Scan a unified diff for anti-cheat violations.

        Args:
            diff_text: Unified diff output (from git diff or GitHub API)

        Returns:
            AntiCheatResult with all findings
        """
        findings = []
        files_analyzed = 0
        test_files_modified = 0

        # Parse diff into file chunks
        current_file = None
        current_line = 0

        for line in diff_text.split("\n"):
            # Detect file header
            if line.startswith("diff --git"):
                # Extract file path
                match = re.search(r"b/(.+)$", line)
                if match:
                    current_file = match.group(1)
                    files_analyzed += 1

                    if self._is_test_file(current_file):
                        test_files_modified += 1
                continue

            # Track line numbers
            if line.startswith("@@"):
                match = re.search(r"\+(\d+)", line)
                if match:
                    current_line = int(match.group(1))
                continue

            # Only analyze test files
            if current_file and self._is_test_file(current_file):

                # Check for deleted assertions (lines starting with -)
                if line.startswith("-"):
                    for pattern in self.assertion_patterns:
                        if pattern.search(line):
                            findings.append(AntiCheatFinding(
                                finding_type="deleted_assertion",
                                file_path=current_file,
                                line_number=current_line,
                                original_content=line[1:].strip(),
                                severity=Severity.BLOCK,
                                requires_justification=True,
                            ))
                            break

                # Check for added skip decorators
                if line.startswith("+"):
                    for pattern in self.skip_patterns:
                        if pattern.search(line):
                            findings.append(AntiCheatFinding(
                                finding_type="skipped_test",
                                file_path=current_file,
                                line_number=current_line,
                                original_content=line[1:].strip(),
                                severity=Severity.BLOCK,
                                requires_justification=True,
                            ))
                            break

            # Check for bypass patterns in any file
            if line.startswith("+"):
                for pattern in self.bypass_patterns:
                    if pattern.search(line):
                        findings.append(AntiCheatFinding(
                            finding_type="mock_bypass",
                            file_path=current_file or "unknown",
                            line_number=current_line,
                            original_content=line[1:].strip(),
                            severity=Severity.WARN,
                            requires_justification=True,
                        ))
                        break

            # Track line numbers for additions
            if line.startswith("+") and not line.startswith("+++"):
                current_line += 1
            elif not line.startswith("-") and not line.startswith("\\"):
                current_line += 1

        # Check for removed test files
        removed_files = re.findall(r"deleted file mode \d+\n.*?diff --git a/([^\s]+)", diff_text)
        for removed in removed_files:
            if self._is_test_file(removed):
                findings.append(AntiCheatFinding(
                    finding_type="removed_test_file",
                    file_path=removed,
                    line_number=None,
                    original_content=None,
                    severity=Severity.BLOCK,
                    requires_justification=True,
                ))

        return AntiCheatResult(
            findings=findings,
            files_analyzed=files_analyzed,
            test_files_modified=test_files_modified,
        )

    def _is_test_file(self, file_path: str) -> bool:
        """Check if a file path matches test file patterns."""
        for pattern in self.test_file_patterns:
            if pattern.search(file_path):
                return True
        return False

    def check_justification(
        self,
        result: AntiCheatResult,
        packet_claims: list
    ) -> list[AntiCheatFinding]:
        """
        Cross-reference findings with packet claims to check for justification.

        Returns:
            List of findings that lack justification
        """
        unjustified = []

        for finding in result.findings:
            if not finding.requires_justification:
                continue

            # Check if any Class F claim provides justification
            has_justification = False
            for claim in packet_claims:
                if claim.evidence_class.value == "F":
                    if claim.justification and len(claim.justification) > 20:
                        has_justification = True
                        break

            if not has_justification:
                unjustified.append(finding)

        return unjustified
```

### 5.4 Link Immutability Validator

```python
"""
aiv/lib/validators/links.py

URL validation and immutability checking (Addendum 2.2).
"""

import re
from urllib.parse import urlparse

from ..models import (
    ArtifactLink,
    ValidationError,
    Severity,
    VerificationPacket,
)
from ..config import MutableBranchConfig


class LinkValidator:
    """
    Validates artifact links for accessibility and immutability.
    """

    def __init__(self, config: MutableBranchConfig | None = None):
        self.config = config or MutableBranchConfig()

    def validate_packet_links(
        self,
        packet: VerificationPacket
    ) -> list[ValidationError]:
        """
        Validate all links in a packet.

        Checks:
        - Class E links must be immutable (SHA-pinned)
        - All GitHub blob/tree links should be immutable
        - Links should be accessible (optional, requires network)
        """
        errors = []

        # Validate intent link (Class E) - MUST be immutable
        intent_link = packet.intent.evidence_link
        if not intent_link.is_immutable:
            errors.append(ValidationError(
                rule_id="E004",
                severity=Severity.BLOCK,
                message=(
                    f"Class E Evidence must be immutable. "
                    f"Reason: {intent_link.immutability_reason}"
                ),
                location="Section 0 (Intent Alignment)",
                suggestion=(
                    "Link to a specific commit SHA, not a branch. "
                    "Example: /blob/a1b2c3d/docs/spec.md instead of /blob/main/..."
                )
            ))

        # Validate claim artifacts
        for claim in packet.claims:
            if isinstance(claim.artifact, ArtifactLink):
                link = claim.artifact

                # GitHub blob/tree links should be immutable
                if link.link_type == "github_blob" and not link.is_immutable:
                    errors.append(ValidationError(
                        rule_id="E009",
                        severity=Severity.BLOCK,
                        message=(
                            f"Evidence artifact link is mutable. "
                            f"Reason: {link.immutability_reason}"
                        ),
                        location=f"Section {claim.section_number}",
                        suggestion=(
                            "Use a SHA-pinned link. Copy the link from the "
                            "'Copy permalink' option in GitHub."
                        )
                    ))

        return errors

    def validate_link_format(self, url: str) -> list[ValidationError]:
        """
        Validate a single URL format without network access.
        """
        errors = []

        try:
            parsed = urlparse(url)

            if not parsed.scheme:
                errors.append(ValidationError(
                    rule_id="E009",
                    severity=Severity.BLOCK,
                    message="URL missing scheme (http/https)",
                    suggestion="Ensure URL starts with https://"
                ))

            if parsed.scheme not in ("http", "https"):
                errors.append(ValidationError(
                    rule_id="E009",
                    severity=Severity.WARN,
                    message=f"Unusual URL scheme: {parsed.scheme}",
                ))

            if not parsed.netloc:
                errors.append(ValidationError(
                    rule_id="E009",
                    severity=Severity.BLOCK,
                    message="URL missing domain",
                ))

        except Exception as e:
            errors.append(ValidationError(
                rule_id="E009",
                severity=Severity.BLOCK,
                message=f"Invalid URL format: {e}",
            ))

        return errors
```

---

## 6. Component Specifications

### 6.1 aiv-cli Specification

The CLI provides developer-facing tooling for packet generation and local validation.

```python
"""
aiv/cli/main.py

CLI application entry point.
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from aiv.lib.models import ValidationStatus, Severity
from aiv.lib.parser import PacketParser
from aiv.lib.validators.structure import StructureValidator
from aiv.lib.validators.evidence import EvidenceValidator
from aiv.lib.validators.links import LinkValidator
from aiv.lib.validators.zero_touch import ZeroTouchValidator
from aiv.lib.validators.anti_cheat import AntiCheatScanner
from aiv.lib.config import AIVConfig

app = typer.Typer(
    name="aiv",
    help="AIV Protocol Suite - Evidence-based engineering verification",
    no_args_is_help=True,
)
console = Console()


@app.command()
def check(
    body: Optional[str] = typer.Argument(
        None,
        help="PR body text or path to file containing it"
    ),
    diff: Optional[Path] = typer.Option(
        None,
        "--diff", "-d",
        help="Path to diff file for anti-cheat scanning"
    ),
    strict: bool = typer.Option(
        True,
        "--strict/--no-strict",
        help="Treat warnings as errors"
    ),
    config: Optional[Path] = typer.Option(
        None,
        "--config", "-c",
        help="Path to .aiv.yml configuration file"
    ),
):
    """
    Validate a Verification Packet locally.

    Examples:
        aiv check "# AIV Verification Packet..."
        aiv check pr_body.md --diff changes.diff
        cat pr.md | aiv check -
    """
    # Load configuration
    cfg = AIVConfig.from_file(config) if config else AIVConfig()
    cfg.strict_mode = strict

    # Read body from argument, file, or stdin
    if body == "-":
        import sys
        body_text = sys.stdin.read()
    elif body and Path(body).exists():
        body_text = Path(body).read_text()
    elif body:
        body_text = body
    else:
        console.print("[red]Error:[/red] No packet body provided")
        raise typer.Exit(1)

    # Parse packet
    parser = PacketParser()
    try:
        packet = parser.parse(body_text)
    except Exception as e:
        console.print(Panel(
            f"[red]Parse Error:[/red] {e}",
            title="❌ Packet Invalid",
            border_style="red"
        ))
        raise typer.Exit(1)

    # Collect all errors
    all_errors = list(parser.errors)

    # Run validators
    link_validator = LinkValidator(cfg.mutable_branches)
    all_errors.extend(link_validator.validate_packet_links(packet))

    zero_touch_validator = ZeroTouchValidator(cfg.zero_touch)
    all_errors.extend(zero_touch_validator.validate_packet(packet))

    # Run anti-cheat if diff provided
    anti_cheat_result = None
    if diff and diff.exists():
        scanner = AntiCheatScanner(cfg.anti_cheat)
        anti_cheat_result = scanner.scan_diff(diff.read_text())

        if anti_cheat_result.has_violations:
            unjustified = scanner.check_justification(
                anti_cheat_result,
                packet.claims
            )
            for finding in unjustified:
                all_errors.append(ValidationError(
                    rule_id="E011",
                    severity=Severity.BLOCK,
                    message=f"Test modification requires justification: {finding.finding_type}",
                    location=f"{finding.file_path}:{finding.line_number}",
                    suggestion="Add Class F evidence with justification for test changes"
                ))

    # Separate by severity
    blocking = [e for e in all_errors if e.severity == Severity.BLOCK]
    warnings = [e for e in all_errors if e.severity == Severity.WARN]

    # Display results
    if blocking:
        _display_errors(blocking, "Blocking Errors", "red")

    if warnings:
        _display_errors(warnings, "Warnings", "yellow")

    # Summary
    if blocking:
        console.print(Panel(
            f"[red]Validation Failed[/red]\n"
            f"{len(blocking)} blocking error(s), {len(warnings)} warning(s)",
            title="❌ Result",
            border_style="red"
        ))
        raise typer.Exit(1)
    elif warnings and cfg.strict_mode:
        console.print(Panel(
            f"[yellow]Validation Failed (Strict Mode)[/yellow]\n"
            f"{len(warnings)} warning(s) treated as errors",
            title="⚠️ Result",
            border_style="yellow"
        ))
        raise typer.Exit(1)
    else:
        console.print(Panel(
            f"[green]Validation Passed[/green]\n"
            f"Packet version: {packet.version}\n"
            f"Claims: {len(packet.claims)}",
            title="✅ Result",
            border_style="green"
        ))


@app.command()
def generate(
    pr: Optional[int] = typer.Option(
        None,
        "--pr", "-p",
        help="GitHub PR number to generate packet for"
    ),
    repo: str = typer.Option(
        ...,
        "--repo", "-r",
        help="GitHub repository (owner/name)"
    ),
    intent: str = typer.Option(
        ...,
        "--intent", "-i",
        help="URL to intent document (Issue, Task, etc.)"
    ),
):
    """
    Generate a Verification Packet from PR data.

    Fetches PR diff, CI status, and generates a formatted packet.

    Example:
        aiv generate --pr 2 --repo owner/repo --intent "https://..."
    """
    # This requires GitHub API access - implementation in commands/generate.py
    from aiv.cli.commands.generate import generate_packet

    packet_text = generate_packet(
        pr_number=pr,
        repo=repo,
        intent_url=intent,
    )

    console.print(Panel(
        packet_text,
        title="Generated Verification Packet",
        border_style="blue"
    ))

    # Copy to clipboard if available
    try:
        import pyperclip
        pyperclip.copy(packet_text)
        console.print("[dim]Copied to clipboard[/dim]")
    except ImportError:
        pass


@app.command()
def init(
    path: Path = typer.Argument(
        Path("."),
        help="Repository path to initialize"
    ),
):
    """
    Initialize AIV Protocol in a repository.

    Creates:
    - .aiv.yml configuration file
    - .github/workflows/aiv-guard.yml workflow
    """
    from aiv.cli.commands.init import initialize_repo

    initialize_repo(path)
    console.print(f"[green]✅ AIV Protocol initialized in {path}[/green]")


def _display_errors(errors: list, title: str, color: str):
    """Display errors in a formatted table."""
    table = Table(title=title, border_style=color)
    table.add_column("Rule", style="bold")
    table.add_column("Location")
    table.add_column("Message")
    table.add_column("Suggestion", style="dim")

    for error in errors:
        table.add_row(
            error.rule_id,
            error.location or "-",
            error.message,
            error.suggestion or "-"
        )

    console.print(table)


if __name__ == "__main__":
    app()
```

### 6.2 aiv-guard Specification

The GitHub Action provides automated enforcement:

```yaml
# .github/workflows/guard.yml
#
# AIV Protocol Guard - Reusable Workflow
#
# This workflow validates Pull Requests against the AIV Verification Protocol.
# It is designed to be called from other repositories.
#
# Usage in consuming repository:
#
#   name: AIV Verification
#   on: [pull_request]
#   jobs:
#     guard:
#       uses: ImmortalDemonGod/aiv-protocol/.github/workflows/guard.yml@v1
#       with:
#         strict: true
#

name: AIV Guard

on:
  workflow_call:
    inputs:
      strict:
        description: "Treat warnings as errors"
        required: false
        type: boolean
        default: true
      config_path:
        description: "Path to .aiv.yml in calling repo"
        required: false
        type: string
        default: ".aiv.yml"

jobs:
  validate:
    name: Validate Verification Packet
    runs-on: ubuntu-latest

    permissions:
      contents: read
      pull-requests: write
      checks: write

    steps:
      - name: Checkout AIV Protocol
        uses: actions/checkout@v4
        with:
          repository: ImmortalDemonGod/aiv-protocol
          path: aiv-protocol

      - name: Checkout PR Repository
        uses: actions/checkout@v4
        with:
          path: pr-repo
          fetch-depth: 0 # Full history for diff

      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install AIV Protocol
        run: |
          cd aiv-protocol
          pip install -e .

      - name: Fetch PR Data
        id: pr_data
        uses: actions/github-script@v7
        with:
          script: |
            // Fetch PR details safely (no shell interpolation)
            const pr = await github.rest.pulls.get({
              owner: context.repo.owner,
              repo: context.repo.repo,
              pull_number: context.payload.pull_request.number,
            });

            // Write body to file to avoid shell injection
            const fs = require('fs');
            fs.writeFileSync('pr_body.md', pr.data.body || '');

            // Fetch diff
            const diff = await github.rest.pulls.get({
              owner: context.repo.owner,
              repo: context.repo.repo,
              pull_number: context.payload.pull_request.number,
              mediaType: { format: 'diff' }
            });
            fs.writeFileSync('pr_diff.diff', diff.data);

            // Return metadata
            return {
              number: pr.data.number,
              title: pr.data.title,
              sha: pr.data.head.sha,
            };

      - name: Run AIV Validation
        id: validate
        continue-on-error: true
        run: |
          cd pr-repo

          # Run validation
          if [ "${{ inputs.strict }}" = "true" ]; then
            aiv check ../pr_body.md --diff ../pr_diff.diff --strict 2>&1 | tee validation_output.txt
          else
            aiv check ../pr_body.md --diff ../pr_diff.diff --no-strict 2>&1 | tee validation_output.txt
          fi

          echo "exit_code=$?" >> $GITHUB_OUTPUT

      - name: Create Check Run
        uses: actions/github-script@v7
        with:
          script: |
            const fs = require('fs');
            const output = fs.readFileSync('pr-repo/validation_output.txt', 'utf8');
            const exitCode = '${{ steps.validate.outputs.exit_code }}';

            const conclusion = exitCode === '0' ? 'success' : 'failure';
            const title = exitCode === '0' 
              ? '✅ AIV Verification Passed'
              : '❌ AIV Verification Failed';

            // Create check run
            await github.rest.checks.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              name: 'AIV Protocol Guard',
              head_sha: context.payload.pull_request.head.sha,
              status: 'completed',
              conclusion: conclusion,
              output: {
                title: title,
                summary: Validation ${conclusion},
                text: '``\n' + output + '\n``'
              }
            });

            // Post comment on failure
            if (exitCode !== '0') {
              const body = `## ❌ AIV Verification Failed
              
            Your Pull Request does not have a valid Verification Packet.

            <details>
            <summary>Validation Output</summary>

            \\\`
            ${output}
            \\\`

            </details>

            ### How to Fix

            1. Add a Verification Packet to your PR description following the [AIV Protocol](https://github.com/ImmortalDemonGod/aiv-protocol)
            2. Use \aiv generate\ to auto-generate a packet
            3. Ensure all links are SHA-pinned (immutable)
            4. Provide justification for any test modifications

            Run \aiv check\ locally to validate before pushing.`;
              
              await github.rest.issues.createComment({
                owner: context.repo.owner,
                repo: context.repo.repo,
                issue_number: context.payload.pull_request.number,
                body: body
              });
            }

      - name: Set Exit Status
        if: steps.validate.outputs.exit_code != '0'
        run: exit 1
```

---

## 7. Implementation Reference

### 7.1 Complete Validation Pipeline

```python
"""
aiv/lib/validators/pipeline.py

Complete validation pipeline that orchestrates all validators.
"""

from dataclasses import dataclass
from typing import Callable

from ..models import (
    ValidationResult,
    ValidationStatus,
    ValidationError,
    VerificationPacket,
    AntiCheatResult,
    Severity,
)
from ..parser import PacketParser
from ..config import AIVConfig
from .structure import StructureValidator
from .evidence import EvidenceValidator
from .links import LinkValidator
from .zero_touch import ZeroTouchValidator
from .anti_cheat import AntiCheatScanner


@dataclass
class ValidationContext:
    """Context passed through validation pipeline."""
    body: str
    diff: str | None
    config: AIVConfig
    packet: VerificationPacket | None = None
    anti_cheat_result: AntiCheatResult | None = None


class ValidationPipeline:
    """
    Orchestrates the complete validation process.

    Pipeline stages:
    1. Parse - Convert markdown to structured packet
    2. Structure - Validate packet structure completeness
    3. Links - Validate URL immutability
    4. Evidence - Validate evidence class requirements
    5. Zero-Touch - Validate reproduction instructions
    6. Anti-Cheat - Scan diff for test manipulation
    7. Cross-Reference - Ensure anti-cheat findings are justified
    """

    def __init__(self, config: AIVConfig | None = None):
        self.config = config or AIVConfig()

        # Initialize validators
        self.parser = PacketParser()
        self.structure_validator = StructureValidator()
        self.link_validator = LinkValidator(self.config.mutable_branches)
        self.evidence_validator = EvidenceValidator()
        self.zero_touch_validator = ZeroTouchValidator(self.config.zero_touch)
        self.anti_cheat_scanner = AntiCheatScanner(self.config.anti_cheat)

    def validate(self, body: str, diff: str | None = None) -> ValidationResult:
        """
        Run complete validation pipeline.

        Args:
            body: PR description markdown
            diff: Git diff (optional, for anti-cheat)

        Returns:
            Complete validation result
        """
        ctx = ValidationContext(
            body=body,
            diff=diff,
            config=self.config,
        )

        all_errors: list[ValidationError] = []
        all_warnings: list[ValidationError] = []
        all_info: list[ValidationError] = []

        # Stage 1: Parse
        try:
            ctx.packet = self.parser.parse(body)
            all_errors.extend(self.parser.errors)
        except Exception as e:
            all_errors.append(ValidationError(
                rule_id="E001",
                severity=Severity.BLOCK,
                message=f"Failed to parse packet: {e}",
            ))
            return ValidationResult(
                status=ValidationStatus.FAIL,
                packet=None,
                errors=all_errors,
            )

        # Stage 2: Structure
        structure_errors = self.structure_validator.validate(ctx.packet)
        all_errors.extend([e for e in structure_errors if e.severity == Severity.BLOCK])
        all_warnings.extend([e for e in structure_errors if e.severity == Severity.WARN])

        # Stage 3: Links
        link_errors = self.link_validator.validate_packet_links(ctx.packet)
        all_errors.extend([e for e in link_errors if e.severity == Severity.BLOCK])
        all_warnings.extend([e for e in link_errors if e.severity == Severity.WARN])

        # Stage 4: Evidence
        evidence_errors = self.evidence_validator.validate(ctx.packet)
        all_errors.extend([e for e in evidence_errors if e.severity == Severity.BLOCK])
        all_warnings.extend([e for e in evidence_errors if e.severity == Severity.WARN])

        # Stage 5: Zero-Touch
        zero_touch_errors = self.zero_touch_validator.validate_packet(ctx.packet)
        all_errors.extend([e for e in zero_touch_errors if e.severity == Severity.BLOCK])
        all_warnings.extend([e for e in zero_touch_errors if e.severity == Severity.WARN])

        # Stage 6: Anti-Cheat (if diff provided)
        if diff:
            ctx.anti_cheat_result = self.anti_cheat_scanner.scan_diff(diff)

            # Stage 7: Cross-Reference
            if ctx.anti_cheat_result.requires_justification:
                unjustified = self.anti_cheat_scanner.check_justification(
                    ctx.anti_cheat_result,
                    ctx.packet.claims
                )

                for finding in unjustified:
                    all_errors.append(ValidationError(
                        rule_id="E011",
                        severity=Severity.BLOCK,
                        message=(
                            f"Test modification requires Class F justification: "
                            f"{finding.finding_type} in {finding.file_path}"
                        ),
                        location=f"{finding.file_path}:{finding.line_number or 'N/A'}",
                        suggestion=(
                            "Add a claim with Evidence Class F and include "
                            "**Justification:** explaining why this test change is valid"
                        )
                    ))

        # Determine final status
        if self.config.strict_mode:
            has_failures = len(all_errors) > 0 or len(all_warnings) > 0
        else:
            has_failures = len(all_errors) > 0

        status = ValidationStatus.FAIL if has_failures else ValidationStatus.PASS

        return ValidationResult(
            status=status,
            packet=ctx.packet,
            errors=all_errors,
            warnings=all_warnings,
            info=all_info,
        )
```

### 7.2 Evidence Class-Specific Validation

```python
"""
aiv/lib/validators/evidence.py

Evidence class-specific validation rules.
"""

from ..models import (
    ArtifactLink,
    Claim,
    EvidenceClass,
    ValidationError,
    Severity,
    VerificationPacket,
)


class EvidenceValidator:
    """
    Validates evidence based on class-specific requirements.

    Each evidence class has different requirements for what
    constitutes valid proof.
    """

    def validate(self, packet: VerificationPacket) -> list[ValidationError]:
        """Validate all claims according to their evidence class."""
        errors = []

        for claim in packet.claims:
            class_errors = self._validate_claim_evidence(claim)
            errors.extend(class_errors)

        # Check for required Class F on bug fixes
        if self._is_bug_fix(packet) and not packet.has_conservation_evidence:
            errors.append(ValidationError(
                rule_id="E010",
                severity=Severity.BLOCK,
                message="Bug fixes require Class F (Conservation) evidence",
                location="Packet-wide",
                suggestion=(
                    "Add a claim showing that existing tests were preserved. "
                    "Include a link to the test file diff and CI run."
                )
            ))

        return errors

    def _validate_claim_evidence(self, claim: Claim) -> list[ValidationError]:
        """Validate a single claim's evidence against its class requirements."""
        errors = []

        # Dispatch to class-specific validator
        validators = {
            EvidenceClass.EXECUTION: self._validate_execution,
            EvidenceClass.REFERENTIAL: self._validate_referential,
            EvidenceClass.NEGATIVE: self._validate_negative,
            EvidenceClass.STATE: self._validate_state,
            EvidenceClass.INTENT: self._validate_intent,
            EvidenceClass.CONSERVATION: self._validate_conservation,
        }

        validator = validators.get(claim.evidence_class)
        if validator:
            errors.extend(validator(claim))

        return errors

    def _validate_execution(self, claim: Claim) -> list[ValidationError]:
        """
        Class A: Execution Evidence

        Requirements:
        - Must link to CI artifact (preferred) or automation output
        - UI evidence must show state transition (GIF/video)
        - Performance evidence must be differential A/B
        """
        errors = []

        # Check for CI link
        if isinstance(claim.artifact, ArtifactLink):
            if claim.artifact.link_type not in ("github_actions", "external"):
                # Not a CI link - warn but allow
                if "performance" in claim.description.lower():
                    errors.append(ValidationError(
                        rule_id="E013",
                        severity=Severity.BLOCK,
                        message="Performance claims require CI-based differential benchmarks",
                        location=f"Section {claim.section_number}",
                        suggestion=(
                            "Link to a CI job that runs benchmarks on both "
                            "main and feature branches"
                        )
                    ))
                elif "ui" in claim.description.lower() or "visual" in claim.description.lower():
                    errors.append(ValidationError(
                        rule_id="E012",
                        severity=Severity.WARN,
                        message="UI evidence should show state transition (GIF/video preferred)",
                        location=f"Section {claim.section_number}",
                    ))

        return errors

    def _validate_referential(self, claim: Claim) -> list[ValidationError]:
        """
        Class B: Referential Evidence

        Requirements:
        - Must link to specific file/line
        - Must be SHA-pinned
        """
        errors = []

        if isinstance(claim.artifact, ArtifactLink):
            if claim.artifact.link_type != "github_blob":
                errors.append(ValidationError(
                    rule_id="E007",
                    severity=Severity.WARN,
                    message="Class B evidence should link directly to code (GitHub blob)",
                    location=f"Section {claim.section_number}",
                ))
        elif isinstance(claim.artifact, str):
            # Check if it looks like a file reference
            if not any(x in claim.artifact.lower() for x in ["line", "file", "path"]):
                errors.append(ValidationError(
                    rule_id="E007",
                    severity=Severity.WARN,
                    message="Class B evidence should reference specific file locations",
                    location=f"Section {claim.section_number}",
                ))

        return errors

    def _validate_negative(self, claim: Claim) -> list[ValidationError]:
        """
        Class C: Negative Evidence

        Requirements:
        - Must demonstrate absence of something
        - For refactoring, entire regression suite must pass
        """
        errors = []

        # Check description mentions what is absent
        negative_keywords = ["not", "no ", "absence", "removed", "clean", "without"]
        has_negative_framing = any(kw in claim.description.lower() for kw in negative_keywords)

        if not has_negative_framing:
            errors.append(ValidationError(
                rule_id="E007",
                severity=Severity.WARN,
                message="Class C evidence should clearly state what is NOT present",
                location=f"Section {claim.section_number}",
                suggestion="Frame claim as 'Does not contain X' or 'Absence of Y'"
            ))

        return errors

    def _validate_state(self, claim: Claim) -> list[ValidationError]:
        """
        Class D: State Evidence

        Requirements:
        - Must show actual state change (not just logs)
        - Must be generated by automated script
        - Verifier must NOT run manually (Zero-Touch)
        """
        errors = []

        # Check that reproduction doesn't require manual DB access
        manual_state_keywords = ["sqlite3", "psql", "mysql", "mongo", "query"]
        repro_lower = claim.reproduction.lower()

        if any(kw in repro_lower for kw in manual_state_keywords):
            errors.append(ValidationError(
                rule_id="E007",
                severity=Severity.BLOCK,
                message="Class D evidence must not require manual database queries",
                location=f"Section {claim.section_number}",
                suggestion=(
                    "Generate state evidence as a CI artifact. "
                    "Example: Script that dumps relevant state to JSON file."
                )
            ))

        return errors

    def _validate_intent(self, claim: Claim) -> list[ValidationError]:
        """
        Class E: Intent Alignment

        Requirements:
        - Must link to spec/task/design doc
        - Must be immutable (SHA-pinned)
        """
        errors = []

        # Note: Primary Class E validation happens in IntentSection
        # This handles additional Class E claims if any
        if isinstance(claim.artifact, ArtifactLink):
            if not claim.artifact.is_immutable:
                errors.append(ValidationError(
                    rule_id="E004",
                    severity=Severity.BLOCK,
                    message="Class E links must be SHA-pinned (immutable)",
                    location=f"Section {claim.section_number}",
                ))

        return errors

    def _validate_conservation(self, claim: Claim) -> list[ValidationError]:
        """
        Class F: Conservation Evidence

        Requirements:
        - Must show test file diff (no deleted assertions)
        - Must link to full regression suite CI run
        - Must include justification if tests modified
        """
        errors = []

        # Check for justification if this is a test modification
        test_keywords = ["test", "assertion", "spec"]
        is_test_related = any(kw in claim.description.lower() for kw in test_keywords)

        if is_test_related and not claim.justification:
            errors.append(ValidationError(
                rule_id="E011",
                severity=Severity.WARN,
                message="Class F claims about tests should include justification",
                location=f"Section {claim.section_number}",
                suggestion="Add **Justification:** explaining why test changes are valid"
            ))

        return errors

    def _is_bug_fix(self, packet: VerificationPacket) -> bool:
        """Heuristic to detect if this PR is a bug fix."""
        indicators = ["fix", "bug", "issue", "patch", "resolve", "closes #"]

        # Check intent description
        intent_text = packet.intent.verifier_check.lower()
        if any(ind in intent_text for ind in indicators):
            return True

        # Check claim descriptions
        for claim in packet.claims:
            if any(ind in claim.description.lower() for ind in indicators):
                return True

        return False
```

---

## 8. Security Model

### 8.1 Threat Model

| Threat                | Attack Vector                               | Mitigation                                             |
| --------------------- | ------------------------------------------- | ------------------------------------------------------ |
| **Shell Injection**   | Malicious PR body/URL interpolated in shell | Use github-script with proper escaping; write to files |
| **Link Spoofing**     | Fake CI links that appear valid             | Validate link structure; optionally verify via API     |
| **Packet Forgery**    | Copy/paste old packet to new PR             | Cross-reference links with actual PR SHA               |
| **Anti-Cheat Bypass** | Obfuscate test deletions                    | Multiple detection patterns; semantic analysis         |
| **DoS via Regex**     | Crafted input causing ReDoS                 | Use re with timeouts; limit input size                 |
| **Secrets Exposure**  | Logs containing sensitive data              | Never log PR body raw; sanitize output                 |

### 8.2 Security Implementation

```python
"""
aiv/guard/security.py

Security utilities for the GitHub Action.
"""

import re
import html
from typing import Any


def sanitize_for_shell(value: str) -> str:
    """
    Sanitize a value for safe shell usage.

    Note: Prefer avoiding shell entirely. This is a fallback.
    """
    # Remove shell metacharacters
    dangerous_chars = r'[;&|`$(){}[\]<>\'"]'
    return re.sub(dangerous_chars, '', value)


def sanitize_for_markdown(value: str) -> str:
    """Sanitize value for inclusion in markdown comments."""
    # Escape HTML entities
    value = html.escape(value)
    # Escape markdown special chars
    value = re.sub(r'([*_~`#])', r'\\\1', value)
    return value


def truncate_for_log(value: str, max_length: int = 1000) -> str:
    """Truncate long values for safe logging."""
    if len(value) <= max_length:
        return value
    return value[:max_length] + f"... [truncated, {len(value)} total chars]"


def validate_url_structure(url: str) -> bool:
    """
    Validate URL structure without network access.

    Rejects:
    - Non-HTTP(S) schemes
    - localhost/private IPs
    - Unusual ports
    """
    from urllib.parse import urlparse

    try:
        parsed = urlparse(url)

        # Must be HTTPS (HTTP allowed for testing)
        if parsed.scheme not in ('http', 'https'):
            return False

        # No localhost or private IPs
        hostname = parsed.hostname or ''
        if hostname in ('localhost', '127.0.0.1', '0.0.0.0'):
            return False
        if hostname.startswith('192.168.') or hostname.startswith('10.'):
            return False

        # No unusual ports
        if parsed.port and parsed.port not in (80, 443, 8080):
            return False

        return True

    except Exception:
        return False


def safe_json_loads(data: str, max_size: int = 1_000_000) -> Any:
    """Load JSON with size limit to prevent DoS."""
    import json

    if len(data) > max_size:
        raise ValueError(f"JSON exceeds max size of {max_size} bytes")

    return json.loads(data)
```

---

## 9. Edge Case Handling

### 9.1 Bootstrap Exception (Addendum 2.3)

```python
"""
aiv/lib/validators/exceptions.py

Handlers for protocol exceptions (Addendum 2.3).
"""

from ..models import (
    ValidationError,
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
        import re

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
    ) -> list[ValidationError]:
        """
        Validate bootstrap-specific requirements.

        Requires:
        - Link to infrastructure code (Dockerfile, etc.)
        - Single-command reproducibility ("Verifier's Key")
        """
        errors = []

        # Check for infrastructure code reference
        has_infra_ref = False
        for claim in packet.claims:
            if claim.evidence_class.value == "B":
                artifact_str = str(claim.artifact)
                if any(p in artifact_str.lower() for p in ["dockerfile", "terraform", ".tf"]):
                    has_infra_ref = True
                    break

        if not has_infra_ref:
            errors.append(ValidationError(
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
                ";" not in repro and
                " && " not in repro and
                any(repro.startswith(cmd) for cmd in ["make ", "docker ", "terraform "])
            ):
                has_single_command = True
                break

        if not has_single_command:
            errors.append(ValidationError(
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
        claim,
        ci_run_urls: list[str]
    ) -> list[ValidationError]:
        """
        Validate a flake report claim.

        Args:
            claim: The claim asserting flakiness
            ci_run_urls: URLs to the CI runs being compared
        """
        errors = []

        if len(ci_run_urls) < 3:
            errors.append(ValidationError(
                rule_id="E014",
                severity=Severity.BLOCK,
                message=f"Flake proof requires 3 CI runs, got {len(ci_run_urls)}",
                location=f"Section {claim.section_number}",
                suggestion="Re-run CI twice more and link all 3 runs",
            ))

        return errors


class FastTrackHandler:
    """
    Handles Fast-Track protocol for trivial changes (Addendum 2.3).

    Documentation-only, styling, and config changes can use
    simplified evidence requirements.
    """

    def __init__(self, config=None):
        self.eligible_patterns = config.fast_track_patterns if config else [
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
        import re

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
    ) -> list[ValidationError]:
        """
        Validate fast-track packet.

        Fast-track still requires:
        - Intent alignment (Class E)
        - At least one claim (can be simplified)

        Does NOT require:
        - CI evidence
        - Zero-touch compliance (can be "Visual inspection")
        """
        errors = []

        # Check for "Fast-Track" tag
        has_fast_track_tag = False
        for claim in packet.claims:
            if "fast-track" in claim.description.lower():
                has_fast_track_tag = True
                break

        if not has_fast_track_tag:
            errors.append(ValidationError(
                rule_id="E005",
                severity=Severity.INFO,
                message=(
                    "This appears to be a trivial change eligible for Fast-Track. "
                    "Tag a claim with 'Fast-Track (Trivial)' to use simplified requirements."
                ),
            ))

        return errors
```

### 9.2 Atomic Spec Update (Addendum 2.5)

```python
"""
aiv/lib/validators/spec_update.py

Handles atomic spec updates when implementation reveals spec flaws.
"""

from ..models import (
    ArtifactLink,
    ValidationError,
    Severity,
    VerificationPacket,
)


class AtomicSpecValidator:
    """
    Validates that spec changes are atomic with code changes.

    When a PR modifies both code and specifications:
    1. The spec change must be in the same PR
    2. Class E link must point to the feature branch blob
    3. Verifier reviews spec change first
    """

    # File patterns that are specifications
    SPEC_PATTERNS = [
        r"docs?/",
        r"spec/",
        r"design/",
        r"\.md$",
        r"openapi",
        r"swagger",
        r"schema",
    ]

    def detect_spec_code_combo(self, file_list: list[str]) -> tuple[list[str], list[str]]:
        """
        Detect if PR contains both spec and code changes.

        Returns:
            Tuple of (spec_files, code_files)
        """
        import re

        spec_files = []
        code_files = []

        for file in file_list:
            is_spec = any(
                re.search(p, file, re.IGNORECASE)
                for p in self.SPEC_PATTERNS
            )

            if is_spec:
                spec_files.append(file)
            else:
                code_files.append(file)

        return spec_files, code_files

    def validate_atomic_update(
        self,
        packet: VerificationPacket,
        spec_files: list[str],
        code_files: list[str],
        pr_branch: str,
    ) -> list[ValidationError]:
        """
        Validate atomic spec update requirements.

        Args:
            packet: The verification packet
            spec_files: List of spec files in the PR
            code_files: List of code files in the PR
            pr_branch: The PR branch name (for link validation)
        """
        errors = []

        if not spec_files or not code_files:
            return errors  # Not a combo PR

        # Check that Class E points to feature branch
        intent_link = packet.intent.evidence_link

        if isinstance(intent_link, ArtifactLink):
            url_str = str(intent_link.url)

            # Should NOT point to main/master
            if "/main/" in url_str or "/master/" in url_str:
                errors.append(ValidationError(
                    rule_id="E015",
                    severity=Severity.WARN,
                    message=(
                        "Atomic spec update detected. Class E should point to "
                        "the updated spec on the feature branch, not main."
                    ),
                    location="Section 0",
                    suggestion=f"Update link to use feature branch: {pr_branch}",
                ))

        # Add informational note about review order
        errors.append(ValidationError(
            rule_id="E015",
            severity=Severity.INFO,
            message=(
                "This PR modifies both specs and code. "
                "Verifier should review spec changes FIRST."
            ),
            location="Packet-wide",
        ))

        return errors
```

---

## 10. Testing Strategy

### 10.1 Test Categories

```python
"""
tests/conftest.py

Shared test fixtures and utilities.
"""

import pytest
from pathlib import Path


# ============================================================================
# Valid Packet Fixtures
# ============================================================================

@pytest.fixture
def valid_minimal_packet():
    """Minimal valid packet meeting all requirements."""
    return """
# AIV Verification Packet (v2.1)

## 0. Intent Alignment (Mandatory)
- **Class E Evidence:** [Task #123](https://github.com/owner/repo/blob/abc123def456/docs/spec.md)
- **Verifier Check:** This PR implements the feature described in the linked spec.

## 1. Claim: Implements new API endpoint
- **Evidence Class:** A (Execution)
- **Evidence Artifact:** [CI Run](https://github.com/owner/repo/actions/runs/12345)
- **Reproduction:** CI Automation

---
_This packet certifies that all claims are supported by the linked, reproducible evidence._
"""


@pytest.fixture
def valid_full_packet():
    """Comprehensive packet with all evidence classes."""
    return """
# AIV Verification Packet (v2.1)

## 0. Intent Alignment (Mandatory)
- **Class E Evidence:** [Issue #42](https://github.com/owner/repo/blob/a1b2c3d/docs/requirements.md#feature-x)
- **Verifier Check:** Fixes the bug described in Issue #42 where login fails for SSO users.

## 1. Claim: Fixed SSO authentication flow
- **Evidence Class:** A (Execution)
- **Evidence Artifact:** [CI Run #9876](https://github.com/owner/repo/actions/runs/9876543)
- **Reproduction:** CI Automation

## 2. Claim: Added regression test for SSO edge case
- **Evidence Class:** B (Referential)
- **Evidence Artifact:** [test_sso.py:45-67](https://github.com/owner/repo/blob/a1b2c3d/tests/test_sso.py#L45-L67)
- **Reproduction:** N/A (Static Code)

## 3. Claim: No existing tests were modified or deleted
- **Evidence Class:** F (Conservation)
- **Evidence Artifact:** [Test diff](https://github.com/owner/repo/pull/123/files#diff-tests)
- **Reproduction:** See CI artifact
- **Justification:** Only additions; all existing assertions preserved.

---
_This packet certifies that all claims are supported by the linked, reproducible evidence._
"""


# ============================================================================
# Invalid Packet Fixtures
# ============================================================================

@pytest.fixture
def invalid_missing_header():
    """Packet without required header."""
    return """
## 0. Intent Alignment
- **Class E Evidence:** [Link](https://example.com)
"""


@pytest.fixture
def invalid_mutable_link():
    """Packet with mutable (non-SHA) link."""
    return """
# AIV Verification Packet (v2.1)

## 0. Intent Alignment (Mandatory)
- **Class E Evidence:** [Spec](https://github.com/owner/repo/blob/main/docs/spec.md)
- **Verifier Check:** This PR implements the spec.

## 1. Claim: Did something
- **Evidence Class:** A
- **Evidence Artifact:** [Link](https://example.com)
- **Reproduction:** N/A
"""


@pytest.fixture
def invalid_manual_reproduction():
    """Packet with Zero-Touch violation."""
    return """
# AIV Verification Packet (v2.1)

## 0. Intent Alignment (Mandatory)
- **Class E Evidence:** [Task](https://github.com/owner/repo/blob/abc123/docs/task.md)
- **Verifier Check:** Implements the task.

## 1. Claim: Feature works
- **Evidence Class:** A
- **Evidence Artifact:** Screenshot attached
- **Reproduction:** git clone repo && cd repo && npm install && npm run dev && open browser and click login
"""


# ============================================================================
# Diff Fixtures
# ============================================================================

@pytest.fixture
def diff_with_deleted_assertion():
    """Git diff that deletes an assertion."""
    return """
diff --git a/tests/test_auth.py b/tests/test_auth.py
index abc123..def456 100644
--- a/tests/test_auth.py
+++ b/tests/test_auth.py
@@ -10,7 +10,6 @@ def test_login():
     user = login("test@example.com", "password")
     assert user is not None
-    assert user.is_authenticated
     assert user.email == "test@example.com"
"""


@pytest.fixture
def diff_with_skip_decorator():
    """Git diff that adds a skip decorator."""
    return """
diff --git a/tests/test_payment.py b/tests/test_payment.py
index abc123..def456 100644
--- a/tests/test_payment.py
+++ b/tests/test_payment.py
@@ -5,6 +5,7 @@ import pytest
 from app.payment import process_payment


+@pytest.mark.skip(reason="Flaky test - fix later")
 def test_process_payment_success():
     result = process_payment(100, "USD")
     assert result.success
"""


@pytest.fixture
def diff_clean():
    """Git diff with no anti-cheat violations."""
    return """
diff --git a/src/auth.py b/src/auth.py
index abc123..def456 100644
--- a/src/auth.py
+++ b/src/auth.py
@@ -10,6 +10,10 @@ def login(email, password):
     user = find_user(email)
     if not user:
         return None
+
+    # SSO handling
+    if is_sso_user(user):
+        return sso_login(user)

     if verify_password(user, password):
         return user
"""
```

### 10.2 Unit Test Examples

```python
"""
tests/unit/test_validators/test_zero_touch.py

Unit tests for Zero-Touch validation.
"""

import pytest
from aiv.lib.validators.zero_touch import ZeroTouchValidator
from aiv.lib.models import Claim, EvidenceClass, ArtifactLink, Severity


class TestZeroTouchValidator:
    """Tests for ZeroTouchValidator."""

    @pytest.fixture
    def validator(self):
        return ZeroTouchValidator()

    def _make_claim(self, reproduction: str) -> Claim:
        """Helper to create a claim with given reproduction."""
        return Claim(
            section_number=1,
            description="Test claim",
            evidence_class=EvidenceClass.EXECUTION,
            artifact="https://example.com",
            reproduction=reproduction,
        )

    # ========================================================================
    # Allowed Patterns
    # ========================================================================

    def test_allows_na(self, validator):
        """N/A reproduction should pass."""
        claim = self._make_claim("N/A")
        errors, friction = validator.validate_claim(claim)

        assert len(errors) == 0
        assert friction.is_zero_touch_compliant
        assert friction.score == 0

    def test_allows_ci_automation(self, validator):
        """CI Automation reproduction should pass."""
        claim = self._make_claim("CI Automation")
        errors, friction = validator.validate_claim(claim)

        assert len(errors) == 0
        assert friction.is_zero_touch_compliant

    def test_allows_url_only(self, validator):
        """URL-only reproduction should pass."""
        claim = self._make_claim("https://github.com/owner/repo/actions/runs/123")
        errors, friction = validator.validate_claim(claim)

        assert len(errors) == 0
        assert friction.is_zero_touch_compliant

    def test_allows_see_ci_artifact(self, validator):
        """'See CI artifact' reproduction should pass."""
        claim = self._make_claim("See CI artifact: test_output.log")
        errors, friction = validator.validate_claim(claim)

        assert len(errors) == 0
        assert friction.is_zero_touch_compliant

    # ========================================================================
    # Prohibited Patterns
    # ========================================================================

    def test_blocks_git_clone(self, validator):
        """Git clone should be blocked."""
        claim = self._make_claim("git clone https://github.com/owner/repo.git")
        errors, friction = validator.validate_claim(claim)

        assert len(errors) > 0
        assert errors[0].severity == Severity.BLOCK
        assert not friction.is_zero_touch_compliant

    def test_blocks_npm_install(self, validator):
        """npm install should be blocked."""
        claim = self._make_claim("npm install && npm test")
        errors, friction = validator.validate_claim(claim)

        assert len(errors) > 0
        assert "npm" in errors[0].message.lower() or "install" in errors[0].message.lower()

    def test_blocks_pytest_command(self, validator):
        """Direct pytest execution should be blocked."""
        claim = self._make_claim("pytest tests/test_auth.py -v")
        errors, friction = validator.validate_claim(claim)

        assert len(errors) > 0
        assert not friction.is_zero_touch_compliant

    def test_blocks_manual_gui_steps(self, validator):
        """Manual GUI steps should be blocked."""
        claim = self._make_claim("Open browser, click login button, verify redirect")
        errors, friction = validator.validate_claim(claim)

        assert len(errors) > 0

    # ========================================================================
    # Multi-Step Detection
    # ========================================================================

    def test_warns_multi_step_semicolon(self, validator):
        """Multiple steps separated by semicolons should warn."""
        claim = self._make_claim("Step 1: do thing; Step 2: verify thing")
        errors, friction = validator.validate_claim(claim)

        # May be blocked for other reasons, but should detect multi-step
        assert friction.step_count > 1

    def test_warns_multi_step_numbered(self, validator):
        """Numbered steps should warn."""
        claim = self._make_claim("1. Clone repo 2. Run tests 3. Check output")
        errors, friction = validator.validate_claim(claim)

        assert friction.step_count > 1

    # ========================================================================
    # Edge Cases
    # ========================================================================

    def test_empty_reproduction(self, validator):
        """Empty reproduction should not crash."""
        claim = self._make_claim("")
        errors, friction = validator.validate_claim(claim)

        # May have warnings but should not raise
        assert isinstance(errors, list)

    def test_url_in_multi_step(self, validator):
        """URL within multi-step should still flag the steps."""
        claim = self._make_claim(
            "See https://example.com/ci/run and also run pytest locally"
        )
        errors, friction = validator.validate_claim(claim)

        # Should catch the pytest
        assert not friction.is_zero_touch_compliant
```

### 10.3 Integration Test Examples

```python
"""
tests/integration/test_full_workflow.py

End-to-end integration tests.
"""

import pytest
from aiv.lib.validators.pipeline import ValidationPipeline
from aiv.lib.models import ValidationStatus, Severity


class TestFullValidationWorkflow:
    """Integration tests for complete validation pipeline."""

    @pytest.fixture
    def pipeline(self):
        return ValidationPipeline()

    def test_valid_packet_passes(self, pipeline, valid_full_packet):
        """A complete, valid packet should pass all validations."""
        result = pipeline.validate(valid_full_packet)

        assert result.status == ValidationStatus.PASS
        assert len(result.blocking_errors) == 0
        assert result.packet is not None
        assert len(result.packet.claims) == 3

    def test_missing_header_fails(self, pipeline, invalid_missing_header):
        """Missing header should fail with E001."""
        result = pipeline.validate(invalid_missing_header)

        assert result.status == ValidationStatus.FAIL
        assert any(e.rule_id == "E001" for e in result.errors)

    def test_mutable_link_fails(self, pipeline, invalid_mutable_link):
        """Mutable Class E link should fail with E004."""
        result = pipeline.validate(invalid_mutable_link)

        assert result.status == ValidationStatus.FAIL
        assert any(e.rule_id == "E004" for e in result.errors)

    def test_manual_reproduction_blocks_in_strict(self, pipeline, invalid_manual_reproduction):
        """Manual reproduction should block in strict mode."""
        result = pipeline.validate(invalid_manual_reproduction)

        assert result.status == ValidationStatus.FAIL
        assert any(e.rule_id == "E008" for e in result.errors)

    def test_deleted_assertion_without_justification_fails(
        self,
        pipeline,
        valid_minimal_packet,
        diff_with_deleted_assertion
    ):
        """Deleted assertion without Class F justification should fail."""
        result = pipeline.validate(
            valid_minimal_packet,
            diff=diff_with_deleted_assertion
        )

        assert result.status == ValidationStatus.FAIL
        assert any(e.rule_id == "E011" for e in result.errors)

    def test_clean_diff_passes(self, pipeline, valid_full_packet, diff_clean):
        """Clean diff with proper packet should pass."""
        result = pipeline.validate(valid_full_packet, diff=diff_clean)

        assert result.status == ValidationStatus.PASS
```

---

## 11. Deployment & Integration

### 11.1 Repository Setup

```bash
#!/bin/bash
# scripts/init-repo.sh
#
# Initialize AIV Protocol in a new repository.

set -euo pipefail

REPO_ROOT="${1:-.}"

echo "Initializing AIV Protocol in $REPO_ROOT..."

# Create .aiv.yml configuration
cat > "$REPO_ROOT/.aiv.yml" << 'EOF'
# AIV Protocol Configuration
# See: https://github.com/ImmortalDemonGod/aiv-protocol

version: "1.0"

# Strictness settings
strict_mode: true

# Zero-Touch configuration
zero_touch:
  max_steps: 1
  # Add custom allowed patterns if needed
  # allowed_patterns:
  #   - "^make verify$"

# Anti-Cheat configuration
anti_cheat:
  # Add custom test file patterns if needed
  # test_file_patterns:
  #   - "spec/.*_spec.rb$"

# Fast-Track eligible files
fast_track_patterns:
  - "\.md$"
  - "\.txt$"
  - "\.gitignore$"
  - "LICENSE"
  - "README"
  - "CHANGELOG"
EOF

# Create GitHub workflow
mkdir -p "$REPO_ROOT/.github/workflows"

cat > "$REPO_ROOT/.github/workflows/aiv-guard.yml" << 'EOF'
# AIV Protocol Guard
# Validates Verification Packets on all Pull Requests

name: AIV Guard

on:
  pull_request:
    types: [opened, edited, synchronize, reopened]

permissions:
  contents: read
  pull-requests: write
  checks: write

jobs:
  validate:
    name: Validate Verification Packet
    uses: ImmortalDemonGod/aiv-protocol/.github/workflows/guard.yml@v1
    with:
      strict: true
EOF

echo "✅ AIV Protocol initialized!"
echo ""
echo "Next steps:"
echo "1. Commit the new files: git add .aiv.yml .github/workflows/aiv-guard.yml"
echo "2. Install the CLI: pip install aiv-protocol"
echo "3. Generate your first packet: aiv generate --help"
```

### 11.2 CI/CD Integration Examples

```yaml
# Example: Full CI with AIV as required check
name: CI

on:
  pull_request:
  push:
    branches: [main]

jobs:
  # AIV runs first - fast gate
  aiv-guard:
    name: AIV Protocol
    uses: ImmortalDemonGod/aiv-protocol/.github/workflows/guard.yml@v1
    with:
      strict: true

  # Tests only run if AIV passes
  test:
    name: Test Suite
    needs: [aiv-guard] # Depends on AIV
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -e ".[test]"
      - run: pytest

  # Merge requires both
  merge-ready:
    name: Ready to Merge
    needs: [aiv-guard, test]
    runs-on: ubuntu-latest
    steps:
      - run: echo "All checks passed!"
```

---

## 12. Application to PR #2

This section demonstrates applying the AIV Protocol to the actual mastery-engine Pull Request #2.

### 12.1 PR #2 Analysis

**Repository:** ImmortalDemonGod/mastery-engine
**PR Number:** 2
**Title:** "Surface Harden bug id in CLI and align README with runtime behavior"
**Branch:** codex/verify-readme-commands-execute-successfully

**Changes Summary:**

- Updated HardenRunner API from 2-tuple to 3-tuple (adding bug_id)
- Created missing symptom file
- Fixed README documentation
- Updated tests to match new API

### 12.2 Generated Verification Packet for PR #2

```markdown
# AIV Verification Packet (v2.1)

## 0. Intent Alignment (Mandatory)

- **Class E Evidence:** [Codex Task: Surface Bug ID](https://chatgpt.com/codex/tasks/task_e_6945984331008333bf2a6d004dd4213e)
- **Verifier Check:** This PR satisfies the Codex task requirement to surface the bug_id in CLI output during the Harden stage, ensuring the selected bug is visible for reproducibility and debugging.

## 1. Claim: HardenRunner API updated to return 3-tuple (harden_file, symptom, bug_id)

- **Evidence Class:** B (Referential)
- **Evidence Artifact:** [engine/stages/harden.py - Return Type Change](https://github.com/ImmortalDemonGod/mastery-engine/pull/2/files#diff-82121e784656461993f45447101888490a072047395066467023363383827038)
- **Reproduction:** N/A (Static Code Review)

## 2. Claim: Missing symptom file no_subtract_max_v2_symptom.txt has been created

- **Evidence Class:** C (Negative/Conservation)
- **Evidence Artifact:** [New File Added](https://github.com/ImmortalDemonGod/mastery-engine/pull/2/files#diff-1207e37340d2d634267425712128711584370215312015025745127202758162)
- **Reproduction:** N/A (File existence visible in diff)

## 3. Claim: All 185 engine tests pass with new API signature

- **Evidence Class:** A (Execution)
- **Evidence Artifact:** [CI: Engine Tests / test](https://github.com/ImmortalDemonGod/mastery-engine/actions/runs/12415125125)
- **Reproduction:** CI Automation (GitHub Actions)

## 4. Claim: Test suite updated to match new signature without deleting assertions

- **Evidence Class:** F (Conservation)
- **Evidence Artifact:** [tests/engine/test_stages.py diff](https://github.com/ImmortalDemonGod/mastery-engine/pull/2/files#diff-tests)
- **Reproduction:** See CI artifact
- **Justification:** Changes are limited to tuple unpacking (a,b) -> (a,b,c) and adding mock for bug_file.stem. All existing assertions preserved; no test logic deleted. The change is necessitated by the API signature update and maintains test coverage.

---

_This packet certifies that all claims are supported by the linked, reproducible evidence. No manual execution by the verifier is required._
```

### 12.3 Validation Result for PR #2

```
$ aiv check pr2_packet.md --diff pr2.diff

╭─────────────────────────────────────────────────────────────────╮
│                    AIV Validation Results                        │
├─────────────────────────────────────────────────────────────────┤
│ Packet Version: 2.1                                              │
│ Claims: 4                                                        │
│ Evidence Classes: B, C, A, F                                     │
╰─────────────────────────────────────────────────────────────────╯

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ✅ Structure Validation                                          ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ • Header: Present (v2.1)                                         ┃
┃ • Intent Section: Valid                                          ┃
┃ • Claims: 4 claims parsed                                        ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ⚠️  Link Validation                                              ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ Rule   │ Location  │ Message                                     ┃
┃────────┼───────────┼─────────────────────────────────────────────┃
┃ E004   │ Section 0 │ WARN: Class E link (chatgpt.com) is         ┃
┃        │           │ external; immutability cannot be verified.  ┃
┃        │           │ Suggestion: For maximum traceability, link  ┃
┃        │           │ to a GitHub Issue that references the task. ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ✅ Zero-Touch Validation                                         ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ All reproduction instructions are Zero-Touch compliant.          ┃
┃ Total Friction Score: 0                                          ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ ✅ Anti-Cheat Scan                                               ┃
┣━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┫
┃ Files Analyzed: 6                                                ┃
┃ Test Files Modified: 2                                           ┃
┃ Violations Found: 0                                              ┃
┃                                                                  ┃
┃ Test modifications detected in:                                  ┃
┃ • tests/engine/test_stages.py                                    ┃
┃ • tests/engine/test_new_cli_commands.py                          ┃
┃                                                                  ┃
┃ ✅ Class F justification provided in Claim #4                    ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

╭─────────────────────────────────────────────────────────────────╮
│ ✅ VALIDATION PASSED                                             │
│                                                                  │
│ 0 blocking errors                                                │
│ 1 warning (non-blocking)                                         │
│                                                                  │
│ This PR is ready for Systematic Verifier Protocol (SVP) review.  │
│ The human verifier should now perform:                           │
│ 1. Mental Trace of HardenRunner logic                            │
│ 2. Ownership Lock (variable renaming if desired)                 │
│ 3. Approval                                                      │
╰─────────────────────────────────────────────────────────────────╯
```

### 12.4 Verifier's SVP Notes for PR #2

After the automated validation passes, the human verifier performs the Systematic Verifier Protocol:

**Mental Trace Target:** engine/stages/harden.py::present_challenge

1. **Black Box Prediction:** Before reading, I predict the function selects a bug, copies reference implementation, applies the bug, and returns the path + symptom. The new bug_id should be derived from the bug file name.

2. **Code Trace:**

   ```python
   bug_id = bug_file.stem  # Line ~87
   # ... processing ...
   return harden_file, symptom, bug_id  # Line ~163
   ```

   - bug_file is a Path object from \_select_bug()
   - .stem returns filename without extension → valid for bug ID
   - Return order matches updated type hint

3. **Edge Case Probe:**
   - What if bug_file is None? → \_select_bug raises HardenChallengeError before we reach this line ✅
   - What if .stem is empty? → Would need a file named .json which violates naming convention; acceptable risk

4. **Ownership Lock:**
   - Consider renaming bug_id to selected_bug_identifier for clarity?
   - Decision: Current name is sufficient; matches CLI output terminology

**Judgment:** ✅ **APPROVED**

---

## 13. Appendices

### 13.1 Glossary

| Term                      | Definition                                                       |
| ------------------------- | ---------------------------------------------------------------- |
| **AIV Model**             | Architect-Implementer-Verifier workflow for software development |
| **Verification Packet**   | Structured evidence document attached to PRs                     |
| **Evidence Class**        | Category of proof (A-F) with specific requirements               |
| **Zero-Touch**            | Mandate that verifiers never execute code locally                |
| **SVP**                   | Systematic Verifier Protocol - cognitive review process          |
| **Immutable Link**        | URL pinned to specific commit SHA                                |
| **Anti-Cheat**            | Detection of test manipulation to fake passing                   |
| **Conservation Evidence** | Proof that existing tests/assertions preserved                   |
| **Friction Score**        | Quantified measure of reproduction complexity                    |
| **Fast-Track**            | Simplified requirements for trivial changes                      |

### 13.2 Rule ID Reference

| ID   | Addendum | Description                           |
| ---- | -------- | ------------------------------------- |
| E001 | v2.0     | Packet header required                |
| E002 | 2.1      | Intent section required               |
| E003 | 2.1      | Class E link required                 |
| E004 | 2.2      | Class E must be immutable             |
| E005 | v2.0     | At least one claim required           |
| E006 | v2.0     | Evidence class required per claim     |
| E007 | v2.0     | Evidence artifact required per claim  |
| E008 | 2.7      | Zero-Touch compliance                 |
| E009 | 2.2      | Artifact links must be immutable      |
| E010 | 2.4      | Bug fixes need Class F                |
| E011 | 2.4      | Test modifications need justification |
| E012 | 2.2      | UI evidence needs state transition    |
| E013 | 2.2      | Performance needs A/B CI              |
| E014 | 2.3      | Flake proof needs 3 runs              |
| E015 | 2.5      | Atomic spec updates                   |

### 13.3 Migration Guide

For teams adopting AIV Protocol:

**Week 1: Awareness**

- Share this document with team
- Install aiv-cli locally
- Review 2-3 existing PRs for what packets would look like

**Week 2: Soft Launch**

- Enable aiv-guard workflow in non-blocking mode
- Generate packets for new PRs (no enforcement)
- Collect feedback on friction points

**Week 3: Enforcement**

- Enable strict mode
- Block PRs without valid packets
- Hold first "SVP Review" session

**Week 4+: Optimization**

- Customize .aiv.yml for project patterns
- Add custom evidence class validators
- Integrate with existing tools (Jira, Linear, etc.)

---

## Document Control

| Version | Date       | Author   | Changes                         |
| ------- | ---------- | -------- | ------------------------------- |
| 1.0.0   | 2025-12-19 | AIV Team | Initial canonical specification |

**Review Status:** This document synthesizes V1 (SOP compliance), V2 (methodology rigor), and V3 (implementation code) while addressing all identified weaknesses. It is ready for implementation.

**License:** MIT

---

_End of AIV Protocol Suite Specification_
