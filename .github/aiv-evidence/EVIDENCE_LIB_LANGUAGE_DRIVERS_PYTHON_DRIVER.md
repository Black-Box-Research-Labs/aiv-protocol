# AIV Evidence File (v1.0)

**File:** `src/aiv/lib/language_drivers/python_driver.py`
**Commit:** `2ed17d3`
**Generated:** 2026-02-10T20:49:12Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "src/aiv/lib/language_drivers/python_driver.py"
  classification_rationale: "R1: delegation wrapper"
  classified_by: "Miguel Ingram"
  classified_at: "2026-02-10T20:49:12Z"
```

## Claim(s)

1. Delegates to resolve_changed_symbols, build_test_graph, find_downstream_callers in evidence_collector.py
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/aiv-protocol/blob/2ed17d3044616ea5ed1c325aca50f77df678e618/docs/EXTERNAL_READINESS_AUDIT.md](https://github.com/ImmortalDemonGod/aiv-protocol/blob/2ed17d3044616ea5ed1c325aca50f77df678e618/docs/EXTERNAL_READINESS_AUDIT.md)
- **Requirements Verified:** P1-6: PythonDriver maintains backward compat while conforming to LanguageDriver protocol

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`2ed17d3`](https://github.com/ImmortalDemonGod/aiv-protocol/tree/2ed17d3044616ea5ed1c325aca50f77df678e618))

- [`src/aiv/lib/language_drivers/python_driver.py#L1-L55`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/2ed17d3044616ea5ed1c325aca50f77df678e618/src/aiv/lib/language_drivers/python_driver.py#L1-L55)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`PythonDriver`** (L1-L55): PASS -- 4 test(s) call `PythonDriver` directly
  - `tests/unit/test_language_drivers.py::test_extensions`
  - `tests/unit/test_language_drivers.py::test_resolve_symbols_delegates`
  - `tests/unit/test_language_drivers.py::test_build_test_graph_delegates`
  - `tests/unit/test_language_drivers.py::test_find_downstream_callers_delegates`
- **`PythonDriver.name`** (unknown): FAIL -- WARNING: No tests import or call `name`
- **`PythonDriver.extensions`** (unknown): FAIL -- WARNING: No tests import or call `extensions`
- **`PythonDriver.resolve_symbols`** (unknown): PASS -- 10 test(s) call `resolve_symbols` directly
  - `tests/unit/test_language_drivers.py::test_resolve_symbols_delegates`
  - `tests/unit/test_language_drivers.py::test_function_declaration`
  - `tests/unit/test_language_drivers.py::test_arrow_function`
  - `tests/unit/test_language_drivers.py::test_class_and_methods`
  - `tests/unit/test_language_drivers.py::test_method_only`
  - `tests/unit/test_language_drivers.py::test_module_level_returns_module`
  - `tests/unit/test_language_drivers.py::test_parse_error_returns_marker`
  - `tests/unit/test_language_drivers.py::test_typescript_file`
  - `tests/unit/test_language_drivers.py::test_tsx_file`
  - `tests/unit/test_language_drivers.py::test_multi_symbol_hunk`
- **`PythonDriver.build_test_graph`** (unknown): PASS -- 15 test(s) call `build_test_graph` directly
  - `tests/unit/test_language_drivers.py::test_build_test_graph_delegates`
  - `tests/unit/test_language_drivers.py::test_imports_extracted`
  - `tests/unit/test_language_drivers.py::test_calls_extracted`
  - `tests/unit/test_language_drivers.py::test_empty_test_dir`
  - `tests/unit/test_language_drivers.py::test_nonexistent_test_dir`
  - `tests/unit/test_evidence_collector.py::test_builds_import_map`
  - `tests/unit/test_evidence_collector.py::test_builds_call_map`
  - `tests/unit/test_evidence_collector.py::test_empty_dir`
  - `tests/unit/test_evidence_collector.py::test_nonexistent_dir`
  - `tests/unit/test_evidence_collector.py::test_finds_direct_caller`
- **`PythonDriver.find_downstream_callers`** (unknown): PASS -- 8 test(s) call `find_downstream_callers` directly
  - `tests/unit/test_language_drivers.py::test_find_downstream_callers_delegates`
  - `tests/unit/test_language_drivers.py::test_finds_caller`
  - `tests/unit/test_language_drivers.py::test_excludes_committed_file`
  - `tests/unit/test_language_drivers.py::test_no_callers_returns_empty`
  - `tests/unit/test_language_drivers.py::test_nonexistent_src_dir`
  - `tests/unit/test_evidence_collector.py::test_finds_caller_in_src`
  - `tests/unit/test_evidence_collector.py::test_excludes_committed_file`
  - `tests/unit/test_evidence_collector.py::test_no_callers_returns_empty`

**Coverage summary:** 4/6 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** All checks passed
- **mypy:** Success: no issues found in 1 source file

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | Delegates to resolve_changed_symbols, build_test_graph, find... | symbol | 23 test(s) call `PythonDriver.find_downstream_callers`, `PythonDriver.build_test_graph` | PASS VERIFIED |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 1 verified, 0 unverified, 1 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (4/6 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

PythonDriver
