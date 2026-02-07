# Case Study: AI First-Pass SVP Audit

**Why this matters:** This document is the empirical proof that the AIV+SVP protocol
works. An AI was given 3 PRs to verify. It produced structured sessions. Those
sessions were then audited by executing every claim. The results expose exactly
where AI verification succeeds, where it fails, and what the protocol must enforce.

**Author:** Human + AI collaborative analysis
**Date:** 2026-02-07
**Sessions:** PR#1 (AIV_IMPLEMENTATION), PR#2 (AIV_GUARD), PR#3 (GUARD_REFACTOR)

---

## 1. The Scorecard

| Phase | Accuracy | Value Type | Failure Mode |
| :--- | :--- | :--- | :--- |
| **Prediction** | 74% (22/31) | Architectural mapping | Hallucination — inventing functions that don't exist |
| **Trace (code-read)** | 87% (13/15) | Logic navigation | Assumption — misreading complex conditionals |
| **Trace (execution-verified)** | 100% (10/10) | Logic navigation | None after corrections |
| **Probe findings** | **100% (11/11)** | **Bug discovery** | **None — 8 real bugs found in "passing" code** |
| **Falsification** | **40% (8/20)** | **Pure theater** | Parroting — repeating wrong numbers from predictions |

---

## 2. The Core Discovery: Hunter vs. Validator

The AI is a **superb Hunter** but a **dangerous Validator**.

- **The Hunter (Probe Phase — 100%):** Reading code adversarially to find bugs,
  the AI found logic collisions, missing regex patterns, hardcoded assumptions, and
  a header injection vulnerability. Every finding was real. This is the value.

- **The Validator (Falsification Phase — 40%):** Attempting to "prove" claims true,
  the AI defaulted to pattern matching. It parroted "12 models" because it predicted
  "12 models," even though the code had 13. It validated theater, not logic.

**Conclusion:** The AI is not a "Verifier Jr." It is an **Automated Adversary**.

---

## 3. The Hallucination Cascade

The audit revealed a recursive failure loop unique to AI:

1. **Predict:** AI predicts `sanitize_shell_input` exists.
2. **Trace:** AI "mentally traces" that non-existent function.
3. **Probe:** AI writes a falsification scenario testing that function.
4. **Result:** A perfectly valid JSON file describing a reality that doesn't exist.

For an AI, "Mental Simulation" is a synonym for "Confidently Incorrect Hallucination."
This is why **S015** now requires AI sessions to include `verified_output` from
actual execution — mental simulation is banned for AI verifiers.

---

## 4. Bugs Found (All Real)

The probe phase found **8 architectural flaws** that 371 unit tests missed:

| # | Bug | File | Severity |
|---|-----|------|----------|
| 1 | Parser treats `##` inside fenced code blocks as sections (header injection) | `parser.py` | **HIGH — FIXED** |
| 2 | E020 rule_id collision between pipeline.py and evidence.py | `pipeline.py` | Medium |
| 3 | `.py` files excluded from JS guard semantic analysis | `aiv-guard.yml` | Medium |
| 4 | Mutable branch list differs: JS checks 5, Python checks 7 | `models.py` / `aiv-guard.yml` | Medium |
| 5 | Section detection uses substring `includes()` not heading match | `aiv-guard.yml` | Medium |
| 6 | `node`/`npm` hardcoded in manifest validation (rejects Python CI) | `manifest.py` | Medium |
| 7 | Zero-test manifests pass Class A validation | `manifest.py` | **High** |
| 8 | No retry logic on 429 rate limits | `github_api.py` | Medium |

Bug #1 was fixed immediately (commit `304d47e`). The others remain as documented tech debt.

---

## 5. Execution Verification Detail

### Verification Method

- **Round 1 (code-read):** Traces written by reading source and mentally simulating.
  Found 2 errors: one factually wrong (`sod_mode` S3), one misleading (critical surfaces).
- **Round 2 (execution-verified):** Every edge case actually executed via Python.
  All 10 testable traces confirmed correct after corrections. PR#2 traces (JS
  workflow) remain code-read only — cannot be executed from Python.

### PR#1: AIV_IMPLEMENTATION — Traces (5/5 verified)

| Trace | Edge Case | Result |
|-------|-----------|--------|
| `ArtifactLink.from_url` | `/blob/abcdef1/` (7-char hex) | `is_immutable=True` — **CONFIRMED** |
| `PacketParser.parse` | `##` inside fenced code block | 8 sections (should be 7) — **BUG CONFIRMED** |
| `ValidationPipeline.validate` | Mutable `/blob/main/` link | E004 BLOCK + pipeline continues — **CONFIRMED** |
| CLI check | Piped stdin without `-` arg | "No packet body provided", exit 1 — **CONFIRMED** |
| `AntiCheatScanner.scan_diff` | Production assertion deletion | 0 findings, 0 test files — **CONFIRMED** |

### PR#2: AIV_GUARD — Traces (0/5 verified — JS workflow)

All 5 traces are **code-read only**. The 2244-line JS workflow runs inside GitHub
Actions and cannot be executed locally.

### PR#3: GUARD_REFACTOR — Traces (5/5 verified)

