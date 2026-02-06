# AIV Protocol

**Auditable Verification Standard for AI-Assisted Code Changes**

---

## What Is AIV?

AIV is a formal specification for proving that code changes — especially those authored or assisted by AI — were verified with immutable, auditable evidence before deployment.

In a world where AI writes 60–80% of code, organizations need more than green CI badges. AIV replaces "someone reviewed it" with **"here is the documented, immutable evidence of what was verified, by whom, and when."**

## The Problem

AI-assisted development increases code throughput beyond what humans can reliably comprehend line-by-line. Without structured verification:

- **Orphan Code** — Logic exists in repositories but in no human's mental model
- **Debug Inability** — Engineers cannot troubleshoot code they didn't understand when approving
- **Verification Theater** — Green CI badges provide false assurance without semantic comprehension
- **Cognitive Debt** — Accumulated unverified changes compound into systemic fragility

## The Solution

AIV addresses these risks through two complementary layers:

### Layer 1: Evidence Quality (Classes A–F)

Automated validation that verification evidence exists and is immutable.

| Class | Name         | Proves                                         |
| ----- | ------------ | ---------------------------------------------- |
| **A** | Execution    | Tests passed in a defined environment          |
| **B** | Referential  | Traceability to exact code locations (SHA-pinned) |
| **C** | Negative     | Absence of disallowed patterns                 |
| **D** | Differential | Change impact beyond test coverage             |
| **E** | Intent       | Alignment with upstream requirement            |
| **F** | Provenance   | Artifact integrity and chain-of-custody        |

### Layer 2: Cognitive Verification (Class G — Optional)

Structured process ensuring humans actually understand the code, not just approve it.

| Phase | Name                | Purpose                                      |
| ----- | ------------------- | -------------------------------------------- |
| 1     | Black Box Prediction | Predict implementation before seeing the diff |
| 2     | Mental Trace         | Simulate execution flow without running code  |
| 3     | Adversarial Probe    | Hunt for AI hallucinations and edge cases     |
| 4     | Ownership Lock       | Push a commit proving you touched the code    |

## Risk Tiers

| Tier   | Name    | Required Evidence | Examples                                    |
| ------ | ------- | ----------------- | ------------------------------------------- |
| **R0** | Trivial | A, B              | Docs, comments, formatting                  |
| **R1** | Low     | A, B, E           | Isolated bug fixes, minor refactors         |
| **R2** | Medium  | A, B, C, E        | API changes, config, dependency upgrades    |
| **R3** | High    | A–F               | Auth, crypto, payments, PII, audit logging  |

## Repository Structure

```
aiv-protocol/
├── SPECIFICATION.md                 # Canonical AIV standard (v1.0.0)
├── docs/
│   ├── specs/
│   │   ├── AIV-SUITE-SPEC-V1.0-CANONICAL_2025-12-19.md
│   │   └── SVP-SUITE-SPEC-V1.0-CANONICAL-2025-12-20.md
│   └── AIV_SVP_PROTOCOL_USER_STORY.md
├── .github/
│   ├── workflows/
│   │   ├── aiv-guard.yml            # PR validation (live)
│   │   └── verify-architecture.yml  # Evidence generation (live)
│   ├── aiv-packets/
│   │   └── VERIFICATION_PACKET_TEMPLATE.md
│   └── PULL_REQUEST_TEMPLATE.md
└── .husky/
    └── pre-commit                   # Atomic commit enforcement
```

## Key Documents

| Document | Description |
| --- | --- |
| [`SPECIFICATION.md`](SPECIFICATION.md) | The canonical AIV standard — normative, RFC-style, with formal validation rules |
| [`docs/specs/AIV-SUITE-SPEC-V1.0-CANONICAL_2025-12-19.md`](docs/specs/AIV-SUITE-SPEC-V1.0-CANONICAL_2025-12-19.md) | Implementation specification for the AIV automation suite |
| [`docs/specs/SVP-SUITE-SPEC-V1.0-CANONICAL-2025-12-20.md`](docs/specs/SVP-SUITE-SPEC-V1.0-CANONICAL-2025-12-20.md) | Implementation specification for the SVP cognitive verification suite |
| [`docs/AIV_SVP_PROTOCOL_USER_STORY.md`](docs/AIV_SVP_PROTOCOL_USER_STORY.md) | User story, problem statement, and honest sufficiency assessment |

## Enforcement (Live)

This repository already enforces AIV at two levels:

1. **Pre-commit hook** — Blocks commits that don't follow the atomic unit pattern (1 functional file + 1 verification packet)
2. **AIV Guard CI** — Validates verification packets on every PR: structure, immutable links, evidence class requirements, critical surface detection, SoD checks, and CI artifact inspection

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
