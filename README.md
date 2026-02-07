# AIV Protocol

**Auditable Verification Standard for AI-Assisted Code Changes**

---

## What Is AIV?

AIV is a formal specification for proving that code changes — especially those authored or assisted by AI — were verified with immutable, auditable evidence before deployment.

In a world where AI writes 60–80% of code, organizations need more than green CI badges. AIV replaces "someone reviewed it" with **"here is the documented, immutable evidence of what was verified, by whom, and when."**

## Quickstart

```bash
# Install
pip install -e ".[dev]"

# Validate a verification packet
aiv check .github/aiv-packets/VERIFICATION_PACKET_GITIGNORE.md

# Validate in strict mode (warnings become errors)
aiv check --strict .github/aiv-packets/VERIFICATION_PACKET_AIV_IMPLEMENTATION.md

# Validate with anti-cheat diff scanning
aiv check packet.md --diff changes.patch

# Audit all packets for quality issues
aiv audit

# Scaffold a new verification packet
aiv generate my-feature --tier R1

# Initialize AIV in a repository
aiv init

# SVP cognitive verification (per-PR workflow)
aiv svp predict 42 --verifier alice --test-file tests/test_auth.py --approach "..." --edge-cases "..."
aiv svp trace 42 --verifier alice --function src/auth.py::login --notes "..." --edge-case "..." --predicted-output "..."
aiv svp probe 42 --verifier alice --assessment "..." --why-question "..."
aiv svp status 42
```

## CLI Commands

### `aiv check`

Validates a verification packet through an 8-stage pipeline:

1. **Parse** — Markdown → structured `VerificationPacket`
2. **Structure** — Completeness and quality checks
3. **Links** — SHA-pinned immutability enforcement
4. **Evidence** — Class-specific requirement validation
5. **Risk-Tier** — Evidence requirements per classification (R0–R3)
6. **Zero-Touch** — Reproduction instruction compliance
7. **Anti-Cheat** — Git diff scanning for test manipulation
8. **Cross-Reference** — Anti-cheat findings vs. packet justifications

```
$ aiv check .github/aiv-packets/VERIFICATION_PACKET_GITIGNORE.md
+-------------------------------- [OK] Result --------------------------------+
| Validation Passed                                                           |
| Packet version: 2.1                                                         |
| Claims: 3                                                                   |
+-----------------------------------------------------------------------------+
```

### `aiv init`

Creates a `.aiv.yml` configuration file in the target directory.

### `aiv audit`

Audits all verification packets for quality issues the validation pipeline does not catch:

- Commit SHA traceability (`COMMIT_PENDING`)
- Class E link immutability
- TODO remnants
- Missing Class F for bug-fix claims

```bash
# Audit all packets
aiv audit

# Audit with auto-fix
aiv audit --fix

# Audit a specific directory
aiv audit .github/aiv-packets --fix
```

### `aiv generate`

Scaffolds a new verification packet with tier-appropriate evidence sections:

```bash
# Generate an R2 packet with auto-detected git scope
aiv generate auth-fix --tier R2

# Generate with rationale
aiv generate cleanup --tier R0 --rationale "Remove dead code"
```

Auto-detects staged/unstaged files via `git diff` and populates the scope inventory.

### `aiv svp` (SVP Protocol Suite)

Cognitive verification commands for the Systematic Verifier Protocol:

| Command | Phase | Description |
| --- | --- | --- |
| `aiv svp status <PR>` | — | Show SVP completion status and phase checklist |
| `aiv svp predict <PR>` | 1 | Record a Black Box Prediction before seeing the diff |
| `aiv svp trace <PR>` | 2 | Record a Mental Trace (simulate execution flow) |
| `aiv svp probe <PR>` | 3 | Submit an Adversarial Probe checklist |
| `aiv svp validate <PR>` | — | Validate session completeness (JSON output) |

## The Problem

AI-assisted development increases code throughput beyond what humans can reliably comprehend line-by-line. Without structured verification:

- **Orphan Code** — Logic exists in repositories but in no human's mental model
- **Debug Inability** — Engineers cannot troubleshoot code they didn't understand when approving
- **Verification Theater** — Green CI badges provide false assurance without semantic comprehension
- **Cognitive Debt** — Accumulated unverified changes compound into systemic fragility

## Empirically Validated: The AI First-Pass Proof

We gave an AI 3 PRs to verify using the SVP protocol, then audited every claim it produced. The results define the core value proposition.

### The Scorecard

| SVP Phase | Accuracy | Takeaway |
| --- | --- | --- |
| **Adversarial Probe** (bug hunting) | **100%** (11/11) | Found 8 real bugs that 371 unit tests missed |
| **Trace** (execution-verified) | 100% (10/10) | Accurate when forced to execute |
| **Trace** (code-read only) | 87% (13/15) | Misread complex conditionals without execution |
| **Prediction** (architecture) | 74% (22/31) | Hallucinated functions that don't exist |
| **Falsification** (claim validation) | **40%** (8/20) | Parroted wrong numbers; verified theater, not logic |