| Trace | Edge Case | Result |
|-------|-----------|--------|
| `GuardRunner._check_critical_surfaces` | Renamed `helpers.py`, empty patch | Path: [], Semantic: [] — **CONFIRMED** |
| `validate_canonical` | `sod_mode='S3'` | BLOCK CLS-003 immediately — **CONFIRMED** (was factually wrong, fixed) |
| `GuardResult.finalize` | WARN-only findings | `overall_result=PASS` — **CONFIRMED** |
| `GitHubAPI._request_bytes` | 429 HTTPError | `GitHubAPIError(status_code=429)`, no retry — **CONFIRMED** |
| `validate_class_a_manifest` | `{pass:0, fail:0, skip:0}` | `errors=[]`, validation passes — **CONFIRMED** |

### Trace Corrections Applied

1. **Critical surfaces trace:** Original said "would miss the file" without noting
   path patterns still catch auth-named files. Fixed with explicit path + semantic check.
2. **sod_mode trace:** Original claimed S3 "passes silently for R0/R1". Execution
   proved `sod_mode not in ("S0", "S1")` blocks S3 before R2+ check runs.

---

## 6. Falsification Scenario Detail

### PR#1 (7 scenarios — 2 confirmed, 2 broken, 2 wrong, 1 ambiguous)

| Claim | Scenario | Result |
|-------|----------|--------|
| C-001 | "12 models, all BaseModel frozen" | **WRONG** — actual 13; 4 are Enums |
| C-002 | `/blob/main/` produces E004 BLOCK | **CONFIRMED** |
| C-003 | `aiv check` exit 0 on valid packet | **AMBIGUOUS** — only with `--no-strict` |
| C-004 | Call `sanitize_shell_input` | **BROKEN** — hallucinated function |
| C-005 | Call `DiffAnalyzer.parse_diff` | **BROKEN** — hallucinated class |
| C-006 | Every model has `frozen=True` | **CONFIRMED** (9/9 BaseModels) |
| C-007 | "exactly 36 tests pass" | **WRONG** — suite has 371 |

### PR#2 (8 scenarios — 3 confirmed, 5 unverifiable)

| Claim | Scenario | Result |
|-------|----------|--------|
| C-001 | Workflow triggers on opened/edited/synchronize to main | **CONFIRMED** |
| C-002–C-005, C-007 | Various JS runtime checks | **UNVERIFIABLE** — JS runtime |
| C-006 | `src/auth/login.py` triggers critical surface | **CONFIRMED** via `_CS_PATH` |
| C-008 | Workflow writes JSON to disk | **CONFIRMED** — `writeFileSync` found |

### PR#3 (5 scenarios — 3 confirmed, 1 wrong, 1 unverifiable)

| Claim | Scenario | Result |
|-------|----------|--------|
| C-001 | "exactly 5 Python files" | **WRONG** — actual 7 |
| C-002 | head_sha binding check | **CONFIRMED** — CT-005 BLOCK |
| C-003 | Workflow < 100 lines, invokes guard | **CONFIRMED** (36 lines) |
| C-004 | test_guard.py >= 36 test functions | **CONFIRMED** (36 collected) |
| C-005 | No files modified outside guard scope | **UNVERIFIABLE** — commit-scope |

### Root Cause Analysis

1. **Hallucination propagation.** `sanitize_shell_input` and `DiffAnalyzer` were
   invented in predictions, carried into falsification scenarios. Garbage in, garbage out.
2. **Count parroting.** "12 models", "36 tests", "5 files" — all wrong because
   numbers were repeated from predictions instead of independently verified.
3. **Missing execution context.** Scenarios didn't specify `--no-strict`, which
   test file, or which commit. Ambiguity kills falsifiability.
4. **JS workflow gap.** 5 of 8 PR#2 scenarios require JS runtime. Should have
   been flagged unverifiable at authoring time.

---

## 7. Protocol Changes Implemented

This audit directly produced 4 changes to the SVP protocol:

| Change | Rule | What It Does |
|--------|------|-------------|
| **SessionType enum** | — | `human_verification` vs `ai_adversarial_triage` on `SVPSession` |
| **Execution Trace** | S015 | AI sessions BLOCK without `verified_output` on traces |
| **Falsification-as-Code** | S016 | AI sessions BLOCK without `test_code` on scenarios |
| **Parser bug fix** | — | Fenced code block headings no longer parsed as sections |

Additionally: `StateTransition.line_number` was removed from the model entirely
because line numbers are fragile references that rot with every edit.

---

## 8. What This Proves About AIV+SVP

### The protocol works.

The SVP process caught errors that would have been invisible without it:
- A factually wrong trace (sod_mode) that would have misled human reviewers
- 8 real bugs in code that passed 371 unit tests
- A header injection vulnerability in the parser

### AI verification is real — but only the adversarial part.

The probe phase (100% accuracy) is genuine value. The prediction and falsification
phases are scaffolding that exposes the AI's blind spots. The 40% falsification
rate proves that an AI cannot validate its own claims — it can only find bugs in
other code.

### The "Honest Protocol" is the right response.

Banning mental simulation (S015) and requiring code-as-falsification (S016) for AI
sessions doesn't weaken the protocol — it makes it honest. An AI that is forced to
execute its edge cases and write pytest snippets for its claims will either produce
verified work or fail loudly. Both outcomes are better than theater.

### Retrospective SVP clears architectural debt.

Running SVP sessions on existing PRs — after the code is merged — found issues
that pre-merge review missed. This is not a failure of pre-merge review; it's
proof that adversarial probing adds value at every stage of the lifecycle.
