# AI First-Pass SVP Audit Scorecard

**Auditor:** cascade-ai-first-pass (self-audit)
**Date:** 2026-02-07
**Sessions audited:** PR#1 (AIV_IMPLEMENTATION), PR#2 (AIV_GUARD), PR#3 (GUARD_REFACTOR)

## Overall Results

| Category | Right | Wrong | Partial | Total | Accuracy |
|----------|-------|-------|---------|-------|----------|
| Predictions | 22 | 8 | 1 | 31 | 74% |
| Line numbers | 40 | 0 | 2 | 42 | 95% |
| Trace content | 14 | 1 | 0 | 15 | 93% |
| Probe findings | 11 | 0 | 0 | 11 | 100% |

## Known Issue: Line Number Fragility

State transitions cite line numbers that are **snapshots at time of trace** and
will rot with any code edit. The `StateTransition.line_number` field should be
treated as informational context, not a stable reference. Future sessions should
prefer anchoring to function/method signatures or code snippets over line numbers.

---

## PR#1: AIV_IMPLEMENTATION (R2, 7 claims)

### Prediction Errors

- **"12 models"** → actual 13 (missed `FrictionScore`)
- **"computed property evidence_classes_present"** → it's a regular field
- **"sanitize_shell_input"** → hallucinated, does not exist
- **"DiffAnalyzer class"** → hallucinated, actual is `AntiCheatScanner`

### Trace Errors

None. All 18 line citations matched actual code.

### Findings Confirmed

- E020 rule_id collision (pipeline.py + evidence.py) → **REAL**
- Parser code block bug (no fenced block detection) → **REAL**

---

## PR#2: AIV_GUARD (R2, 8 claims)

### Prediction Errors

- **"regex for section headers"** → actual uses `packetContent.includes(h)` (substring)
- **"artifact download via direct API call"** → actual is env-var inter-step communication

### Trace Errors

- 2 off-by-one line citations (628→627, 1984→1983)

### Findings Confirmed

- `.py` excluded from `shouldFetchContentAtHead` → **REAL** (line 605)
- Mutable branch list JS≠Python (5 vs 7) → **REAL**
- Substring `includes()` for section detection → **REAL**

---

## PR#3: GUARD_REFACTOR (R2, 5 claims)

### Prediction Errors

- **"5 files"** → actual 7 (missed `__init__.py`, `__main__.py`)
- **"45-line workflow"** → actual 36 lines (parroted packet claim without verifying)
- **"84+36=120 tests"** → not independently verified

### Trace Errors

- **CRITICAL: `validate_canonical` sod_mode trace was factually wrong.**
  Original claimed `sod_mode='S3'` would "pass silently for R0/R1".
  Actual code has `if sod_mode not in ("S0", "S1")` at line ~147 which
  BLOCKS S3 before the R2+ check runs. **Corrected in session JSON.**

### Findings Confirmed

- `node`/`npm` hardcoded in manifest.py → **REAL**
- Zero-test acceptance (`_is_int(0)` passes) → **REAL**
- Branch list inconsistency → **REAL**

---

## Lessons for Future AI First-Pass

1. **Don't hallucinate functions.** If a claim says "guard sanitization", predict
   the mechanism, don't invent specific function names.
2. **Don't parrot packet claims.** Verify counts independently (file count, line
   count, test count) during the trace phase.
3. **Line numbers are fragile.** Prefer function signatures or code snippet
   anchors in state transitions over absolute line numbers.
4. **Self-audit catches real errors.** The sod_mode trace error would have misled
   a human reviewer. Post-hoc verification is essential.
5. **Prediction accuracy (74%) is the weakest phase.** This is expected — black-box
   prediction before reading code is inherently speculative. The value is in
   documenting what was expected vs. actual, not in being right.
6. **Probe findings were 100% real.** The adversarial probe phase produced the
   highest-value output — every flagged issue is a genuine code concern.
