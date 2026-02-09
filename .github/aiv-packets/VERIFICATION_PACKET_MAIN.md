# AIV Verification Packet (v2.1)

**Commit:** `f81b6e6`
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R2
  sod_mode: S1
  critical_surfaces: []
  blast_radius: "src/aiv/cli/main.py"
  classification_rationale: "Class F was redundant with Class C and A — now shows distinct chain-of-custody provenance"
  classified_by: "ImmortalDemonGod"
  classified_at: "2026-02-09T02:10:20Z"
```

## Claim(s)

1. commit_cmd extracts unique test file paths from Class A relevant_tests and passes them to collect_class_f
2. Class F now shows git log chain-of-custody for the specific test files that cover the changed code
3. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/aiv-protocol/blob/3e48e90/docs/CLAIM_AWARE_EVIDENCE_PLAN.md](https://github.com/ImmortalDemonGod/aiv-protocol/blob/3e48e90/docs/CLAIM_AWARE_EVIDENCE_PLAN.md)
- **Requirements Verified:** CLAIM_AWARE_EVIDENCE_PLAN.md Phase 0: Class F must use git log --follow on covering test files, not restate Class C+A

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`f81b6e6`](https://github.com/ImmortalDemonGod/aiv-protocol/tree/f81b6e629c2e1f2665b0d9f9eb6c5d001a67af99))

- [`src/aiv/cli/main.py#L889`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/f81b6e629c2e1f2665b0d9f9eb6c5d001a67af99/src/aiv/cli/main.py#L889)
- [`src/aiv/cli/main.py#L892-L903`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/f81b6e629c2e1f2665b0d9f9eb6c5d001a67af99/src/aiv/cli/main.py#L892-L903)

### Class A (Execution Evidence)

- **pytest:** 543 passed, 0 failed in 25.07s
- **Tests covering changed file** (73):
  - `tests/integration/test_e2e_compliance.py::test_every_real_packet_passes_lenient`
  - `tests/integration/test_e2e_compliance.py::test_every_real_packet_parses_classification`
  - `tests/integration/test_e2e_compliance.py::test_cli_subprocess_check_passes`
  - `tests/integration/test_e2e_compliance.py::test_cli_subprocess_check_rejects_garbage`
  - `tests/integration/test_e2e_compliance.py::test_todo_only_evidence_section_not_counted`
  - `tests/integration/test_e2e_compliance.py::test_r3_with_empty_sections_fails`
  - `tests/integration/test_e2e_compliance.py::test_r3_with_substantive_sections_passes`
  - `tests/integration/test_e2e_compliance.py::test_r0_scaffold_passes_without_optional`
  - `tests/integration/test_e2e_compliance.py::test_r2_missing_required_class_fails`
  - `tests/integration/test_e2e_compliance.py::test_bugfix_claims_require_class_f`
  - `tests/integration/test_e2e_compliance.py::test_class_a_code_blob_link_warns`
  - `tests/integration/test_e2e_compliance.py::test_class_a_ci_link_no_e020`
  - `tests/integration/test_e2e_compliance.py::test_bugfix_claims_with_class_f_passes`
  - `tests/integration/test_e2e_compliance.py::test_mutable_github_link_blocked`
  - `tests/integration/test_e2e_compliance.py::test_sha_pinned_link_passes`
  - `tests/integration/test_e2e_compliance.py::test_deleted_assertion_in_diff_blocked`
  - `tests/integration/test_e2e_compliance.py::test_added_skip_decorator_blocked`
  - `tests/integration/test_e2e_compliance.py::test_deleted_test_file_blocked`
  - `tests/integration/test_e2e_compliance.py::test_clean_diff_passes`
  - `tests/integration/test_e2e_compliance.py::test_class_f_justification_overrides_anticheat`
- **ruff:** All checks passed
- **mypy:** Success: no issues found in 1 source file

### Class C (Negative Evidence)

**Search methodology:** Ran `git diff --cached` and scanned for regression indicators.

- Test file deletions: **none**
- Test file modifications: **none**
- Deleted assertions (`assert` removals in diff): **none found**
- Added skip markers (`@pytest.mark.skip`, `@unittest.skip`): **none found**

### Class F (Provenance Evidence)

**Test file chain-of-custody:**

| File | Commits | Created By | Last Modified By | Assertions |
|------|---------|------------|------------------|------------|
| `tests/integration/test_e2e_compliance.py` | 6 | ImmortalDemonGod (dca3d1f) | ImmortalDemonGod (ffd62ca) | 94 |
| `tests/unit/test_coverage.py` | 3 | ImmortalDemonGod (2ea606e) | ImmortalDemonGod (90e23b6) | 50 |

**Recent test directory history** (`git log --oneline -5 -- tests/`):

```
f81b6e6 test(lib): 31 tests for AST symbol resolver, test graph, and semantic coverage
9547980 test(auditor): 3 tests for evidence TODO severity escalation â€” the exact bar
2985156 test(lib): 18 tests for evidence collector module
c88bb9c test(hooks): 41 tests for portable pre-commit hook
157ccbb style: fix ruff format, lint, and mypy strict errors for CI
```

---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence was collected by `aiv commit` running: git diff, pytest -v, ruff, mypy, anti-cheat scan.

---

## Summary

Wire collect_class_f to receive covering test file paths from Class A evidence
