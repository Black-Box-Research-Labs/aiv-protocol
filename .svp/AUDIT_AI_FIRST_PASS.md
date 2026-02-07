# AI First-Pass SVP Audit Scorecard

**Auditor:** cascade-ai-first-pass (self-audit)
**Date:** 2026-02-07
**Sessions audited:** PR#1 (AIV_IMPLEMENTATION), PR#2 (AIV_GUARD), PR#3 (GUARD_REFACTOR)

## Overall Results

| Category | Right | Wrong | Partial | Total | Accuracy |
|----------|-------|-------|---------|-------|----------|
| Predictions | 22 | 8 | 1 | 31 | 74% |
| Trace content (code-read only) | 13 | 2 | 0 | 15 | 87% |
| Trace content (execution-verified) | 10 | 0 | 0 | 10 | 100% |
| Probe findings | 11 | 0 | 0 | 11 | 100% |

## Verification Method

**Round 1 (code-read):** Traces written by reading source code and mentally
simulating execution. Found 2 errors: one factually wrong (sod_mode S3) and
one misleading (renamed file critical surface).

**Round 2 (execution-verified):** Each edge case actually executed via Python.
All 10 testable traces confirmed correct after corrections. PR#2 traces target
a JS workflow and cannot be executed from Python — these remain code-read only.

---

## PR#1: AIV_IMPLEMENTATION (R2, 7 claims)

### Prediction Errors (4 of 12)

- **"12 models"** → actual 13 (missed `FrictionScore`)
- **"computed property evidence_classes_present"** → it's a regular field
- **"sanitize_shell_input"** → hallucinated, does not exist
- **"DiffAnalyzer class"** → hallucinated, actual is `AntiCheatScanner`

### Trace Verification (5/5 execution-verified)

| Trace | Edge Case | Execution Result |
|-------|-----------|-----------------|
| ArtifactLink.from_url | `/blob/abcdef1/` (7-char hex) | `is_immutable=True` — **CONFIRMED** |
| PacketParser.parse | `##` inside fenced code block | 8 sections found (should be 7) — **BUG CONFIRMED** |
| ValidationPipeline.validate | Mutable `/blob/main/` link | E004 BLOCK + pipeline continues — **CONFIRMED** |
| CLI check | Piped stdin without `-` arg | "No packet body provided", exit 1 — **CONFIRMED** |
| AntiCheatScanner.scan_diff | Production assertion deletion | 0 findings, 0 test files — **CONFIRMED** |

### Findings Confirmed

- E020 rule_id collision (pipeline.py + evidence.py) → **REAL**
- Parser code block bug (no fenced block detection) → **REAL**

---

## PR#2: AIV_GUARD (R2, 8 claims)

### Prediction Errors (2 of 10)

- **"regex for section headers"** → actual uses `packetContent.includes(h)` (substring)
- **"artifact download via direct API call"** → actual is env-var inter-step communication

### Trace Verification (0/5 execution-verified — JS workflow, cannot run from Python)

All 5 traces are **code-read only**. The JS workflow runs inside GitHub Actions
and cannot be executed locally. These traces should be treated as unverified
mental models until a JS test harness or live CI run confirms them.

### Findings Confirmed

- `.py` excluded from `shouldFetchContentAtHead` → **REAL** (regex on line 605)
- Mutable branch list JS≠Python (5 vs 7) → **REAL**
- Substring `includes()` for section detection → **REAL**

---

## PR#3: GUARD_REFACTOR (R2, 5 claims)

### Prediction Errors (3 of 9)

- **"5 files"** → actual 7 (missed `__init__.py`, `__main__.py`)
- **"45-line workflow"** → actual 36 lines (parroted packet claim without verifying)
- **"84+36=120 tests"** → not independently verified

### Trace Verification (5/5 execution-verified)

| Trace | Edge Case | Execution Result |
|-------|-----------|-----------------|
| GuardRunner._check_critical_surfaces | Renamed `helpers.py` (no auth path), empty patch | Path: [], Semantic: [] — **CONFIRMED** (trace fixed: was misleading) |
| validate_canonical | `sod_mode='S3'` | BLOCK CLS-003 immediately — **CONFIRMED** (trace fixed: was factually wrong) |
| GuardResult.finalize | WARN-only findings | `overall_result=PASS` — **CONFIRMED** |
| GitHubAPI._request_bytes | 429 HTTPError | `GitHubAPIError(status_code=429)`, no retry — **CONFIRMED** |
| validate_class_a_manifest | `test_results: {pass:0, fail:0, skip:0}` | `errors=[]`, validation passes — **CONFIRMED** |

### Trace Corrections Applied

1. **Trace 1 (critical surfaces):** Original said "would miss the file" without
   specifying that path patterns still catch files with auth keywords in the path.
   Fixed to show both path AND semantic checks explicitly, with note that
   `src/auth/login.py` would still be caught by path patterns.

2. **Trace 2 (sod_mode):** Original claimed S3 "passes silently for R0/R1".
   Execution proved code has `sod_mode not in ("S0", "S1")` check that catches
   S3 BEFORE the R2+ check. Fixed with `AUDIT CORRECTION` note.

### Findings Confirmed

- `node`/`npm` hardcoded in manifest.py → **REAL**
- Zero-test acceptance (`_is_int(0)` passes) → **REAL**
- Branch list inconsistency → **REAL**

---

## Lessons for Future AI First-Pass

1. **Execute every edge case.** Mental traces without execution verification caught
   only 87% accuracy. Execution verification caught 100%. The sod_mode error would
   have misled a human reviewer if not caught by running the code.
2. **Don't hallucinate functions.** If a claim says "guard sanitization", predict
   the mechanism, don't invent specific function names.
3. **Don't parrot packet claims.** Verify counts independently (file count, line
   count, test count) during the trace phase.
4. **Line numbers are fragile.** `StateTransition.line_number` was removed from the
   model. Variable name + before/after values tell the story without brittle refs.
5. **Mark unverifiable traces.** PR#2 JS traces cannot be executed from Python.
   They should be explicitly marked as "code-read only" until a JS test harness
   or live CI run confirms them.
6. **Probe findings were 100% real.** The adversarial probe phase produced the
   highest-value output — every flagged issue is a genuine code concern.
