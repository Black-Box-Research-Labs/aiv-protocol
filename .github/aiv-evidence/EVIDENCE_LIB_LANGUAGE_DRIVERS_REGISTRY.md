# AIV Evidence File (v1.0)

**File:** `src/aiv/lib/language_drivers/registry.py`
**Commit:** `b89f53f`
**Generated:** 2026-02-10T20:49:40Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "src/aiv/lib/language_drivers/registry.py"
  classification_rationale: "R1: registry pattern"
  classified_by: "Miguel Ingram"
  classified_at: "2026-02-10T20:49:40Z"
```

## Claim(s)

1. Maps file extensions to LanguageDriver instances. PythonDriver always registered. TreeSitterDriver registered lazily when tree-sitter packages available.
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/aiv-protocol/blob/b89f53f804bf05847c48bfba4c859df90f44357a/docs/EXTERNAL_READINESS_AUDIT.md](https://github.com/ImmortalDemonGod/aiv-protocol/blob/b89f53f804bf05847c48bfba4c859df90f44357a/docs/EXTERNAL_READINESS_AUDIT.md)
- **Requirements Verified:** P1-6: driver dispatch by file extension

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`b89f53f`](https://github.com/ImmortalDemonGod/aiv-protocol/tree/b89f53f804bf05847c48bfba4c859df90f44357a))

- [`src/aiv/lib/language_drivers/registry.py#L1-L63`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/b89f53f804bf05847c48bfba4c859df90f44357a/src/aiv/lib/language_drivers/registry.py#L1-L63)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`register_driver`** (L1-L63): FAIL -- WARNING: No tests import or call `register_driver`
- **`get_driver`** (unknown): PASS -- 5 test(s) call `get_driver` directly
  - `tests/unit/test_language_drivers.py::test_get_driver_for_python`
  - `tests/unit/test_language_drivers.py::test_get_driver_for_unknown_extension`
  - `tests/unit/test_language_drivers.py::test_get_driver_for_nonexistent_file`
  - `tests/unit/test_language_drivers.py::test_registered_for_js`
  - `tests/unit/test_language_drivers.py::test_registered_for_ts`
- **`registered_extensions`** (unknown): PASS -- 1 test(s) call `registered_extensions` directly
  - `tests/unit/test_language_drivers.py::test_python_always_registered`
- **`_bootstrap`** (unknown): FAIL -- WARNING: No tests import or call `_bootstrap`

**Coverage summary:** 2/4 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** All checks passed
- **mypy:** Success: no issues found in 1 source file

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | Maps file extensions to LanguageDriver instances. PythonDriv... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 2 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (2/4 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

get_driver,register_driver,registered_extensions,_bootstrap
