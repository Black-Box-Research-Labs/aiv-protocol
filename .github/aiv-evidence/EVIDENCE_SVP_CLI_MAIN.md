# AIV Evidence File (v1.0)

**File:** `src/aiv/svp/cli/main.py`
**Commit:** `9448bd5`
**Generated:** 2026-02-09T09:06:49Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "src/aiv/svp/cli/main.py"
  classification_rationale: "User-facing CLI bug fix in SVP commands"
  classified_by: "ImmortalDemonGod"
  classified_at: "2026-02-09T09:06:49Z"
```

## Claim(s)

1. SVP predict catches ValidationError and prints friendly field-level errors instead of raw traceback
2. SVP trace catches ValidationError with same friendly handler
3. SVP probe catches ValidationError with same friendly handler
4. SVP ownership catches ValidationError with same friendly handler
5. Unicode em-dashes replaced with ASCII -- in SVP status output for Windows compatibility
6. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/aiv-protocol/blob/9448bd59cc77ba0195fa3f713e2d3a77bcf30a98/src/aiv/svp/cli/main.py](https://github.com/ImmortalDemonGod/aiv-protocol/blob/9448bd59cc77ba0195fa3f713e2d3a77bcf30a98/src/aiv/svp/cli/main.py)
- **Requirements Verified:** CLI commands must not expose raw tracebacks to users; output must be Windows-compatible

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`9448bd5`](https://github.com/ImmortalDemonGod/aiv-protocol/tree/9448bd59cc77ba0195fa3f713e2d3a77bcf30a98))

- [`src/aiv/svp/cli/main.py#L15`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/9448bd59cc77ba0195fa3f713e2d3a77bcf30a98/src/aiv/svp/cli/main.py#L15)
- [`src/aiv/svp/cli/main.py#L71-L81`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/9448bd59cc77ba0195fa3f713e2d3a77bcf30a98/src/aiv/svp/cli/main.py#L71-L81)
- [`src/aiv/svp/cli/main.py#L106-L110`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/9448bd59cc77ba0195fa3f713e2d3a77bcf30a98/src/aiv/svp/cli/main.py#L106-L110)
- [`src/aiv/svp/cli/main.py#L170-L182`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/9448bd59cc77ba0195fa3f713e2d3a77bcf30a98/src/aiv/svp/cli/main.py#L170-L182)
- [`src/aiv/svp/cli/main.py#L254-L268`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/9448bd59cc77ba0195fa3f713e2d3a77bcf30a98/src/aiv/svp/cli/main.py#L254-L268)
- [`src/aiv/svp/cli/main.py#L383-L403`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/9448bd59cc77ba0195fa3f713e2d3a77bcf30a98/src/aiv/svp/cli/main.py#L383-L403)
- [`src/aiv/svp/cli/main.py#L468-L480`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/9448bd59cc77ba0195fa3f713e2d3a77bcf30a98/src/aiv/svp/cli/main.py#L468-L480)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`_print_validation_errors`** (L15): FAIL — WARNING: No tests import or call `_print_validation_errors`
- **`status`** (L71-L81): FAIL — WARNING: No tests import or call `status`
- **`predict`** (L106-L110): FAIL — WARNING: No tests import or call `predict`
- **`trace`** (L170-L182): FAIL — WARNING: No tests import or call `trace`
- **`probe`** (L254-L268): FAIL — WARNING: No tests import or call `probe`
- **`ownership`** (L383-L403): FAIL — WARNING: No tests import or call `ownership`

**Coverage summary:** 0/6 symbols verified by tests.
- **ruff:** All checks passed
- **mypy:** Success: no issues found in 1 source file

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | SVP predict catches ValidationError and prints friendly fiel... | symbol | 0 tests call `predict`, `trace` | FAIL UNVERIFIED |
| 2 | SVP trace catches ValidationError with same friendly handler | symbol | 0 tests call `trace` | FAIL UNVERIFIED |
| 3 | SVP probe catches ValidationError with same friendly handler | symbol | 0 tests call `probe` | FAIL UNVERIFIED |
| 4 | SVP ownership catches ValidationError with same friendly han... | symbol | 0 tests call `ownership` | FAIL UNVERIFIED |
| 5 | Unicode em-dashes replaced with ASCII -- in SVP status outpu... | symbol | 0 tests call `status` | FAIL UNVERIFIED |
| 6 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 5 unverified, 1 manual review.

---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff, pytest (680 passed, 7 failed), ruff (clean), mypy (Success: no issues found in 1 source file), AST symbol-to-test binding (6 symbols).

---

## Summary

SVP commands now show friendly validation errors instead of raw Pydantic tracebacks
