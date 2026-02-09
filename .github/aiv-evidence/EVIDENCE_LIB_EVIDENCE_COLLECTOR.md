# AIV Evidence File (v1.0)

**File:** `src/aiv/lib/evidence_collector.py`
**Commit:** `b4fd49d`
**Previous:** `b4fd49d`
**Generated:** 2026-02-09T19:36:20Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "src/aiv/lib/evidence_collector.py"
  classification_rationale: "AST binding fix eliminates false negatives that caused all force usage"
  classified_by: "ImmortalDemonGod"
  classified_at: "2026-02-09T19:36:20Z"
```

## Claim(s)

1. _CallVisitor.visit_List scans all list literals in function bodies for aiv CLI command patterns
2. build_test_graph resolves one level of helper indirection for subprocess-detected CLI commands
3. find_covering_tests matches subprocess-detected CLI calls even without direct imports
4. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/aiv-protocol/blob/b4fd49da563beaad8c374ddf6da984562163ae17/docs/CLAIM_AWARE_EVIDENCE_PLAN.md](https://github.com/ImmortalDemonGod/aiv-protocol/blob/b4fd49da563beaad8c374ddf6da984562163ae17/docs/CLAIM_AWARE_EVIDENCE_PLAN.md)
- **Requirements Verified:** Theater Gap 2: false UNVERIFIED verdicts on CLI entry points must be eliminated

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`b4fd49d`](https://github.com/ImmortalDemonGod/aiv-protocol/tree/b4fd49da563beaad8c374ddf6da984562163ae17))

- [`src/aiv/lib/evidence_collector.py#L695-L697`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/b4fd49da563beaad8c374ddf6da984562163ae17/src/aiv/lib/evidence_collector.py#L695-L697)
- [`src/aiv/lib/evidence_collector.py#L711`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/b4fd49da563beaad8c374ddf6da984562163ae17/src/aiv/lib/evidence_collector.py#L711)
- [`src/aiv/lib/evidence_collector.py#L714-L720`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/b4fd49da563beaad8c374ddf6da984562163ae17/src/aiv/lib/evidence_collector.py#L714-L720)
- [`src/aiv/lib/evidence_collector.py#L727`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/b4fd49da563beaad8c374ddf6da984562163ae17/src/aiv/lib/evidence_collector.py#L727)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`_CallVisitor`** (L695-L697): PASS -- 3 test(s) call `_CallVisitor` directly
  - `tests/unit/test_evidence_collector.py::test_detects_direct_subprocess_run`
  - `tests/unit/test_evidence_collector.py::test_detects_list_literal_variable`
  - `tests/unit/test_evidence_collector.py::test_unknown_command_ignored`
- **`_CallVisitor.visit_Call`** (L711): FAIL -- WARNING: No tests import or call `visit_Call`
- **`_CallVisitor.visit_List`** (L714-L720): FAIL -- WARNING: No tests import or call `visit_List`
- **`_CallVisitor._extract_cli_from_list`** (L727): FAIL -- WARNING: No tests import or call `_extract_cli_from_list`

**Coverage summary:** 1/4 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** All checks passed
- **mypy:** Success: no issues found in 1 source file

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | _CallVisitor.visit_List scans all list literals in function ... | symbol | 3 test(s) call `_CallVisitor.visit_List`, `_CallVisitor` | PASS VERIFIED |
| 2 | build_test_graph resolves one level of helper indirection fo... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 3 | find_covering_tests matches subprocess-detected CLI calls ev... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 4 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 1 verified, 0 unverified, 3 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (1/4 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

AST detects subprocess CLI tests through list scanning and helper indirection
