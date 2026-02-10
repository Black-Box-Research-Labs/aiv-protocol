# AIV Evidence File (v1.0)

**File:** `src/aiv/lib/language_drivers/protocol.py`
**Commit:** `0ddfb5f`
**Generated:** 2026-02-10T20:48:43Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "src/aiv/lib/language_drivers/protocol.py"
  classification_rationale: "R1: new protocol definition"
  classified_by: "Miguel Ingram"
  classified_at: "2026-02-10T20:48:43Z"
```

## Claim(s)

1. Protocol with resolve_symbols, build_test_graph, find_downstream_callers methods. Runtime-checkable for isinstance validation.
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/aiv-protocol/blob/0ddfb5f27d48783fee7561b1b6a5a3720fd12096/docs/EXTERNAL_READINESS_AUDIT.md](https://github.com/ImmortalDemonGod/aiv-protocol/blob/0ddfb5f27d48783fee7561b1b6a5a3720fd12096/docs/EXTERNAL_READINESS_AUDIT.md)
- **Requirements Verified:** P1-6: LanguageDriver interface

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`0ddfb5f`](https://github.com/ImmortalDemonGod/aiv-protocol/tree/0ddfb5f27d48783fee7561b1b6a5a3720fd12096))

- [`src/aiv/lib/language_drivers/protocol.py#L1-L87`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/0ddfb5f27d48783fee7561b1b6a5a3720fd12096/src/aiv/lib/language_drivers/protocol.py#L1-L87)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`LanguageDriver`** (L1-L87): FAIL -- WARNING: 1 file(s) import `LanguageDriver` but 0 tests call it directly
  - Imported by: `tests/unit/test_language_drivers.py`
- **`LanguageDriver.name`** (unknown): FAIL -- WARNING: No tests import or call `name`
- **`LanguageDriver.extensions`** (unknown): FAIL -- WARNING: No tests import or call `extensions`
- **`LanguageDriver.resolve_symbols`** (unknown): PASS -- 10 test(s) call `resolve_symbols` directly
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
- **`LanguageDriver.build_test_graph`** (unknown): PASS -- 15 test(s) call `build_test_graph` directly
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
- **`LanguageDriver.find_downstream_callers`** (unknown): PASS -- 8 test(s) call `find_downstream_callers` directly
  - `tests/unit/test_language_drivers.py::test_find_downstream_callers_delegates`
  - `tests/unit/test_language_drivers.py::test_finds_caller`
  - `tests/unit/test_language_drivers.py::test_excludes_committed_file`
  - `tests/unit/test_language_drivers.py::test_no_callers_returns_empty`
  - `tests/unit/test_language_drivers.py::test_nonexistent_src_dir`
  - `tests/unit/test_evidence_collector.py::test_finds_caller_in_src`
  - `tests/unit/test_evidence_collector.py::test_excludes_committed_file`
  - `tests/unit/test_evidence_collector.py::test_no_callers_returns_empty`

**Coverage summary:** 3/6 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** All checks passed
- **mypy:** Success: no issues found in 1 source file

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | Protocol with resolve_symbols, build_test_graph, find_downst... | symbol | 33 test(s) call `LanguageDriver.find_downstream_callers`, `LanguageDriver.build_test_graph`, `LanguageDriver.resolve_symbols` | PASS VERIFIED |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 1 verified, 0 unverified, 1 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (3/6 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

LanguageDriver
