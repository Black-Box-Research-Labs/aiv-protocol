# AIV Verification Packet (v2.1)

**Commit:** `9547980`
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R2
  sod_mode: S1
  critical_surfaces: []
  blast_radius: "src/aiv/cli/main.py"
  classification_rationale: "Class E was accepting a URL but emitting generic See linked spec — no verifier can trace that to a real requirement"
  classified_by: "ImmortalDemonGod"
  classified_at: "2026-02-09T01:30:38Z"
```

## Claim(s)

1. aiv commit requires --requirement flag specifying which section/requirement the intent URL satisfies
2. Class E evidence now includes the user-provided requirement text instead of generic See linked spec
3. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/aiv-protocol/blob/80014cd/SPECIFICATION.md](https://github.com/ImmortalDemonGod/aiv-protocol/blob/80014cd/SPECIFICATION.md)
- **Requirements Verified:** SPECIFICATION.md Class E Intent Alignment: evidence must reference a specific requirement, not just link to a document

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`9547980`](https://github.com/ImmortalDemonGod/aiv-protocol/tree/95479805a27cf80417fc6fad810420cef36ac2cc))

- [`src/aiv/cli/main.py#L730-L732`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/95479805a27cf80417fc6fad810420cef36ac2cc/src/aiv/cli/main.py#L730-L732)
- [`src/aiv/cli/main.py#L779-L780`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/95479805a27cf80417fc6fad810420cef36ac2cc/src/aiv/cli/main.py#L779-L780)
- [`src/aiv/cli/main.py#L841`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/95479805a27cf80417fc6fad810420cef36ac2cc/src/aiv/cli/main.py#L841)

### Class A (Execution Evidence)

- **pytest:** 528 passed, 0 failed in 35.04s
- **Tests covering changed file** (119):
  - `tests/conftest.py::test_process_payment_success`
  - `tests/conftest.py::test_login`
  - `tests/conftest.py::test_refresh_token`
  - `tests/conftest.py::test_charge`
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
- **ruff:** All checks passed
- **mypy:** Success: no issues found in 1 source file

### Class C (Negative Evidence)

**Search methodology:** Ran `git diff --cached` and scanned for regression indicators.

- Test file deletions: **none**
- Test file modifications: **none**
- Deleted assertions (`assert` removals in diff): **none found**
- Added skip markers (`@pytest.mark.skip`, `@unittest.skip`): **none found**

### Class F (Provenance Evidence)

- No test files deleted. No assertions removed. Full test suite passes.

---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence was collected by `aiv commit` running: git diff, pytest -v, ruff, mypy, anti-cheat scan.

---

## Summary

aiv commit --requirement forces specific section/requirement text into Class E evidence
