# AIV Evidence File (v1.0)

**File:** `tests/unit/test_language_drivers.py`
**Commit:** `9b70f61`
**Generated:** 2026-02-10T20:51:09Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "tests/unit/test_language_drivers.py"
  classification_rationale: "R1: test suite for new feature"
  classified_by: "Miguel Ingram"
  classified_at: "2026-02-10T20:51:09Z"
```

## Claim(s)

1. Tests cover: registry discovery, PythonDriver delegation, TreeSitterDriver symbol resolution (JS/TS functions, arrow functions, classes, methods, TSX), test graph building, and downstream caller analysis
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/aiv-protocol/blob/9b70f61b61f184fb6ade604b735bb3005f9c037f/docs/EXTERNAL_READINESS_AUDIT.md](https://github.com/ImmortalDemonGod/aiv-protocol/blob/9b70f61b61f184fb6ade604b735bb3005f9c037f/docs/EXTERNAL_READINESS_AUDIT.md)
- **Requirements Verified:** P1-6/7/8: all polyglot capabilities must have test coverage

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`9b70f61`](https://github.com/ImmortalDemonGod/aiv-protocol/tree/9b70f61b61f184fb6ade604b735bb3005f9c037f))

- [`tests/unit/test_language_drivers.py#L1-L351`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/9b70f61b61f184fb6ade604b735bb3005f9c037f/tests/unit/test_language_drivers.py#L1-L351)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`TestRegistry`** (L1-L351): FAIL -- WARNING: No tests import or call `TestRegistry`
- **`TestPythonDriver`** (unknown): FAIL -- WARNING: No tests import or call `TestPythonDriver`
- **`TestTreeSitterDriverProtocol`** (unknown): FAIL -- WARNING: No tests import or call `TestTreeSitterDriverProtocol`
- **`TestTreeSitterSymbolResolution`** (unknown): FAIL -- WARNING: No tests import or call `TestTreeSitterSymbolResolution`
- **`TestTreeSitterTestGraph`** (unknown): FAIL -- WARNING: No tests import or call `TestTreeSitterTestGraph`
- **`TestTreeSitterDownstreamCallers`** (unknown): FAIL -- WARNING: No tests import or call `TestTreeSitterDownstreamCallers`
- **`TestRegistry.test_python_always_registered`** (unknown): FAIL -- WARNING: No tests import or call `test_python_always_registered`
- **`TestRegistry.test_get_driver_for_python`** (unknown): FAIL -- WARNING: No tests import or call `test_get_driver_for_python`
- **`TestRegistry.test_get_driver_for_unknown_extension`** (unknown): FAIL -- WARNING: No tests import or call `test_get_driver_for_unknown_extension`
- **`TestRegistry.test_get_driver_for_nonexistent_file`** (unknown): FAIL -- WARNING: No tests import or call `test_get_driver_for_nonexistent_file`
- **`TestPythonDriver.test_conforms_to_protocol`** (unknown): FAIL -- WARNING: No tests import or call `test_conforms_to_protocol`
- **`TestPythonDriver.test_name`** (unknown): FAIL -- WARNING: No tests import or call `test_name`
- **`TestPythonDriver.test_extensions`** (unknown): FAIL -- WARNING: No tests import or call `test_extensions`
- **`TestPythonDriver.test_resolve_symbols_delegates`** (unknown): FAIL -- WARNING: No tests import or call `test_resolve_symbols_delegates`
- **`TestPythonDriver.test_build_test_graph_delegates`** (unknown): FAIL -- WARNING: No tests import or call `test_build_test_graph_delegates`
- **`TestPythonDriver.test_find_downstream_callers_delegates`** (unknown): FAIL -- WARNING: No tests import or call `test_find_downstream_callers_delegates`
- **`TestTreeSitterDriverProtocol.test_conforms_to_protocol`** (unknown): FAIL -- WARNING: No tests import or call `test_conforms_to_protocol`
- **`TestTreeSitterDriverProtocol.test_name`** (unknown): FAIL -- WARNING: No tests import or call `test_name`
- **`TestTreeSitterDriverProtocol.test_extensions_include_js_ts`** (unknown): FAIL -- WARNING: No tests import or call `test_extensions_include_js_ts`
- **`TestTreeSitterDriverProtocol.test_registered_for_js`** (unknown): FAIL -- WARNING: No tests import or call `test_registered_for_js`
- **`TestTreeSitterDriverProtocol.test_registered_for_ts`** (unknown): FAIL -- WARNING: No tests import or call `test_registered_for_ts`
- **`TestTreeSitterSymbolResolution.test_function_declaration`** (unknown): FAIL -- WARNING: No tests import or call `test_function_declaration`
- **`TestTreeSitterSymbolResolution.test_arrow_function`** (unknown): FAIL -- WARNING: No tests import or call `test_arrow_function`
- **`TestTreeSitterSymbolResolution.test_class_and_methods`** (unknown): FAIL -- WARNING: No tests import or call `test_class_and_methods`
- **`TestTreeSitterSymbolResolution.test_method_only`** (unknown): FAIL -- WARNING: No tests import or call `test_method_only`
- **`TestTreeSitterSymbolResolution.test_module_level_returns_module`** (unknown): FAIL -- WARNING: No tests import or call `test_module_level_returns_module`
- **`TestTreeSitterSymbolResolution.test_parse_error_returns_marker`** (unknown): FAIL -- WARNING: No tests import or call `test_parse_error_returns_marker`
- **`TestTreeSitterSymbolResolution.test_typescript_file`** (unknown): FAIL -- WARNING: No tests import or call `test_typescript_file`
- **`TestTreeSitterSymbolResolution.test_tsx_file`** (unknown): FAIL -- WARNING: No tests import or call `test_tsx_file`
- **`TestTreeSitterSymbolResolution.test_multi_symbol_hunk`** (unknown): FAIL -- WARNING: No tests import or call `test_multi_symbol_hunk`
- **`TestTreeSitterTestGraph.test_imports_extracted`** (unknown): FAIL -- WARNING: No tests import or call `test_imports_extracted`
- **`TestTreeSitterTestGraph.test_calls_extracted`** (unknown): FAIL -- WARNING: No tests import or call `test_calls_extracted`
- **`TestTreeSitterTestGraph.test_empty_test_dir`** (unknown): FAIL -- WARNING: No tests import or call `test_empty_test_dir`
- **`TestTreeSitterTestGraph.test_nonexistent_test_dir`** (unknown): FAIL -- WARNING: No tests import or call `test_nonexistent_test_dir`
- **`TestTreeSitterDownstreamCallers.test_finds_caller`** (unknown): FAIL -- WARNING: No tests import or call `test_finds_caller`
- **`TestTreeSitterDownstreamCallers.test_excludes_committed_file`** (unknown): FAIL -- WARNING: No tests import or call `test_excludes_committed_file`
- **`TestTreeSitterDownstreamCallers.test_no_callers_returns_empty`** (unknown): FAIL -- WARNING: No tests import or call `test_no_callers_returns_empty`
- **`TestTreeSitterDownstreamCallers.test_nonexistent_src_dir`** (unknown): FAIL -- WARNING: No tests import or call `test_nonexistent_src_dir`

**Coverage summary:** 0/38 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** 17 error(s)
- **mypy:** Found 17 errors in 1 file (checked 1 source file)

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | Tests cover: registry discovery, PythonDriver delegation, Tr... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 2 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (0/38 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

TestRegistry,TestPythonDriver,TestTreeSitterSymbolResolution,TestTreeSitterTestGraph,TestTreeSitterDownstreamCallers