### The Core Discovery: Hunter vs. Validator

The AI is a **superb Hunter** but a **dangerous Validator**.

- **As Hunter** (Probe phase — 100%): Reading code adversarially, the AI found logic collisions, missing regex patterns, hardcoded assumptions, and a header injection vulnerability. Every finding was real.
- **As Validator** (Falsification phase — 40%): Attempting to "prove" claims true, the AI defaulted to pattern matching — repeating "12 models" from its own prediction even though the code had 13.

### AIV Is a Hallucination Firewall

An AI can hallucinate a function, but it cannot hallucinate a **Class A artifact** (a URL to a passing CI run) or a **Class B permalink** to a file that doesn't exist. The evidence class taxonomy forces every claim to be grounded in artifacts that exist in reality, making phantom approvals structurally impossible.

The audit also revealed the **Hallucination Cascade** — a recursive failure loop where an AI predicts a nonexistent function, "mentally traces" it, writes a falsification scenario testing it, and produces a perfectly valid JSON session describing a reality that doesn't exist. Artifact-based evidence classes break this loop at step one.

### The Honest AI Protocol

These findings produced three protocol rules that harden SVP against AI yes-men:

| Rule | Enforcement |
| --- | --- |
| **S015** — Execution Trace | AI sessions must include `verified_output` from actual execution; mental simulation is banned |
| **S016** — Falsification-as-Code | AI falsification scenarios must be executable pytest snippets, not prose |
| **Adversarial Primacy** | The AI's primary deliverable is the Adversarial Report (probe findings), not approval |

Full details: [`.svp/AUDIT_AI_FIRST_PASS.md`](.svp/AUDIT_AI_FIRST_PASS.md)

## Evidence Classes (A–F)

| Class | Name         | Proves                                         | R0 | R1 | R2 | R3 |
| ----- | ------------ | ---------------------------------------------- |:--:|:--:|:--:|:--:|
| **A** | Execution    | Tests passed in a defined environment          | ✓  | ✓  | ✓  | ✓  |
| **B** | Referential  | Traceability to exact code locations (SHA-pinned) | ✓  | ✓  | ✓  | ✓  |
| **C** | Negative     | Absence of disallowed patterns                 |    | ○  | ✓  | ✓  |
| **D** | Differential | Change impact beyond test coverage             |    |    | ○  | ✓  |
| **E** | Intent       | Alignment with upstream requirement            |    | ✓  | ✓  | ✓  |
| **F** | Provenance   | Artifact integrity and chain-of-custody        |    |    | ○  | ✓  |

**Legend:** ✓ = Required | ○ = Optional

### Cognitive Verification (Class G — Optional)

| Phase | Name                | Purpose                                      |
| ----- | ------------------- | -------------------------------------------- |
| 1     | Black Box Prediction | Predict implementation before seeing the diff |
| 2     | Mental Trace         | Simulate execution flow without running code  |
| 3     | Adversarial Probe    | Hunt for AI hallucinations and edge cases     |
| 4     | Ownership Lock       | Push a commit proving you touched the code    |

## Risk Tiers

| Tier   | Name    | SoD      | Examples                                    |
| ------ | ------- | -------- | ------------------------------------------- |
| **R0** | Trivial | S0 (Self)| Docs, comments, formatting                  |
| **R1** | Low     | S0 (Self)| Isolated bug fixes, minor refactors         |
| **R2** | Medium  | S1 (Ind.)| API changes, config, dependency upgrades    |
| **R3** | High    | S1 (Ind.)| Auth, crypto, payments, PII, audit logging  |

## Repository Structure

