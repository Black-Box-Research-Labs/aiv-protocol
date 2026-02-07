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

This isn't theoretical. During this project's own AI audit, we observed the **Hallucination Cascade**: an AI predicted a nonexistent function, "mentally traced" its execution, wrote a falsification scenario testing it, and produced a perfectly valid verification session describing a reality that didn't exist. Every step looked correct. None of it was real. ([Full audit →](#empirically-validated-the-ai-first-pass-proof))

## Velocity: 331 Commits in 10 Hours 47 Minutes

The most common objection to verification protocols is that they kill velocity. This project is the counter-evidence.

**This entire codebase — every source file, every test, every verification packet — was built in a single session.**

| Metric | Value |
| --- | --- |
| Sprint commits (excludes 2 pre-existing spec commits) | **331** |
| Wall-clock time | **10 h 47 min** (Feb 6 4:02 PM → Feb 7 2:49 AM) |
| Commit rate | **30.7 commits/hour** (~1 every 1 min 57 sec) |
| Python source + tests | **12,960 lines** across 47 files |
| Verification artifacts (packets, docs, specs) | **15,849 lines** across 87 files |
| Config (yml, toml, json) | **4,916 lines** across 9 files |
| **Total output** | **33,725 lines** across 143 files |
| Tests passing | **454** (unit + integration) |
| Verification packets | **75** (+ 1 template) |

47% of total output was verification artifacts. The other 53% — source code and tests — was higher quality *because* of it. Every number is reproducible from `git log`.

### Why It Didn't Slow Down

The atomic commit strategy (1 functional file + 1 verification packet) **enabled** this speed:

1. **Externalized context** — Instead of holding 30 files in your head, you verify *one* file and its evidence at a time. The packet is your working memory on disk.
2. **No regression loops** — Strict tests and evidence requirements catch errors at the commit gate, not 4 hours and 200 commits later.
3. **AI amplification** — AI generates code at superhuman speed. AIV forces every generated artifact through an evidence checkpoint, converting raw throughput into *verified* throughput.

### The Quine Property

This project used the AIV protocol to build the AIV protocol. The fact that it survived 331 atomic commits at 30.7/hour — with pre-commit enforcement active the entire time — is a self-referential proof that the overhead is negligible when the alternative is unverified chaos.

### Limitations

This is a greenfield project built by one developer + AI. The velocity claim is that AIV overhead was negligible *relative to the same project without it* — not that these exact numbers transfer to a 50-person team with a legacy codebase. Multi-team adoption is a harder problem; the risk-tier system (R0–R3) and separation-of-duties requirements are designed to scale to that context without imposing R3-level ceremony on R0 changes.

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

## Quickstart

```bash
# Install
pip install -e ".[dev]"

# Validate a verification packet
aiv check .github/aiv-packets/VERIFICATION_PACKET_GITIGNORE.md

# Validate in lenient mode (warnings don't block)
aiv check --no-strict .github/aiv-packets/VERIFICATION_PACKET_AIV_IMPLEMENTATION.md

# Validate with anti-cheat diff scanning
aiv check packet.md --diff changes.patch

# Validate with link vitality checks (HTTP HEAD probes)
aiv check packet.md --audit-links

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
3. **Links** — SHA-pinned immutability enforcement + link vitality (E021)
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

**Key flags:**

- `--no-strict` — Lenient mode (strict is the default; warnings don't block in lenient)
- `--diff <path>` — Enable anti-cheat scanning against a git diff
- `--audit-links` — Verify evidence URLs are reachable via HTTP HEAD (E021). Dead links — pointing to deleted files, force-pushed commits, or renamed repos — are flagged as blocking errors. Unreachable links (network failures) are flagged as warnings.

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
| `aiv svp ownership <PR>` | 4 | Record an Ownership Lock commit |
| `aiv svp validate <PR>` | — | Validate session completeness (JSON output) |
| `aiv svp rating <ID>` | — | Calculate and display verifier ELO rating |

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
│   │       ├── evidence.py          # Class-specific rules (E010–E022)
│   │       ├── links.py             # SHA-pinned immutability + link vitality (E021)
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
│   │       ├── rating.py            # Verifier ELO rating engine
│   │       └── validators/
│   │           └── session.py       # Session rules S001–S016
│   └── __main__.py                  # python -m aiv support
├── tests/                           # 454 tests (unit + integration)
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
│   │   ├── aiv-guard-python.yml     # PR validation — Python (live)
│   │   ├── ci.yml                   # CI: lint, format, type-check, test
│   │   └── verify-architecture.yml  # Evidence generation (disabled)
│   └── aiv-packets/                 # 75 verification packets (+ 1 template)
├── docs/
│   ├── AIV_SVP_PROTOCOL_USER_STORY.md  # Problem statement and user story
│   └── specs/
│       ├── AIV-SUITE-SPEC-V1.0-CANONICAL_2025-12-19.md
│       ├── SVP-SUITE-SPEC-V1.0-CANONICAL-2025-12-20.md
│       └── E2E_COMPLIANCE_TEST_SUITE_SPEC.md
├── .svp/                            # SVP session data & audit reports
│   ├── AUDIT_AI_FIRST_PASS.md       # AI First-Pass empirical audit
│   ├── session-pr*.json             # SVP verification sessions
│   └── ratings.json                 # Verifier ELO ratings
├── scripts/
│   └── map_packets.py               # Source-file-to-packet mapping generator
├── .husky/pre-commit                # Atomic commit enforcement
├── FILE_PACKET_MAP.md               # Evidence index: file ↔ packet mapping
├── FILE_PACKET_MAP.json             # Machine-readable mapping (same data)
├── SPECIFICATION.md                 # Canonical AIV standard (v1.0.0)
├── AUDIT_REPORT.md                  # Comprehensive codebase audit
├── CHANGELOG.md                     # Version history
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
| [`FILE_PACKET_MAP.md`](FILE_PACKET_MAP.md) | Evidence index — maps every source file to its verification packets (and vice versa) |
| [`CHANGELOG.md`](CHANGELOG.md) | Version history and release notes |

## Enforcement (Live)

Three enforcement layers, all active:

1. **Pre-commit hook** — Blocks commits without atomic unit pattern (1 functional file + 1 verification packet); runs both `aiv check` and `aiv audit` on staged packets
2. **`aiv check` CLI** — Local validation with 8-stage pipeline, strict mode, anti-cheat scanning, link vitality checks
3. **AIV Guard CI (Python)** — PR-level validation as a Python module (`src/aiv/guard/`): canonical packet validation, manifest verification, critical surface detection, SoD checks, and GitHub API integration

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
