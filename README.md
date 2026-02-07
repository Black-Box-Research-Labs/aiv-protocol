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

# Initialize AIV in a repository
aiv init
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

## The Problem

AI-assisted development increases code throughput beyond what humans can reliably comprehend line-by-line. Without structured verification:

- **Orphan Code** — Logic exists in repositories but in no human's mental model
- **Debug Inability** — Engineers cannot troubleshoot code they didn't understand when approving
- **Verification Theater** — Green CI badges provide false assurance without semantic comprehension
- **Cognitive Debt** — Accumulated unverified changes compound into systemic fragility

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
│   │   └── validators/
│   │       ├── pipeline.py          # 8-stage validation orchestrator
│   │       ├── structure.py         # Packet completeness
│   │       ├── evidence.py          # Class-specific rules (E015–E018)
│   │       ├── links.py             # SHA-pinned immutability
│   │       ├── zero_touch.py        # Zero-Touch mandate (E008)
│   │       └── anti_cheat.py        # Test manipulation scanner (E011)
│   └── __main__.py                  # python -m aiv support
├── tests/                           # 84 tests (unit + integration)
│   ├── unit/
│   │   ├── test_models.py
│   │   ├── test_parser.py
│   │   └── test_validators.py
│   └── integration/
│       └── test_full_workflow.py
├── .github/
│   ├── workflows/
│   │   ├── aiv-guard.yml            # PR validation (live)
│   │   └── verify-architecture.yml  # Evidence generation (live)
│   └── aiv-packets/                 # 24 verification packets
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

## Enforcement (Live)

Three enforcement layers, all active:

1. **Pre-commit hook** — Blocks commits without atomic unit pattern (1 functional file + 1 verification packet)
2. **`aiv check` CLI** — Local validation with 8-stage pipeline, strict mode, anti-cheat scanning
3. **AIV Guard CI** — PR-level validation: structure, immutable links, evidence requirements, critical surface detection, SoD checks

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