```
aiv-protocol/
├── src/aiv/                         # Python implementation
│   ├── cli/main.py                  # CLI entry point (typer)
│   ├── lib/
│   │   ├── models.py                # Pydantic models (frozen, typed)
│   │   ├── parser.py                # Markdown → VerificationPacket
│   │   ├── config.py                # .aiv.yml configuration
│   │   ├── errors.py                # Exception hierarchy
│   │   ├── auditor.py               # Packet quality auditor
│   │   └── validators/
│   │       ├── pipeline.py          # 8-stage validation orchestrator
│   │       ├── base.py              # Base validator class
│   │       ├── structure.py         # Packet completeness
│   │       ├── evidence.py          # Class-specific rules (E015–E018)
│   │       ├── links.py             # SHA-pinned immutability
│   │       ├── zero_touch.py        # Zero-Touch mandate (E008)
│   │       └── anti_cheat.py        # Test manipulation scanner (E011)
│   ├── guard/                       # Python AIV Guard (CI module)
│   │   ├── models.py                # Guard-specific Pydantic models
│   │   ├── github_api.py            # GitHub API client
│   │   ├── canonical.py             # Canonical packet validation
│   │   ├── manifest.py              # CI artifact manifest validation
│   │   ├── runner.py                # Guard orchestrator
│   │   └── __main__.py              # python -m aiv.guard support
│   ├── svp/                         # SVP Protocol Suite
│   │   ├── cli/main.py              # SVP CLI commands (typer)
│   │   └── lib/
│   │       ├── models.py            # SVP Pydantic models (sessions, ratings)
│   │       └── validators/
│   │           └── session.py       # Session rules S001–S013
│   └── __main__.py                  # python -m aiv support
├── tests/                           # 371 tests (unit + integration)
│   ├── unit/
│   │   ├── test_models.py
│   │   ├── test_parser.py
│   │   ├── test_validators.py
│   │   ├── test_guard.py            # Guard module tests
│   │   ├── test_svp.py              # SVP module tests
│   │   ├── test_auditor.py          # Auditor module tests
│   │   └── test_coverage.py         # Coverage gap tests
│   └── integration/
│       ├── test_full_workflow.py
│       ├── test_e2e_compliance.py   # E2E compliance tests
│       └── test_svp_full_workflow.py # SVP integration tests
├── .github/
│   ├── workflows/
│   │   ├── aiv-guard.yml            # PR validation — JS (live)
│   │   ├── aiv-guard-python.yml     # PR validation — Python (live)
│   │   └── verify-architecture.yml  # Evidence generation (live)
│   └── aiv-packets/                 # 51 verification packets
├── docs/specs/
│   ├── AIV-SUITE-SPEC-V1.0-CANONICAL_2025-12-19.md
│   ├── SVP-SUITE-SPEC-V1.0-CANONICAL-2025-12-20.md
│   └── E2E_COMPLIANCE_TEST_SUITE_SPEC.md
├── .svp/                            # SVP session data & audit reports
│   ├── AUDIT_AI_FIRST_PASS.md       # AI First-Pass empirical audit
│   ├── session-pr*.json             # SVP verification sessions
│   └── ratings.json                 # Verifier ELO ratings
├── .husky/pre-commit                # Atomic commit enforcement
├── SPECIFICATION.md                 # Canonical AIV standard (v1.0.0)
├── AUDIT_REPORT.md                  # Comprehensive codebase audit
└── pyproject.toml                   # Build config (hatchling)
```

## Key Documents

| Document | Description |
| --- | --- |
| [`SPECIFICATION.md`](SPECIFICATION.md) | Canonical AIV standard — normative, RFC-style, formal validation rules |
| [`AUDIT_REPORT.md`](AUDIT_REPORT.md) | Comprehensive codebase audit with cross-analysis |
| [`docs/specs/AIV-SUITE-SPEC-V1.0-CANONICAL_2025-12-19.md`](docs/specs/AIV-SUITE-SPEC-V1.0-CANONICAL_2025-12-19.md) | AIV automation suite implementation spec |
| [`docs/specs/SVP-SUITE-SPEC-V1.0-CANONICAL-2025-12-20.md`](docs/specs/SVP-SUITE-SPEC-V1.0-CANONICAL-2025-12-20.md) | SVP cognitive verification suite implementation spec |
| [`docs/specs/E2E_COMPLIANCE_TEST_SUITE_SPEC.md`](docs/specs/E2E_COMPLIANCE_TEST_SUITE_SPEC.md) | End-to-end compliance test suite specification |
| [`.svp/AUDIT_AI_FIRST_PASS.md`](.svp/AUDIT_AI_FIRST_PASS.md) | AI First-Pass audit — empirical proof of Hunter vs. Validator dichotomy |

## Enforcement (Live)

Four enforcement layers, all active:

1. **Pre-commit hook** — Blocks commits without atomic unit pattern (1 functional file + 1 verification packet)
2. **`aiv check` CLI** — Local validation with 8-stage pipeline, strict mode, anti-cheat scanning
3. **AIV Guard CI (JS)** — PR-level validation: structure, immutable links, evidence requirements, critical surface detection, SoD checks
4. **AIV Guard CI (Python)** — Refactored guard as a Python module (`src/aiv/guard/`) with canonical packet validation, manifest verification, and GitHub API integration

## Configuration

Create `.aiv.yml` in your repository root (or run `aiv init`):

```yaml
# AIV Protocol Configuration
version: "1.0"
strict_mode: true
```

## Design Principles

- **Zero-Touch** — Verifiers never run code locally; all evidence is artifact-based
- **Falsifiability** — Every rule produces deterministic pass/fail
- **Defense in Depth** — All external data is untrusted until validated
- **Separation of Concerns** — AIV validates evidence quality, not code quality
- **Immutability** — All links must be SHA-pinned; branch-based URLs are rejected

## Standards Alignment

| Standard               | AIV Alignment                                |
| ---------------------- | -------------------------------------------- |
| SOC 2 (CC8.1)          | Change management, testing evidence          |
| SLSA v1.0              | Build provenance, artifact integrity         |
| ISO 27001 (A.14.2)     | Secure development, change control           |
| NIST SSDF (PW.7, PW.8) | Code review, security testing               |

## License

[MIT](LICENSE)
