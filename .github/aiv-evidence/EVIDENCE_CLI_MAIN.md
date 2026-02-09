# AIV Evidence File (v1.0)

**File:** `src/aiv/cli/main.py`
**Commit:** `5bc211c`
**Previous:** `24cd26a`
**Generated:** 2026-02-09T09:07:51Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "src/aiv/cli/main.py"
  classification_rationale: "User-facing CLI bug fixes from smoke test"
  classified_by: "ImmortalDemonGod"
  classified_at: "2026-02-09T09:07:51Z"
```

## Claim(s)

1. aiv abandon accepts --yes/-y as alias for --force to skip confirmation in non-interactive mode
2. aiv commit detects unchanged files before evidence collection and exits with clear error
3. Unicode em-dashes replaced with ASCII -- in all console.print output for Windows cp1252 compatibility
4. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/aiv-protocol/blob/5bc211c69bd1ae13708bc7368e7bd9dbf7c1bbec/src/aiv/cli/main.py](https://github.com/ImmortalDemonGod/aiv-protocol/blob/5bc211c69bd1ae13708bc7368e7bd9dbf7c1bbec/src/aiv/cli/main.py)
- **Requirements Verified:** CLI must work in non-interactive mode and on Windows cp1252 consoles

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`5bc211c`](https://github.com/ImmortalDemonGod/aiv-protocol/tree/5bc211c69bd1ae13708bc7368e7bd9dbf7c1bbec))

- [`src/aiv/cli/main.py#L165`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/5bc211c69bd1ae13708bc7368e7bd9dbf7c1bbec/src/aiv/cli/main.py#L165)
- [`src/aiv/cli/main.py#L755`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/5bc211c69bd1ae13708bc7368e7bd9dbf7c1bbec/src/aiv/cli/main.py#L755)
- [`src/aiv/cli/main.py#L767-L768`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/5bc211c69bd1ae13708bc7368e7bd9dbf7c1bbec/src/aiv/cli/main.py#L767-L768)
- [`src/aiv/cli/main.py#L899`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/5bc211c69bd1ae13708bc7368e7bd9dbf7c1bbec/src/aiv/cli/main.py#L899)
- [`src/aiv/cli/main.py#L972`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/5bc211c69bd1ae13708bc7368e7bd9dbf7c1bbec/src/aiv/cli/main.py#L972)
- [`src/aiv/cli/main.py#L1057`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/5bc211c69bd1ae13708bc7368e7bd9dbf7c1bbec/src/aiv/cli/main.py#L1057)
- [`src/aiv/cli/main.py#L1091`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/5bc211c69bd1ae13708bc7368e7bd9dbf7c1bbec/src/aiv/cli/main.py#L1091)
- [`src/aiv/cli/main.py#L1102`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/5bc211c69bd1ae13708bc7368e7bd9dbf7c1bbec/src/aiv/cli/main.py#L1102)
- [`src/aiv/cli/main.py#L1111`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/5bc211c69bd1ae13708bc7368e7bd9dbf7c1bbec/src/aiv/cli/main.py#L1111)
- [`src/aiv/cli/main.py#L1308-L1337`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/5bc211c69bd1ae13708bc7368e7bd9dbf7c1bbec/src/aiv/cli/main.py#L1308-L1337)
- [`src/aiv/cli/main.py#L1427`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/5bc211c69bd1ae13708bc7368e7bd9dbf7c1bbec/src/aiv/cli/main.py#L1427)
- [`src/aiv/cli/main.py#L1435`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/5bc211c69bd1ae13708bc7368e7bd9dbf7c1bbec/src/aiv/cli/main.py#L1435)
- [`src/aiv/cli/main.py#L1472`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/5bc211c69bd1ae13708bc7368e7bd9dbf7c1bbec/src/aiv/cli/main.py#L1472)
- [`src/aiv/cli/main.py#L1519`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/5bc211c69bd1ae13708bc7368e7bd9dbf7c1bbec/src/aiv/cli/main.py#L1519)
- [`src/aiv/cli/main.py#L1560`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/5bc211c69bd1ae13708bc7368e7bd9dbf7c1bbec/src/aiv/cli/main.py#L1560)
- [`src/aiv/cli/main.py#L1571`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/5bc211c69bd1ae13708bc7368e7bd9dbf7c1bbec/src/aiv/cli/main.py#L1571)
- [`src/aiv/cli/main.py#L1675`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/5bc211c69bd1ae13708bc7368e7bd9dbf7c1bbec/src/aiv/cli/main.py#L1675)
- [`src/aiv/cli/main.py#L1683`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/5bc211c69bd1ae13708bc7368e7bd9dbf7c1bbec/src/aiv/cli/main.py#L1683)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`init`** (L165): FAIL — WARNING: No tests import or call `init`
- **`_build_evidence_sections`** (L755): PASS — 7 test(s) call `_build_evidence_sections` directly
  - `tests/integration/test_e2e_compliance.py::test_generate_r3_includes_all_six_sections`
  - `tests/integration/test_e2e_compliance.py::test_generate_r0_omits_non_required_sections`
  - `tests/unit/test_coverage.py::test_r0_has_class_b_and_a`
  - `tests/unit/test_coverage.py::test_r1_adds_class_e`
  - `tests/unit/test_coverage.py::test_r2_adds_class_c_and_f`
  - `tests/unit/test_coverage.py::test_r3_has_all_six_classes`
  - `tests/unit/test_coverage.py::test_scope_lines_embedded`
- **`close`** (L767-L768): FAIL — WARNING: No tests import or call `close`
- **`abandon`** (L899): FAIL — WARNING: No tests import or call `abandon`
- **`commit_cmd`** (L972): FAIL — WARNING: No tests import or call `commit_cmd`

**Coverage summary:** 1/5 symbols verified by tests.
- **ruff:** All checks passed
- **mypy:** Success: no issues found in 1 source file

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | aiv abandon accepts --yes/-y as alias for --force to skip co... | symbol | 0 tests call `abandon` | FAIL UNVERIFIED |
| 2 | aiv commit detects unchanged files before evidence collectio... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 3 | Unicode em-dashes replaced with ASCII -- in all console.prin... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 4 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 1 unverified, 3 manual review.

---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff, pytest (677 passed, 10 failed), ruff (clean), mypy (Success: no issues found in 1 source file), AST symbol-to-test binding (5 symbols).

---

## Summary

Fix abandon prompt, nothing-to-commit guard, and Windows Unicode issues in main CLI
