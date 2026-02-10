# AIV Evidence File (v1.0)

**File:** `src/aiv/lib/language_drivers/treesitter_driver.py`
**Commit:** `708d8e6`
**Generated:** 2026-02-10T20:50:09Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "src/aiv/lib/language_drivers/treesitter_driver.py"
  classification_rationale: "R1: new language driver"
  classified_by: "Miguel Ingram"
  classified_at: "2026-02-10T20:50:09Z"
```

## Claim(s)

1. P1-6/7/8 core: tree-sitter based analysis for .js/.jsx/.mjs/.ts/.tsx files. Handles function declarations, arrow functions, classes with methods, ES6 imports, require(), and call extraction.
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/aiv-protocol/blob/708d8e6fca1dad899b9ef906987aaa08dd65f123/docs/EXTERNAL_READINESS_AUDIT.md](https://github.com/ImmortalDemonGod/aiv-protocol/blob/708d8e6fca1dad899b9ef906987aaa08dd65f123/docs/EXTERNAL_READINESS_AUDIT.md)
- **Requirements Verified:** P1-6: polyglot symbol resolution, P1-7: polyglot test graph, P1-8: polyglot downstream callers

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`708d8e6`](https://github.com/ImmortalDemonGod/aiv-protocol/tree/708d8e6fca1dad899b9ef906987aaa08dd65f123))

- [`src/aiv/lib/language_drivers/treesitter_driver.py#L1-L468`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/708d8e6fca1dad899b9ef906987aaa08dd65f123/src/aiv/lib/language_drivers/treesitter_driver.py#L1-L468)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`_SymbolSpan`** (L1-L468): FAIL -- WARNING: No tests import or call `_SymbolSpan`
- **`_FileAnalysis`** (unknown): FAIL -- WARNING: No tests import or call `_FileAnalysis`
- **`_try_load_languages`** (unknown): FAIL -- WARNING: No tests import or call `_try_load_languages`
- **`_create_parser`** (unknown): FAIL -- WARNING: No tests import or call `_create_parser`
- **`_extract_name`** (unknown): FAIL -- WARNING: No tests import or call `_extract_name`
- **`_extract_symbols`** (unknown): FAIL -- WARNING: No tests import or call `_extract_symbols`
- **`_walk_for_symbols`** (unknown): FAIL -- WARNING: No tests import or call `_walk_for_symbols`
- **`_extract_imports`** (unknown): FAIL -- WARNING: No tests import or call `_extract_imports`
- **`_walk_for_imports`** (unknown): FAIL -- WARNING: No tests import or call `_walk_for_imports`
- **`_extract_import_clause`** (unknown): FAIL -- WARNING: No tests import or call `_extract_import_clause`
- **`_extract_named_imports`** (unknown): FAIL -- WARNING: No tests import or call `_extract_named_imports`
- **`_extract_object_pattern`** (unknown): FAIL -- WARNING: No tests import or call `_extract_object_pattern`
- **`_extract_calls`** (unknown): FAIL -- WARNING: No tests import or call `_extract_calls`
- **`_walk_for_calls`** (unknown): FAIL -- WARNING: No tests import or call `_walk_for_calls`
- **`_analyze_file`** (unknown): FAIL -- WARNING: No tests import or call `_analyze_file`
- **`_find_node_at_range`** (unknown): FAIL -- WARNING: No tests import or call `_find_node_at_range`
- **`TreeSitterDriver`** (unknown): PASS -- 20 test(s) call `TreeSitterDriver` directly
  - `tests/unit/test_language_drivers.py::test_conforms_to_protocol`
  - `tests/unit/test_language_drivers.py::test_name`
  - `tests/unit/test_language_drivers.py::test_extensions_include_js_ts`
  - `tests/unit/test_language_drivers.py::test_function_declaration`
  - `tests/unit/test_language_drivers.py::test_arrow_function`
  - `tests/unit/test_language_drivers.py::test_class_and_methods`
  - `tests/unit/test_language_drivers.py::test_method_only`
  - `tests/unit/test_language_drivers.py::test_module_level_returns_module`
  - `tests/unit/test_language_drivers.py::test_parse_error_returns_marker`
  - `tests/unit/test_language_drivers.py::test_typescript_file`
- **`_SymbolSpan.qualified_name`** (unknown): FAIL -- WARNING: No tests import or call `qualified_name`
- **`TreeSitterDriver.__init__`** (unknown): FAIL -- WARNING: No tests import or call `__init__`
- **`TreeSitterDriver.available`** (unknown): FAIL -- WARNING: No tests import or call `available`
- **`TreeSitterDriver.name`** (unknown): FAIL -- WARNING: No tests import or call `name`
- **`TreeSitterDriver.extensions`** (unknown): FAIL -- WARNING: No tests import or call `extensions`
- **`TreeSitterDriver._get_parser`** (unknown): FAIL -- WARNING: No tests import or call `_get_parser`
- **`TreeSitterDriver._parse_file`** (unknown): FAIL -- WARNING: No tests import or call `_parse_file`
- **`TreeSitterDriver.resolve_symbols`** (unknown): PASS -- 10 test(s) call `resolve_symbols` directly
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
- **`TreeSitterDriver.build_test_graph`** (unknown): PASS -- 15 test(s) call `build_test_graph` directly
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
- **`TreeSitterDriver.find_downstream_callers`** (unknown): PASS -- 8 test(s) call `find_downstream_callers` directly
  - `tests/unit/test_language_drivers.py::test_find_downstream_callers_delegates`
  - `tests/unit/test_language_drivers.py::test_finds_caller`
  - `tests/unit/test_language_drivers.py::test_excludes_committed_file`
  - `tests/unit/test_language_drivers.py::test_no_callers_returns_empty`
  - `tests/unit/test_language_drivers.py::test_nonexistent_src_dir`
  - `tests/unit/test_evidence_collector.py::test_finds_caller_in_src`
  - `tests/unit/test_evidence_collector.py::test_excludes_committed_file`
  - `tests/unit/test_evidence_collector.py::test_no_callers_returns_empty`
- **`TreeSitterDriver._is_test_function`** (unknown): FAIL -- WARNING: No tests import or call `_is_test_function`

**Coverage summary:** 4/28 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** All checks passed
- **mypy:** Success: no issues found in 1 source file

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | P1-6/7/8 core: tree-sitter based analysis for .js/.jsx/.mjs/... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 2 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (4/28 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

TreeSitterDriver,_extract_symbols,_extract_imports,_extract_calls
