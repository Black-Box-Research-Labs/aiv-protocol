# AIV Evidence File (v1.0)

**File:** `src/aiv/lib/evidence_collector.py`
**Commit:** `2b42705`
**Previous:** `d5ede86`
**Generated:** 2026-02-09T19:30:48Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "src/aiv/lib/evidence_collector.py"
  classification_rationale: "AST binding fix eliminates false negatives that caused all --force usage"
  classified_by: "ImmortalDemonGod"
  classified_at: "2026-02-09T19:30:48Z"
```

## Claim(s)

1. _CallVisitor detects subprocess.run calls containing aiv CLI commands and maps them to function names
2. build_test_graph resolves one level of helper indirection so test_foo calling _run_aiv_commit propagates commit_cmd
3. find_covering_tests matches subprocess-detected CLI calls even when test file does not import the symbol
4. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/aiv-protocol/blob/2b42705a903b8e7b3f31c03f37c1a4c987b949bd/docs/CLAIM_AWARE_EVIDENCE_PLAN.md](https://github.com/ImmortalDemonGod/aiv-protocol/blob/2b42705a903b8e7b3f31c03f37c1a4c987b949bd/docs/CLAIM_AWARE_EVIDENCE_PLAN.md)
- **Requirements Verified:** Theater Gap 2: false UNVERIFIED verdicts on CLI entry points cause forced bypasses

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`2b42705`](https://github.com/ImmortalDemonGod/aiv-protocol/tree/2b42705a903b8e7b3f31c03f37c1a4c987b949bd))

- [`src/aiv/lib/evidence_collector.py#L676-L689`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/2b42705a903b8e7b3f31c03f37c1a4c987b949bd/src/aiv/lib/evidence_collector.py#L676-L689)
- [`src/aiv/lib/evidence_collector.py#L691-L696`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/2b42705a903b8e7b3f31c03f37c1a4c987b949bd/src/aiv/lib/evidence_collector.py#L691-L696)
- [`src/aiv/lib/evidence_collector.py#L706-L708`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/2b42705a903b8e7b3f31c03f37c1a4c987b949bd/src/aiv/lib/evidence_collector.py#L706-L708)
- [`src/aiv/lib/evidence_collector.py#L711-L728`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/2b42705a903b8e7b3f31c03f37c1a4c987b949bd/src/aiv/lib/evidence_collector.py#L711-L728)
- [`src/aiv/lib/evidence_collector.py#L761-L762`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/2b42705a903b8e7b3f31c03f37c1a4c987b949bd/src/aiv/lib/evidence_collector.py#L761-L762)
- [`src/aiv/lib/evidence_collector.py#L765-L779`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/2b42705a903b8e7b3f31c03f37c1a4c987b949bd/src/aiv/lib/evidence_collector.py#L765-L779)
- [`src/aiv/lib/evidence_collector.py#L826-L827`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/2b42705a903b8e7b3f31c03f37c1a4c987b949bd/src/aiv/lib/evidence_collector.py#L826-L827)
- [`src/aiv/lib/evidence_collector.py#L836-L843`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/2b42705a903b8e7b3f31c03f37c1a4c987b949bd/src/aiv/lib/evidence_collector.py#L836-L843)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`_CallVisitor`** (L676-L689): FAIL -- WARNING: No tests import or call `_CallVisitor`
- **`_CallVisitor.visit_Call`** (L691-L696): FAIL -- WARNING: No tests import or call `visit_Call`
- **`_CallVisitor._extract_cli_command`** (L706-L708): FAIL -- WARNING: No tests import or call `_extract_cli_command`
- **`build_test_graph`** (L711-L728): PASS -- 10 test(s) call `build_test_graph` directly
  - `tests/unit/test_evidence_collector.py::test_builds_import_map`
  - `tests/unit/test_evidence_collector.py::test_builds_call_map`
  - `tests/unit/test_evidence_collector.py::test_empty_dir`
  - `tests/unit/test_evidence_collector.py::test_nonexistent_dir`
  - `tests/unit/test_evidence_collector.py::test_finds_direct_caller`
  - `tests/unit/test_evidence_collector.py::test_import_without_call_warns`
  - `tests/unit/test_evidence_collector.py::test_no_import_warns`
  - `tests/unit/test_evidence_collector.py::test_subprocess_cli_test_detected`
  - `tests/unit/test_evidence_collector.py::test_subprocess_cli_via_helper_detected`
  - `tests/unit/test_evidence_collector.py::test_retro_xdist_bug`
- **`find_covering_tests`** (L761-L762): PASS -- 6 test(s) call `find_covering_tests` directly
  - `tests/unit/test_evidence_collector.py::test_finds_direct_caller`
  - `tests/unit/test_evidence_collector.py::test_import_without_call_warns`
  - `tests/unit/test_evidence_collector.py::test_no_import_warns`
  - `tests/unit/test_evidence_collector.py::test_subprocess_cli_test_detected`
  - `tests/unit/test_evidence_collector.py::test_subprocess_cli_via_helper_detected`
  - `tests/unit/test_evidence_collector.py::test_retro_xdist_bug`

**Coverage summary:** 2/5 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** All checks passed
- **mypy:** Success: no issues found in 1 source file

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | _CallVisitor detects subprocess.run calls containing aiv CLI... | symbol | 0 tests call `_CallVisitor` | FAIL UNVERIFIED |
| 2 | build_test_graph resolves one level of helper indirection so... | symbol | 10 test(s) call `build_test_graph` | PASS VERIFIED |
| 3 | find_covering_tests matches subprocess-detected CLI calls ev... | symbol | 6 test(s) call `find_covering_tests` | PASS VERIFIED |
| 4 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 2 verified, 1 unverified, 1 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (2/5 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

AST now detects subprocess-based CLI tests through helper indirection
