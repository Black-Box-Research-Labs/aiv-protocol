# Two-Layer Verification Architecture

**Document ID:** AIV-ARCH-002
**Version:** 0.1.0 (Draft)
**Status:** Proposal
**Date:** 2026-02-08
**Author:** Cascade + ImmortalDemonGod
**Companion Documents:**
- AIV-SPEC-V1.0.0-CANONICAL (SPECIFICATION.md)
- SVP-SUITE-SPEC-V1.0-CANONICAL
- CLAIM_AWARE_EVIDENCE_PLAN.md

---

## Table of Contents

1. [Motivation](#1-motivation)
2. [Problem Statement](#2-problem-statement)
3. [Architecture Overview](#3-architecture-overview)
4. [Layer 1: Evidence Files](#4-layer-1-evidence-files)
5. [Layer 2: Verification Packets](#5-layer-2-verification-packets)
6. [Change Lifecycle](#6-change-lifecycle)
7. [Workflow Modes](#7-workflow-modes)
8. [Hook Behavior](#8-hook-behavior)
9. [CLI Commands](#9-cli-commands)
10. [Spec Amendment](#10-spec-amendment)
11. [SVP Integration](#11-svp-integration)
12. [Migration Plan](#12-migration-plan)
13. [Edge Cases](#13-edge-cases)
14. [Adopter Profiles](#14-adopter-profiles)
15. [Open Questions](#15-open-questions)
16. [Decision Log](#16-decision-log)

---

## 1. Motivation

### 1.1 Discovery

During routine verification work on 2026-02-08, we discovered that `aiv commit` was
overwriting existing verification packets. Investigation revealed this was not a bug
but a symptom of a fundamental **granularity mismatch** between the spec and the
implementation.

### 1.2 The Mismatch

| Aspect | Spec (SPECIFICATION.md §B.1) | Implementation |
|--------|------------------------------|----------------|
| **Packet granularity** | One per PR (`pr_id` REQUIRED) | One per source file, overwritten on update |
| **Change boundary** | PR/MR (system-enforced) | Individual commit (tool-enforced) |
| **SVP granularity** | One session per PR ✅ | One session per PR ✅ |
| **Link between packet + SVP** | Same `pr_id` | None — different granularities |
| **Evidence lifecycle** | Created once, immutable | Overwritten each time the file is committed |

### 1.3 Why This Matters

1. **Spec non-compliance:** Our packets lack the REQUIRED `pr_id` field.
2. **SVP disconnect:** SVP sessions verify PRs, but packets verify individual files.
   No join key exists between them.
3. **Fragmented evidence:** A logical change touching 5 files produces 5 separate
   packets. An auditor must manually reassemble the full picture.
4. **Adoption barrier:** The spec's `pr_id` requirement locks out teams that push
   directly to main (no PRs).

### 1.4 What Works

1. **Per-file evidence collection** — AST-based Class A/B/C/F evidence is correct
   and valuable.
2. **Overwrite behavior** — Per-file evidence updated on each commit, with git
   history preserving the chain, scales O(files) and is sustainable.
3. **Evidence quality** — Claim-aware symbol resolution, per-symbol coverage,
   downstream caller analysis — all correct at the file level.

**Conclusion:** The evidence layer is sound. The packaging layer needs redesign.

### 1.5 Forensic Record: Overwritten Packets

During this session, 7 evidence files were overwritten via `echo y | aiv commit`
(piping "yes" to the overwrite prompt). The original evidence is recoverable from
git history but no longer present on HEAD.

| Evidence File | Original Commit | Overwritten At | Original Content |
|---------------|----------------|----------------|------------------|
| `VERIFICATION_PACKET_AUDITOR.md` | `ed1639b` | `bb7e7ab` | `git show bb7e7ab~1:.github/aiv-packets/VERIFICATION_PACKET_AUDITOR.md` |
| `VERIFICATION_PACKET_TEST_AUDITOR.md` | `80014cd` | `c1a2dbb` | `git show c1a2dbb~1:.github/aiv-packets/VERIFICATION_PACKET_TEST_AUDITOR.md` |
| `VERIFICATION_PACKET_MAIN.md` | `c1a2dbb` | `bfe5c1d` | `git show bfe5c1d~1:.github/aiv-packets/VERIFICATION_PACKET_MAIN.md` |
| `VERIFICATION_PACKET_CI.md` | (new) | `6b569dc` | Created then overwritten at `46f8166` |
| `VERIFICATION_PACKET_PRE_PUSH.md` | `3d21f23` | `9640d3a` | `git show 9640d3a~1:.github/aiv-packets/VERIFICATION_PACKET_PRE_PUSH.md` |
| `VERIFICATION_PACKET_EVIDENCE_COLLECTOR.md` | `e58b81c` | `a0280c8` | `git show a0280c8~1:.github/aiv-packets/VERIFICATION_PACKET_EVIDENCE_COLLECTOR.md` |
| `VERIFICATION_PACKET_TEST_EVIDENCE_COLLECTOR.md` | `84de1ee` | `0f57be1` | `git show 0f57be1~1:.github/aiv-packets/VERIFICATION_PACKET_TEST_EVIDENCE_COLLECTOR.md` |

**Root cause:** `aiv commit` generates names from the source filename
(`evidence_collector.py` → `VERIFICATION_PACKET_EVIDENCE_COLLECTOR.md`). The
`echo y |` pattern bypassed the overwrite confirmation without recording the
prior version. Under the new two-layer architecture (§3), this overwrite
behavior becomes intentional for Layer 1 evidence files, and the `Previous:`
header (§4.7) makes the chain explicit.

### 1.6 Reasoning Path

The design in this document emerged through a specific reasoning chain. Recording
this prevents future contributors from re-deriving it:

1. **Discovery:** `aiv commit` was overwriting existing packets. Initial reaction:
   "this destroys evidence, we need unique names per commit."
2. **O(n) realization:** Unique names per commit (Option D) creates O(commits)
   files. Unsustainable.
3. **Model B insight:** Per-file overwrite is actually O(files) and sustainable.
   Git history preserves every version. Overwrite is correct behavior.
4. **Spec check:** SPECIFICATION.md Appendix B requires `pr_id` — packets are
   per-PR, not per-file or per-commit. Fundamental granularity mismatch.
5. **SVP connection:** SVP sessions are per-PR. Per-file packets have no join key
   to SVP. This explains why the SVP felt disconnected.
6. **Option analysis:** Evaluated 4 models (PR-based, push-based, logical change,
   per-commit) against 3 adopter profiles. Push-based eliminated (arbitrary
   boundaries). Per-commit eliminated (O(n), SVP broken).
7. **Reconciliation:** Model B (per-file, overwrite) is a valid storage layer.
   The spec's per-change requirement is a packaging layer. Solution: two layers.
8. **Unified design:** Layer 1 (evidence, per-file, mutable) + Layer 2 (packets,
   per-change, immutable). `change_id` as alternative to `pr_id`.

### 1.7 Relationship to Claim-Aware Evidence Plan

The claim-aware evidence system documented in `CLAIM_AWARE_EVIDENCE_PLAN.md`
(AST-based symbol resolution, per-symbol coverage, downstream caller analysis,
claim verification matrix) IS the content of Layer 1 evidence files. The
two-layer architecture does not change what evidence is collected — it changes
how that evidence is organized and packaged.

- `resolve_changed_symbols()` → populates Layer 1 evidence per file
- `find_covering_tests()` → populates Layer 1 Class A per symbol
- `find_downstream_callers()` → populates Layer 1 Class C per symbol
- `ClaimVerification` matrix → aggregated into Layer 2 packet by `aiv close`

---

## 2. Problem Statement

### 2.1 Core Problem

The AIV spec defines verification at PR granularity, but the tooling generates
evidence at file granularity with no aggregation mechanism. This creates a gap
between what the spec requires (one coherent packet per change) and what the tooling
produces (N independent evidence files per N files changed).

### 2.2 Constraints

1. **The spec is ours to amend** — we are not constrained by an external standard.
2. **The tooling is ours to extend** — we can add commands, hooks, and state files.
3. **Existing evidence is valuable** — we must not discard per-file evidence
   collection. It is the foundation.
4. **Multiple workflow support** — the solution must work for PR-based teams AND
   direct-to-main teams.
5. **Backward compatibility** — existing packets should migrate cleanly, not be
   invalidated.

### 2.3 Non-Goals

1. Replacing git as the evidence storage mechanism.
2. Requiring external infrastructure (databases, cloud storage).
3. Breaking existing tests or validation rules.
4. Mandating PRs for all adopters.

---

## 3. Architecture Overview

### 3.1 Two-Layer Model

```
┌──────────────────────────────────────────────────────────────────┐
│  Layer 2: VERIFICATION PACKET (per-change)                       │
│  ════════════════════════════════════════                         │
│  The "AIV Packet" per spec. One per PR or logical change.        │
│  Contains: claims, classification, attestation, evidence refs.   │
│  THIS is what the spec validates.                                │
│                                                                  │
│  Location: .github/aiv-packets/                                  │
│  Naming:   PACKET_<change-name>.md  or  PACKET_PR_<N>.md        │
│  Lifecycle: Created by `aiv close` or CI guard on PR merge.      │
│  Mutability: Immutable once created. Never overwritten.          │
├──────────────────────────────────────────────────────────────────┤
│  Layer 1: EVIDENCE FILES (per-file, overwrite-on-update)         │
│  ════════════════════════════════════════════════════             │
│  Raw evidence artifacts. One per source file. Auto-generated     │
│  on each commit. Git history preserves every version.            │
│                                                                  │
│  Location: .github/aiv-evidence/                                 │
│  Naming:   EVIDENCE_<source-file-name>.md                        │
│  Lifecycle: Created/updated by `aiv commit` (pre-commit hook).   │
│  Mutability: Overwritten on each commit. Git history = chain.    │
└──────────────────────────────────────────────────────────────────┘
```

### 3.2 Key Principle: Separation of Evidence from Verification

| Concern | Layer | Responsibility |
|---------|-------|----------------|
| **"What evidence exists for this file?"** | Layer 1 | Per-file evidence files |
| **"Is this change verified?"** | Layer 2 | Per-change verification packet |
| **"Does the evidence support the claims?"** | Layer 2 → Layer 1 | Packet references evidence by commit SHA |
| **"Did a human understand this?"** | SVP | Session linked to Layer 2 packet |

### 3.3 Directory Layout

```
.github/
├── aiv-evidence/              # Layer 1: per-file evidence (overwrite OK)
│   ├── EVIDENCE_auditor.md
│   ├── EVIDENCE_evidence_collector.md
│   ├── EVIDENCE_pre_push.md
│   └── ...
├── aiv-packets/               # Layer 2: per-change packets (immutable)
│   ├── PACKET_enforcement_gap_fix.md
│   ├── PACKET_claim_aware_evidence.md
│   ├── PACKET_PR_42.md
│   └── TEMPLATE.md
.aiv/
├── config.yml                 # Workflow configuration
├── change.json                # Active change context (gitignored)
.svp/
├── session-pr42.json          # SVP sessions (unchanged)
├── session-enforcement_gap_fix.json  # SVP sessions for logical changes
```

---

## 4. Layer 1: Evidence Files

### 4.1 Purpose

Evidence files are **per-file evidence artifacts** containing raw verification data
collected automatically during each commit. They answer: "What do we know about the
current state of this source file?"

### 4.2 Naming Convention

```
EVIDENCE_<normalized-path>.md
```

The normalization algorithm (see §13.5 for collision rationale):
1. Take the path relative to the repo root.
2. Remove the configurable source root prefix (default: `src/aiv/`).
3. Replace path separators with `_`.
4. Remove the file extension.
5. Uppercase.

Examples:
- `src/aiv/lib/auditor.py` → `EVIDENCE_LIB_AUDITOR.md`
- `src/aiv/hooks/pre_push.py` → `EVIDENCE_HOOKS_PRE_PUSH.md`
- `src/aiv/guard/models.py` → `EVIDENCE_GUARD_MODELS.md`
- `tests/unit/test_auditor.py` → `EVIDENCE_TESTS_UNIT_TEST_AUDITOR.md`

This prevents naming collisions when multiple source files share basenames
(e.g., `lib/models.py` vs `guard/models.py`).

### 4.3 Content

Evidence files contain the same content currently generated by `aiv commit`:

- **Class A (Execution Evidence):** Test results, per-symbol AST coverage, ruff/mypy
- **Class B (Referential Evidence):** Scope inventory, file paths
- **Class C (Negative Evidence):** Downstream callers, impact analysis
- **Class F (Provenance Evidence):** Git log chain-of-custody, test file history
- **Claim Verification Matrix:** Per-symbol verdict (VERIFIED / MANUAL REVIEW)

### 4.4 Mutability

Evidence files are **overwritten** each time the source file is committed. This is
intentional:

1. The evidence file always reflects the **current** state of the source file.
2. Previous versions are preserved in **git history**.
3. Layer 2 packets reference evidence files **at specific commit SHAs**, making
   the reference immutable even though the file itself changes.

### 4.5 Lifecycle

```
Developer commits src/aiv/lib/auditor.py
  → pre-commit hook triggers evidence collection
  → .github/aiv-evidence/EVIDENCE_AUDITOR.md is created or updated
  → evidence file is staged and included in the commit
  → .aiv/change.json is updated with this commit's SHA and file list
```

### 4.6 Recovery

Any previous version of an evidence file can be retrieved:

```bash
# Show evidence for auditor.py as of commit abc1234
git show abc1234:.github/aiv-evidence/EVIDENCE_AUDITOR.md

# Full history of evidence for auditor.py
git log -p -- .github/aiv-evidence/EVIDENCE_AUDITOR.md
```

### 4.7 Previous Version Header

Each evidence file includes a `Previous:` header linking to the prior version:

```markdown
# AIV Evidence File (v1.0)

**File:** `src/aiv/lib/auditor.py`
**Commit:** `a0280c8`
**Previous:** `e58b81c` <!-- commit SHA of the prior version of this evidence file -->
**Generated:** 2026-02-08T21:54:08-06:00
```

This makes the chain explicit without relying on `git log`.

---

## 5. Layer 2: Verification Packets

### 5.1 Purpose

Verification packets are **per-change verification records** conforming to the AIV
spec (Appendix B). They answer: "Is this change verified? What claims are made and
what evidence supports them?"

### 5.2 Naming Convention

```
PACKET_<change-identifier>.md
```

For PR workflows:
- `PACKET_PR_42.md`

For logical-change workflows:
- `PACKET_enforcement_gap_fix.md`
- `PACKET_claim_aware_evidence.md`

### 5.3 Content

Packets conform to the spec's Appendix B schema. Key sections:

```markdown
# AIV Verification Packet (v2.2)

## Identification

| Field | Value |
|-------|-------|
| **Repository** | github.com/ImmortalDemonGod/aiv-protocol |
| **Change ID** | enforcement-gap-fix |
| **Commits** | `3d21f23`, `7d12d07`, `bfe5c1d`, `9640d3a` |
| **Head SHA** | `9640d3a` |
| **Base SHA** | `c0561ff` |
| **Created** | 2026-02-08T20:00:00-06:00 |

## Classification

```yaml
risk_tier: R1
sod_mode: S0
blast_radius: component
classification_rationale: "Enforcement layer changes — hooks and auditor."
```

## Claims

1. Pre-push hook blocks pushes containing commits with functional files but no
   verification evidence.
2. Auditor detects HOOK_BYPASS and ATOMIC_VIOLATION in git history.
3. `aiv init` installs pre-push hook alongside pre-commit hook.
4. CI workflow runs `aiv audit --commits 20` on push to main.

## Evidence References

| Claim | Evidence File | Commit SHA | Class |
|-------|---------------|------------|-------|
| 1 | EVIDENCE_PRE_PUSH.md | `3d21f23` | A, B |
| 2 | EVIDENCE_AUDITOR.md | `bb7e7ab` | A, B, C |
| 3 | EVIDENCE_MAIN.md | `bfe5c1d` | A, B |
| 4 | EVIDENCE_CI.md | `6b569dc` | B, E |

## Attestation

| Field | Value |
|-------|-------|
| **Verifier** | cascade-ai |
| **Decision** | COMPLIANT |
| **Timestamp** | 2026-02-08T20:30:00-06:00 |
| **Signature** | unsigned |

## Known Limitations

- Pre-push hook not tested on non-Windows platforms.
- CI audit job only scans last 20 commits.
```

### 5.4 Mutability

Packets are **immutable once created.** They are NEVER overwritten. Each change
gets its own uniquely-named packet. This is enforced by:

1. The naming convention includes the change identifier (unique).
2. `aiv close` refuses to create a packet if one already exists for this change.
3. The auditor flags any packet that has been modified after creation.

### 5.5 Lifecycle

```
aiv close
  → reads .aiv/change.json (list of commits, files, evidence)
  → aggregates claims from all evidence files
  → generates classification (risk tier, blast radius)
  → creates PACKET_<change-id>.md
  → validates the packet (runs aiv check)
  → commits the packet
  → clears .aiv/change.json
```

### 5.6 Evidence Referencing

Packets reference Layer 1 evidence files at specific commit SHAs. This makes the
reference immutable even though the evidence file itself may be overwritten later:

```markdown
| Claim | Evidence File | Commit SHA | Class |
|-------|---------------|------------|-------|
| 1 | EVIDENCE_PRE_PUSH.md | `3d21f23` | A, B |
```

To retrieve the evidence as it existed when the packet was created:

```bash
git show 3d21f23:.github/aiv-evidence/EVIDENCE_PRE_PUSH.md
```

This is the same immutability mechanism as SHA-pinned GitHub URLs (§3.3), but
using git's native content-addressed storage.

---

## 6. Change Lifecycle

### 6.1 State Machine

```
                    aiv begin
    [NO CHANGE] ──────────────────► [CHANGE ACTIVE]
                                          │
                                          │  git commit (repeatable)
                                          │  ← pre-commit hook generates evidence
                                          ▼
                                    [CHANGE ACTIVE]
                                          │
                                          │  aiv close
                                          ▼
                                    [PACKET CREATED]
                                          │
                                          │  git push
                                          │  ← pre-push verifies no open changes
                                          ▼
                                      [PUSHED]
```

### 6.2 State File: `.aiv/change.json`

```json
{
  "name": "enforcement-gap-fix",
  "started_at": "2026-02-08T19:00:00-06:00",
  "mode": "direct",
  "commits": [
    {
      "sha": "3d21f23",
      "message": "feat(hooks): add pre-push enforcement",
      "files": ["src/aiv/hooks/pre_push.py"],
      "evidence": ["EVIDENCE_PRE_PUSH.md"],
      "timestamp": "2026-02-08T19:05:00-06:00"
    },
    {
      "sha": "7d12d07",
      "message": "test(hooks): pre-push hook tests",
      "files": ["tests/unit/test_pre_push_hook.py"],
      "evidence": ["EVIDENCE_TEST_PRE_PUSH_HOOK.md"],
      "timestamp": "2026-02-08T19:10:00-06:00"
    }
  ],
  "files_changed": [
    "src/aiv/hooks/pre_push.py",
    "tests/unit/test_pre_push_hook.py"
  ],
  "evidence_files": [
    "EVIDENCE_PRE_PUSH.md",
    "EVIDENCE_TEST_PRE_PUSH_HOOK.md"
  ]
}
```

This file is **gitignored** — it is local workflow state, not a versioned artifact.

### 6.3 Multiple Concurrent Changes

**Not supported in v1.** One active change at a time. `aiv begin` fails if a
change is already active. Rationale: concurrent changes on the same branch create
ambiguity about which commit belongs to which change. This can be revisited if
demand arises.

### 6.4 Abandoning a Change

```bash
aiv abandon
# → clears .aiv/change.json without generating a packet
# → evidence files from the abandoned change remain (they're per-file, not per-change)
# → commits made during the change remain in git history
```

This is the escape hatch for "I started a change but decided not to finish it."

---

## 7. Workflow Modes

### 7.1 Configuration

`.aiv/config.yml` (or `.aiv.yml` at repo root):

```yaml
workflow:
  mode: direct          # "direct" (push to main) or "pr" (feature branches + PRs)
  protected_branches:
    - main
    - release/*
```

### 7.2 Direct Mode (Our Workflow)

For teams pushing directly to a protected branch.

| Step | Tool | What Happens |
|------|------|-------------|
| Start change | `aiv begin "name"` | Creates `.aiv/change.json` |
| Commit | `git commit` | Pre-commit: checks active change, generates evidence |
| More commits | `git commit` | Same — each commit updates relevant evidence files |
| Close change | `aiv close` | Generates `PACKET_<name>.md`, validates, commits |
| Push | `git push` | Pre-push: checks no open changes |

**Enforcement:** Pre-commit hook + pre-push hook. No CI gate required (but
recommended via `aiv audit` in CI).

### 7.3 PR Mode

For teams using feature branches and pull requests.

| Step | Tool | What Happens |
|------|------|-------------|
| Create branch | `git checkout -b feat/x` | No AIV action needed |
| Commit | `git commit` | Pre-commit: generates evidence (no change context required on feature branches) |
| Push + open PR | `git push` | CI guard activates |
| PR review | CI guard | Auto-generates or validates packet, runs `aiv check` |
| PR merge | GitHub | Packet committed to main, SVP session closed |

**Enforcement:** CI guard on PR (primary), pre-commit hook (advisory on feature
branches, strict on protected branches).

### 7.4 Mode Detection

If `workflow.mode` is not configured, the tooling infers the mode:

1. If the current branch is in `protected_branches` → **direct mode** behavior
   (require active change context).
2. If the current branch is NOT in `protected_branches` → **PR mode** behavior
   (advisory evidence collection, no change context required).
3. Default `protected_branches` if unconfigured: `[main, master]`.

---

## 8. Hook Behavior

### 8.1 Pre-Commit Hook

#### Direct Mode (on protected branch)

```
IF no .aiv/change.json exists:
  BLOCK with message:
    "No active change context. Run `aiv begin <name>` before committing."

IF .aiv/change.json exists:
  Generate/update evidence file(s) for committed source files
  Update .aiv/change.json with commit SHA and file list
  ALLOW commit
```

#### PR Mode (on feature branch)

```
Generate/update evidence file(s) for committed source files
ALLOW commit (no change context required)
```

#### Both Modes: Evidence-Only Commits

Commits that contain ONLY evidence files or packets (no functional files) are
always allowed. This permits `aiv close` to commit the packet without triggering
the hook's functional-file check.

### 8.2 Pre-Push Hook

#### Direct Mode

```
IF .aiv/change.json exists AND has commits:
  BLOCK with message:
    "Open change '<name>' has uncommitted verification.
     Run `aiv close` to generate the verification packet, or
     `aiv abandon` to discard the change context."

IF no .aiv/change.json:
  ALLOW push
```

#### PR Mode

```
ALLOW push (CI guard is the enforcement gate)
```

### 8.3 Hook Installation

`aiv init` installs both hooks and configures the workflow mode:

```bash
aiv init
# → creates .aiv/config.yml with detected mode
# → installs pre-commit hook
# → installs pre-push hook
# → creates .github/aiv-evidence/ directory
# → creates .github/aiv-packets/ directory
```

---

## 9. CLI Commands

### 9.1 `aiv begin <name>`

Opens a new change context.

```
Usage: aiv begin <name> [--description TEXT]

Arguments:
  name          Identifier for this change (used in packet filename).
                Must be lowercase, alphanumeric + hyphens.

Options:
  --description  Human-readable description of the change.

Behavior:
  1. Checks no active change exists (fails if one does).
  2. Creates .aiv/change.json with name, timestamp, empty commits list.
  3. Prints confirmation: "Change 'enforcement-gap-fix' started."

Example:
  aiv begin enforcement-gap-fix --description "Close --no-verify bypass"
```

### 9.2 `aiv close`

Closes the active change and generates a verification packet.

```
Usage: aiv close [--skip-tests] [--requirement TEXT]

Options:
  --skip-tests   Skip running the full test suite (use cached results).
  --requirement  Quoted requirement text for Class E evidence.

Behavior:
  1. Reads .aiv/change.json.
  2. Aggregates evidence from all commits in the change.
  3. Runs full test suite (Class A for the aggregate change).
  4. Generates PACKET_<name>.md in .github/aiv-packets/:
     a. Identification section (change_id, commits, head/base SHA)
     b. Claims aggregated from evidence files
     c. Classification (risk tier inferred from files changed)
     d. Evidence references (evidence file + commit SHA per claim)
     e. Known limitations
  5. Validates the packet (runs `aiv check`).
  6. Commits the packet to git.
  7. Clears .aiv/change.json.

Example:
  aiv close --requirement "§9.1 enforcement gap identified in audit"
```

### 9.3 `aiv abandon`

Abandons the active change without generating a packet.

```
Usage: aiv abandon [--force]

Options:
  --force  Skip confirmation prompt.

Behavior:
  1. Reads .aiv/change.json.
  2. Prompts for confirmation (unless --force).
  3. Clears .aiv/change.json.
  4. Does NOT delete evidence files or revert commits.
  5. Prints warning: "Change 'name' abandoned. N commits remain unpacketed."

Example:
  aiv abandon --force
```

### 9.4 `aiv status`

Shows the current change context and evidence state.

```
Usage: aiv status

Output:
  Active change: enforcement-gap-fix (started 2026-02-08T19:00)
  Commits: 3
  Files changed: 5
  Evidence files: 5 (all current)
  Unpacketed: Yes — run `aiv close` to generate packet.
```

### 9.5 `aiv commit` (Modified)

The existing `aiv commit` command is modified:

- **Old behavior:** Generates `VERIFICATION_PACKET_*.md`, prompts for overwrite.
- **New behavior:** Generates `EVIDENCE_*.md` in `.github/aiv-evidence/`. No
  overwrite prompt (overwrite is expected). Updates `.aiv/change.json`.

The command still accepts the same flags (`--requirement`, `--diff`, etc.) and
performs the same evidence collection. Only the output location and naming change.

---

## 10. Spec Amendment

### 10.1 Change to Appendix B (Packet Schema)

Current:
```yaml
identification:
  pr_id: integer   # REQUIRED
  pr_url: string   # REQUIRED
```

Amended:
```yaml
identification:
  repository: string          # REQUIRED

  # Change identifier — exactly ONE of the following MUST be present:
  pr_id: integer              # REQUIRED for PR/MR workflows
  change_id: string           # REQUIRED for direct-to-main workflows

  pr_url: string              # REQUIRED if pr_id present
  head_sha: string            # REQUIRED — immutable anchor
  base_sha: string            # REQUIRED
  commit_range: [string]      # RECOMMENDED — all commit SHAs in this change

  # Evidence layer references (NEW)
  evidence_refs:
    - file: string            # Evidence file name (e.g., "EVIDENCE_AUDITOR.md")
      commit_sha: string      # Commit SHA when evidence was generated
      classes: [A, B, C, F]   # Evidence classes present in this file
```

### 10.2 Change to §1.6.1 (Per-Change Requirements)

Current:
> A single change (PR/MR) either satisfies these requirements or it does not.

Amended:
> A single change either satisfies these requirements or it does not. A "change"
> is identified by a `pr_id` (for PR/MR workflows) or a `change_id` (for
> direct-to-main workflows). See §B.1 for identification requirements.

### 10.3 New Section: §6.11 Evidence File References

> Verification packets MAY reference per-file evidence files stored in the
> repository. Evidence file references MUST include a commit SHA that pins
> the reference to a specific version of the evidence file, satisfying the
> immutability requirement of §3.3 via git's content-addressed storage.
>
> Evidence files are NOT AIV Packets. They are artifacts referenced BY packets.
> Validators MUST NOT validate evidence files against the packet schema.

### 10.4 Change to §11 (Evidence Integrity Controls)

Add:
> For repositories using per-file evidence files (§6.11), the evidence file's
> git history constitutes an auditable chain of custody. Each version of the
> evidence file is an immutable git blob, retrievable via `git show <sha>:<path>`.
> This satisfies the Content Integrity and Reference Stability requirements of §3.3.

---

## 11. SVP Integration

### 11.1 Session Anchoring

SVP sessions currently anchor to `pr_number`. The amendment adds `change_id` as
an alternative anchor:

```python
class SVPSession(BaseModel):
    pr_number: int | None = None       # For PR workflows
    change_id: str | None = None       # For direct-to-main workflows
    # ... existing fields ...
```

Session storage:
- PR workflow: `.svp/session-pr42.json` (unchanged)
- Direct workflow: `.svp/session-enforcement_gap_fix.json`

### 11.2 Phase 0 (Sanity Gate)

Phase 0 currently checks "AIV-Guard passed." For direct mode, it checks
"packet exists and `aiv check` passes":

```
PR mode:     session.aiv_guard_passed = CI guard result
Direct mode: session.aiv_guard_passed = (PACKET_<change_id>.md exists AND validates)
```

### 11.3 SVP Lifecycle Integration

```
aiv begin "name"          → svp session auto-created (if SVP enabled)
aiv svp predict ...       → prediction recorded against change_id
aiv svp trace ...         → trace recorded against change_id
aiv svp probe ...         → probe recorded against change_id
aiv close                 → generates packet, SVP Phase 0 gate checked
aiv svp ownership ...     → ownership commit recorded
aiv svp validate          → full SVP validation against change_id
```

---

## 12. Migration Plan

### 12.1 Phase 1: Directory Split

Move existing evidence files to the new location:

```bash
# Create new directory
mkdir .github/aiv-evidence

# Move and rename evidence files (per-file evidence)
# Example: VERIFICATION_PACKET_AUDITOR.md → EVIDENCE_AUDITOR.md
# Keep: hand-written packets that are already Layer 2 (e.g., VERIFICATION_PACKET_SVP_AI_VALIDATOR_RULES.md)
```

**Decision required:** Which existing packets are Layer 1 (evidence, move) vs.
Layer 2 (packets, keep)? See §12.3 for classification criteria.

### 12.2 Phase 2: Tooling Updates

1. Modify `aiv commit` to output to `.github/aiv-evidence/` with `EVIDENCE_` prefix.
2. Implement `aiv begin`, `aiv close`, `aiv abandon`, `aiv status`.
3. Refactor pre-commit hook for change-context awareness.
4. Refactor pre-push hook for unclosed-change detection.
5. Update `aiv init` for new directory structure and config.

### 12.3 Packet Classification (Existing Files)

Criteria for classifying existing `VERIFICATION_PACKET_*.md` files:

**Layer 1 (Evidence) — move to `aiv-evidence/`:**
- Auto-generated by `aiv commit`
- Named after a single source file
- Contains per-file Class A/B/C/F evidence
- Has been overwritten (multiple versions in git history)

**Layer 2 (Packet) — keep in `aiv-packets/`:**
- Hand-written or covers a logical change
- Contains claims spanning multiple files
- Named after a feature/change, not a source file
- Examples: `VERIFICATION_PACKET_SVP_AI_VALIDATOR_RULES.md`,
  `VERIFICATION_PACKET_PHASES_5_8_CLAIM_MATRIX.md`

### 12.4 Phase 3: Spec Amendment

Update `SPECIFICATION.md` per §10 of this document.

### 12.5 Phase 4: Retroactive Packets

Generate Layer 2 packets for historical changes that currently only have Layer 1
evidence. This addresses the 7 "overwritten" packets identified in the discovery.

---

## 13. Edge Cases

### 13.1 Commit Without `aiv begin`

**Scenario:** Developer commits to a protected branch without running `aiv begin`.

**Behavior (direct mode):** Pre-commit hook blocks the commit with:
```
ERROR: No active change context.
Run `aiv begin <name>` to start a tracked change before committing.
```

**Behavior (PR mode):** Allowed — feature branches don't require change context.

**Escape hatch:** `git commit --no-verify` bypasses the hook. The pre-push hook
catches this: it sees commits without a closed change and blocks the push. The
CI audit job (`aiv audit --commits`) catches it if the push somehow succeeds.

### 13.2 Multiple Files in One Commit

**Scenario:** Developer commits 3 source files in one commit.

**Behavior:** Pre-commit hook generates 3 evidence files (one per source file).
All 3 are staged and included in the commit. `.aiv/change.json` records one
commit entry with all 3 files listed.

**Note:** The current pre-commit hook enforces 1 functional file per commit.
Under the new architecture, this constraint can be **relaxed** because the
verification boundary is the change (Layer 2), not the commit. However, this is
a configuration option — teams may choose to keep the 1-file-per-commit rule.

```yaml
# .aiv/config.yml
hooks:
  atomic_commits: true    # Enforce 1 functional file per commit (default: false)
```

### 13.3 Push Without `aiv close`

**Scenario:** Developer has an active change and tries to push.

**Behavior:** Pre-push hook blocks with:
```
ERROR: Open change 'enforcement-gap-fix' has 3 commits without a verification packet.
Run `aiv close` to generate the packet, or `aiv abandon` to discard.
```

### 13.4 `aiv close` With No Commits

**Scenario:** Developer runs `aiv begin`, then `aiv close` without making any commits.

**Behavior:** `aiv close` fails with:
```
ERROR: Change 'name' has no commits. Nothing to verify.
Run `aiv abandon` to discard, or make commits first.
```

### 13.5 Evidence File Naming Collision

**Scenario:** Two source files have the same basename:
- `src/aiv/lib/models.py`
- `src/aiv/guard/models.py`

Both would map to `EVIDENCE_MODELS.md` under the §4.2 naming convention.

**Resolution:** Include the parent directory in the normalized name:
- `src/aiv/lib/models.py` → `EVIDENCE_LIB_MODELS.md`
- `src/aiv/guard/models.py` → `EVIDENCE_GUARD_MODELS.md`

The normalization algorithm:
1. Take the path relative to the repo root.
2. Remove the `src/aiv/` prefix (or configurable source root).
3. Replace path separators with `_`.
4. Remove the file extension.
5. Uppercase.

Examples:
- `src/aiv/lib/auditor.py` → `EVIDENCE_LIB_AUDITOR.md`
- `src/aiv/hooks/pre_push.py` → `EVIDENCE_HOOKS_PRE_PUSH.md`
- `tests/unit/test_auditor.py` → `EVIDENCE_TESTS_UNIT_TEST_AUDITOR.md`

This eliminates collisions at the cost of longer filenames. A configurable
`evidence_name_depth` (default: 2 path components) can control this.

### 13.6 Evidence File for Non-Python Files

**Scenario:** Developer commits a YAML config file or a JavaScript file.

**Behavior:** Evidence collection falls back to non-AST mode (grep-based test
relevance, no per-symbol coverage). Evidence file still generated with whatever
evidence is available. The Layer 2 packet may note this as a known limitation.

### 13.7 Change Spanning Multiple Days / Sessions

**Scenario:** Developer runs `aiv begin` on Monday, commits on Tuesday and
Wednesday, runs `aiv close` on Thursday.

**Behavior:** Works fine. `.aiv/change.json` accumulates commits over time.
The packet's `created_at` is when `aiv close` runs. The `commit_range` shows
all commits from Monday through Wednesday.

**Risk:** If another developer pushes to main between Monday and Thursday, there
may be merge conflicts or stale evidence. This is the same risk as any long-lived
branch and is not specific to AIV.

### 13.8 `git commit --no-verify` During Active Change

**Scenario:** Developer has an active change but uses `--no-verify` to skip the
pre-commit hook.

**Behavior:** The commit succeeds but `.aiv/change.json` is NOT updated (the
hook didn't run). When `aiv close` runs, it detects commits on the branch that
are not in `.aiv/change.json` and warns:

```
WARNING: 2 commits found on branch since `aiv begin` that are not tracked
in the change context. These commits may have been made with --no-verify.

Untracked commits:
  abc1234 — feat(x): some change
  def5678 — fix(y): another change

Options:
  1. Include them: `aiv close --include-untracked`
  2. Exclude them: `aiv close` (they will not be in the packet)
  3. Abort: Ctrl+C
```

### 13.9 Renaming a Change

**Scenario:** Developer wants to rename an active change.

**Behavior:**
```bash
aiv rename "new-name"
# → updates .aiv/change.json name field
```

### 13.10 Two Developers, Same Branch (Direct Mode)

**Scenario:** Developer A runs `aiv begin "feature-x"`. Developer B also pushes
to main.

**Behavior:** `.aiv/change.json` is gitignored — it's local state. Developer A's
change context is independent of Developer B's commits. When Developer A runs
`aiv close`, the packet only references Developer A's commits.

Developer B should also have their own `aiv begin`/`aiv close` cycle. If they
don't, the pre-push hook on their end blocks their push (no closed change).

**Risk:** Developer A's evidence files may be overwritten by Developer B's
commits to the same source files. The packet references evidence at specific
commit SHAs, so the reference remains valid — but the evidence reflects Developer
B's version, not Developer A's. This is a known limitation of direct-to-main
workflows and is documented in the packet's `known_limitations`.

### 13.11 Orphaned Change Context

**Scenario:** Developer runs `aiv begin`, makes commits, then switches branches
or the `.aiv/change.json` is deleted.

**Behavior:** `aiv status` shows "No active change." The commits exist in git
but are unpacketed. Developer can:

1. `aiv begin "name"` and `aiv close --include-untracked` to retroactively
   package the commits.
2. Accept that those commits are unpacketed (the auditor will flag them).

### 13.12 CI/CD Integration (PR Mode)

**Scenario:** CI guard needs to auto-generate a packet on PR merge.

**Behavior:** The CI guard job:
1. Detects PR number from GitHub context.
2. Lists all files changed in the PR.
3. Collects evidence files from `.github/aiv-evidence/` at the PR's head SHA.
4. Generates `PACKET_PR_<N>.md` with claims aggregated from evidence.
5. Commits the packet to the merge commit (or as a follow-up commit).

This is the PR-mode equivalent of `aiv close` but runs in CI.

### 13.13 Hotfix / Emergency Bypass

**Scenario:** Production is down. Developer needs to push a fix immediately.

**Behavior:** The spec's Exception Protocol (§10) already handles this. Developer:
1. Uses `git push --no-verify` to bypass the pre-push hook.
2. The CI audit job flags the unpacketed commit.
3. Developer creates a retroactive packet with `aiv begin "hotfix-123" && aiv close --include-untracked`.
4. The packet includes an `exception` section per §10.

---

## 14. Adopter Profiles

### 14.1 Solo Developer (Startup)

**Workflow:** Push to main, no PRs.
**Mode:** `direct`
**Experience:**
```bash
aiv init                              # one-time setup
aiv begin "user-auth"                 # start feature
git commit ...                        # evidence auto-collected
git commit ...                        # evidence auto-collected
aiv close                             # packet generated
git push                              # ✅ push succeeds
```
**Effort:** Two extra commands (`begin`/`close`) per feature.
**Value:** Audit trail from day one. Investors see verified AI code.

### 14.2 Product Engineering Team (20+ Engineers)

**Workflow:** Feature branches + PRs.
**Mode:** `pr`
**Experience:**
```bash
aiv init                              # one-time setup (per-repo)
git checkout -b feat/payments
git commit ...                        # evidence auto-collected
git push && open PR                   # CI guard validates
# PR review happens
# PR merge → packet auto-generated
```
**Effort:** Zero extra commands. Evidence collection is invisible.
**Value:** SOC2-ready audit trail. Every PR has a verification packet.

### 14.3 Regulated Enterprise

**Workflow:** PRs + formal review + signed attestations.
**Mode:** `pr` with signed attestations enabled.
**Experience:** Same as 14.2, plus:
- SVP sessions required (Class G).
- Attestations signed via GPG/sigstore.
- Packets stored in immutable storage (OCI registry, WORM).
**Effort:** High — but they already have formal review processes.
**Value:** Regulatory compliance. Auditable verification chain.

---

## 15. Open Questions

### Q1: Should `aiv begin` be required for single-commit changes?

**Argument for:** Consistency. Every change goes through the same lifecycle.
**Argument against:** Overhead for trivial changes (docs, formatting).
**Possible resolution:** Fast-track patterns in config that auto-close on commit:

```yaml
workflow:
  fast_track:
    - "docs/**"          # Documentation changes auto-close
    - "*.md"             # Markdown-only changes auto-close
    - ".github/**/*.yml" # CI config auto-close
```

### Q2: Should evidence files be gitignored?

**Argument for:** They're transient artifacts, regenerated each commit. Clutters diff.
**Argument against:** They provide valuable context in code review. And Layer 2
packets reference them by commit SHA — they must be in git for that to work.
**Resolution:** Keep them in git. They are referenced artifacts.

### Q3: How does this interact with the existing `aiv generate` command?

`aiv generate` currently scaffolds a verification packet template. Under the new
architecture, it should scaffold a Layer 2 packet template. Evidence files are
never manually created — they are always auto-generated.

### Q4: What happens to the existing 60+ VERIFICATION_PACKET_*.md files?

See §12.3 for classification criteria. Most are Layer 1 (evidence) and should be
renamed/moved. A few are Layer 2 (packets) and should be kept. A migration script
will handle this.

### Q5: Should `change.json` track the diff/patch for each commit?

**Argument for:** `aiv close` could verify that the evidence matches the actual diff.
**Argument against:** Redundant with git. `git diff base_sha..head_sha` gives the
full diff.
**Resolution:** Don't store diffs. Use git.

### Q6: Can a change span multiple branches?

**Resolution:** No. A change is scoped to a single branch. Cross-branch changes
are separate changes.

### Q7: Should `aiv close` auto-detect risk tier?

**Argument for:** Reduces manual classification burden.
**Argument against:** Risk classification requires human judgment (§5.1).
**Possible resolution:** Auto-suggest based on critical surface detection, but
require human confirmation for R2+.

### Q8: Where does the `--requirement` flag live?

Currently `aiv commit --requirement TEXT` embeds Class E (Intent) evidence in the
evidence file. Under the new architecture:
- **Layer 1 evidence files** contain per-file evidence (Class A, B, C, F).
- **Class E (Intent)** is change-level, not file-level — it documents WHY the
  change was made, not what a single file does.

**Possible resolution:** `--requirement` moves to `aiv close` (already shown in
§9.2). Class E is a Layer 2 concern. Evidence files don't include Class E.

### Q9: What about the Windows cp1252 encoding issue?

During the session that triggered this investigation, `git commit` raised a
`UnicodeDecodeError` due to Windows' default cp1252 encoding struggling with
UTF-8 content in evidence files. The commit succeeded but the error is a warning
that evidence generation should explicitly use `encoding="utf-8"` for all
subprocess calls and file I/O.

---

## 16. Impact on Existing Modules

### 16.1 Parser (`src/aiv/lib/parser.py`)

Currently parses `VERIFICATION_PACKET_*.md` files into `VerificationPacket`
models. Under the new architecture:

- **Layer 2 packets** (`PACKET_*.md`) are validated by the parser. These conform
  to the Appendix B schema and contain the Identification, Claims, Evidence
  References, Classification, Attestation, and Known Limitations sections.
- **Layer 1 evidence files** (`EVIDENCE_*.md`) are NOT parsed by the packet
  parser. They are raw evidence artifacts with a different structure. A separate
  lightweight parser (or no parser — just read the markdown) handles them.

**Change required:** Update `parser.py` glob from `VERIFICATION_PACKET_*.md` to
`PACKET_*.md`, or make it configurable.

### 16.2 Auditor (`src/aiv/lib/auditor.py`)

Currently scans `VERIFICATION_PACKET_*.md` for quality issues. Under the new
architecture, the auditor needs two modes:

- **Layer 2 audit** (existing rules, adapted): Scan `PACKET_*.md` for
  COMMIT_PENDING, CLASS_E_NO_URL, TODO_PRESENT, FIX_NO_CLASS_F, etc.
- **Layer 1 audit** (new): Scan `EVIDENCE_*.md` for staleness (evidence file
  not updated since the source file changed), broken `Previous:` chains, and
  missing evidence classes.
- **Cross-layer audit** (new): Check that every functional commit is covered by
  a Layer 2 packet. Flag "unpacketed" commits.

**Change required:** Extend `PacketAuditor` with `audit_evidence()` and
`audit_coverage()` methods. Update `audit()` glob pattern.

### 16.3 Validators (`src/aiv/lib/validators/`)

Validation rules apply to **Layer 2 packets only**. Evidence files are not
validated against the packet schema.

| Validator | Layer 2 Packet | Layer 1 Evidence |
|-----------|---------------|------------------|
| `structure.py` (E002/E005/E008) | ✅ Applies | ❌ Not applicable |
| `links.py` (E004/E009) | ✅ Applies (evidence refs must be SHA-pinned) | ❌ Not applicable |
| `evidence.py` (E010/E012-E018/E020) | ✅ Applies | ❌ Not applicable |
| `zero_touch.py` (E008) | ✅ Applies | ❌ Not applicable |
| `anti_cheat.py` (E011) | ✅ Applies | ❌ Not applicable |
| `pipeline.py` | ✅ Orchestrates Layer 2 validation | ❌ Skips evidence files |

**Change required:** Pipeline must distinguish `PACKET_*.md` from `EVIDENCE_*.md`
and only validate Layer 2 files.

### 16.4 Evidence Collector (`src/aiv/lib/evidence_collector.py`)

The evidence collector's output changes location and naming:
- **Old:** Writes `VERIFICATION_PACKET_<NAME>.md` to `.github/aiv-packets/`
- **New:** Writes `EVIDENCE_<NAME>.md` to `.github/aiv-evidence/`

The collection logic (AST analysis, test coverage, downstream callers) is
unchanged. Only the output path, filename prefix, and header format change.

**Change required:** Update output path and prefix. Add `Previous:` header.
Remove overwrite prompt.

### 16.5 Guard (`src/aiv/guard/runner.py`)

The CI guard currently resolves packets by PR. Under the new architecture:
- **PR mode:** Guard resolves `PACKET_PR_<N>.md` and validates it.
- **Direct mode:** Guard is optional (hooks are the enforcement layer).

**Change required:** Update packet resolution to look for `PACKET_PR_*.md`
instead of `VERIFICATION_PACKET_*.md`.

### 16.6 CI Workflows

- `.github/workflows/ci.yml` — `protocol-audit` job runs `aiv audit`. Needs to
  scan both `aiv-evidence/` and `aiv-packets/`.
- `.github/workflows/aiv-guard-python.yml` — Validates PRs. Needs updated packet
  resolution path.

---

## 17. Test Impact Inventory

Existing tests that reference packet naming/paths and will need updating:

| Test File | What References Packets | Change Needed |
|-----------|------------------------|---------------|
| `tests/unit/test_auditor.py` | Scans `VERIFICATION_PACKET_*.md` | Update glob, add Layer 1/Layer 2 tests |
| `tests/unit/test_validators.py` | Fixture packets use old naming | Update fixtures |
| `tests/unit/test_parser.py` | Parses `VERIFICATION_PACKET_*.md` | Update fixtures |
| `tests/unit/test_guard.py` | Resolves packets by name | Update resolution logic |
| `tests/unit/test_pre_commit_hook.py` | Checks for paired packets | Rewrite for change-context logic |
| `tests/unit/test_pre_push_hook.py` | Scans for per-commit packets | Rewrite for unclosed-change logic |
| `tests/unit/test_evidence_collector.py` | Checks output naming | Update output path assertions |
| `tests/integration/test_full_workflow.py` | End-to-end packet creation | Update for two-layer workflow |
| `tests/integration/test_e2e_compliance.py` | Full compliance checks | Update packet naming in fixtures |
| `tests/conftest.py` | `valid_minimal_packet` etc. | Add Layer 2 packet fixtures |

**New tests needed:**
- `test_change_lifecycle.py` — `aiv begin`, `aiv close`, `aiv abandon`, `aiv status`
- `test_evidence_layer.py` — Evidence file creation, overwrite, `Previous:` chain
- `test_two_layer_integration.py` — End-to-end: begin → commit → close → validate

---

## 18. Migration Checklist

Detailed checklist for the migration (supplements §12):

- [ ] Create `.github/aiv-evidence/` directory
- [ ] Add `.aiv/change.json` to `.gitignore`
- [ ] Classify existing 60+ `VERIFICATION_PACKET_*.md` files (Layer 1 vs Layer 2)
- [ ] Write migration script to rename/move Layer 1 files
- [ ] Rename Layer 2 packets from `VERIFICATION_PACKET_*.md` to `PACKET_*.md`
- [ ] Update `VERIFICATION_PACKET_TEMPLATE.md` → `PACKET_TEMPLATE.md` with new schema
- [ ] Update `src/aiv/lib/evidence_collector.py` output path and naming
- [ ] Remove overwrite prompt from `aiv commit`
- [ ] Add `Previous:` header to evidence file generation
- [ ] Implement `aiv begin` command
- [ ] Implement `aiv close` command
- [ ] Implement `aiv abandon` command
- [ ] Implement `aiv status` command
- [ ] Refactor `src/aiv/hooks/pre_commit.py` for change-context awareness
- [ ] Refactor `src/aiv/hooks/pre_push.py` for unclosed-change detection
- [ ] Update `src/aiv/lib/auditor.py` for two-layer scanning
- [ ] Update `src/aiv/lib/parser.py` glob pattern
- [ ] Update `src/aiv/lib/validators/pipeline.py` to skip evidence files
- [ ] Update `src/aiv/guard/runner.py` packet resolution
- [ ] Update `src/aiv/cli/main.py` — add begin/close/abandon/status commands
- [ ] Update `.aiv.yml` / `.aiv/config.yml` with workflow mode
- [ ] Update `aiv init` for new directory structure
- [ ] Update all test fixtures
- [ ] Write new tests for change lifecycle
- [ ] Update `SPECIFICATION.md` per §10
- [ ] Update `SVPSession` model with `change_id`
- [ ] Update SVP CLI commands to accept `--change` alongside `--pr`
- [ ] Update `.github/workflows/ci.yml` protocol-audit paths
- [ ] Update `.github/workflows/aiv-guard-python.yml` packet resolution
- [ ] Generate retroactive Layer 2 packets for historical changes
- [ ] Run full test suite, verify 0 regressions

---

## 19. Decision Log

| # | Decision | Rationale | Date |
|---|----------|-----------|------|
| D1 | Two-layer architecture (evidence + packets) | Separates file-level evidence (mutable, O(files)) from change-level verification (immutable, O(changes)). Resolves granularity mismatch with spec. | 2026-02-08 |
| D2 | `change_id` as alternative to `pr_id` | Enables direct-to-main workflows without PRs. Backward compatible — PR teams use `pr_id` as before. | 2026-02-08 |
| D3 | Evidence files overwrite, packets don't | Evidence files track current state (mutable). Packets are immutable verification records. Git history preserves evidence chain. | 2026-02-08 |
| D4 | Single active change at a time | Avoids ambiguity in commit-to-change assignment. Can be revisited. | 2026-02-08 |
| D5 | `.aiv/change.json` is gitignored | Local workflow state, not a versioned artifact. Different developers have independent change contexts. | 2026-02-08 |
| D6 | Pre-commit hook relaxed on feature branches (PR mode) | Feature branches don't need change context — the PR is the change boundary. | 2026-02-08 |
| D7 | Evidence file naming includes parent directory | Prevents collisions when multiple source files share the same basename (e.g., `lib/models.py` vs `guard/models.py`). | 2026-02-08 |
| D8 | Class E (Intent) moves to Layer 2 | Intent evidence is change-level ("why this change?"), not file-level. `--requirement` flag moves to `aiv close`. | 2026-02-08 |
| D9 | Validation rules apply to Layer 2 only | Evidence files are raw artifacts, not AIV Packets. Validators must not validate them against the packet schema. | 2026-02-08 |
| D10 | Option B (push-based) and D (per-commit) rejected | Push is not a meaningful verification boundary. Per-commit causes O(n) scaling and SVP disconnect. | 2026-02-08 |
