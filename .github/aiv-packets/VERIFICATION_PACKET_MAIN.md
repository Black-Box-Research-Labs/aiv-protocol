# AIV Verification Packet (v2.1)

**Commit:** `e6ae981`
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R2
  sod_mode: S1
  critical_surfaces: []
  blast_radius: "src/aiv/cli/main.py"
  classification_rationale: "CLI rewire: aiv commit now uses evidence_collector module instead of string templates"
  classified_by: "ImmortalDemonGod"
  classified_at: "2026-02-09T01:16:46Z"
```

## Claim(s)

1. aiv commit collects Class B from git diff line ranges as SHA-pinned permalinks
2. aiv commit collects Class A by running pytest and extracting test names covering the changed file
3. aiv commit collects Class C by scanning the diff for deleted assertions and skip markers
4. aiv commit collects Class F by scanning test file integrity from git diff
5. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/aiv-protocol/blob/cf3639c/SPECIFICATION.md](https://github.com/ImmortalDemonGod/aiv-protocol/blob/cf3639c/SPECIFICATION.md)
- **Requirements Verified:** See linked spec/issue.

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`e6ae981`](https://github.com/ImmortalDemonGod/aiv-protocol/tree/e6ae981d3984ec43417e2a669ea984dcc1a45256))

- [`src/aiv/cli/main.py#L736`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/e6ae981d3984ec43417e2a669ea984dcc1a45256/src/aiv/cli/main.py#L736)
- [`src/aiv/cli/main.py#L738-L741`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/e6ae981d3984ec43417e2a669ea984dcc1a45256/src/aiv/cli/main.py#L738-L741)
- [`src/aiv/cli/main.py#L753-L759`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/e6ae981d3984ec43417e2a669ea984dcc1a45256/src/aiv/cli/main.py#L753-L759)
- [`src/aiv/cli/main.py#L766`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/e6ae981d3984ec43417e2a669ea984dcc1a45256/src/aiv/cli/main.py#L766)
- [`src/aiv/cli/main.py#L778`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/e6ae981d3984ec43417e2a669ea984dcc1a45256/src/aiv/cli/main.py#L778)
- [`src/aiv/cli/main.py#L781`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/e6ae981d3984ec43417e2a669ea984dcc1a45256/src/aiv/cli/main.py#L781)
- [`src/aiv/cli/main.py#L808`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/e6ae981d3984ec43417e2a669ea984dcc1a45256/src/aiv/cli/main.py#L808)
- [`src/aiv/cli/main.py#L829`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/e6ae981d3984ec43417e2a669ea984dcc1a45256/src/aiv/cli/main.py#L829)
- [`src/aiv/cli/main.py#L832-L833`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/e6ae981d3984ec43417e2a669ea984dcc1a45256/src/aiv/cli/main.py#L832-L833)
- [`src/aiv/cli/main.py#L838-L842`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/e6ae981d3984ec43417e2a669ea984dcc1a45256/src/aiv/cli/main.py#L838-L842)
- [`src/aiv/cli/main.py#L844-L854`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/e6ae981d3984ec43417e2a669ea984dcc1a45256/src/aiv/cli/main.py#L844-L854)
- [`src/aiv/cli/main.py#L856`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/e6ae981d3984ec43417e2a669ea984dcc1a45256/src/aiv/cli/main.py#L856)
- [`src/aiv/cli/main.py#L860-L861`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/e6ae981d3984ec43417e2a669ea984dcc1a45256/src/aiv/cli/main.py#L860-L861)
- [`src/aiv/cli/main.py#L863-L875`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/e6ae981d3984ec43417e2a669ea984dcc1a45256/src/aiv/cli/main.py#L863-L875)
- [`src/aiv/cli/main.py#L877-L878`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/e6ae981d3984ec43417e2a669ea984dcc1a45256/src/aiv/cli/main.py#L877-L878)
- [`src/aiv/cli/main.py#L880`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/e6ae981d3984ec43417e2a669ea984dcc1a45256/src/aiv/cli/main.py#L880)
- [`src/aiv/cli/main.py#L882`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/e6ae981d3984ec43417e2a669ea984dcc1a45256/src/aiv/cli/main.py#L882)
- [`src/aiv/cli/main.py#L884-L885`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/e6ae981d3984ec43417e2a669ea984dcc1a45256/src/aiv/cli/main.py#L884-L885)
- [`src/aiv/cli/main.py#L887-L898`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/e6ae981d3984ec43417e2a669ea984dcc1a45256/src/aiv/cli/main.py#L887-L898)
- [`src/aiv/cli/main.py#L937`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/e6ae981d3984ec43417e2a669ea984dcc1a45256/src/aiv/cli/main.py#L937)

### Class A (Execution Evidence)

- **pytest:** 503 passed, 0 failed in 36.43s
- **Tests covering changed file** (134):
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

aiv commit rewired from template generation to tool-based evidence collection
