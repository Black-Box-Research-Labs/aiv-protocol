# AIV Verification Packet (v2.1)

**Commit:** `977b440`
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "tests/unit/test_evidence_collector.py"
  classification_rationale: "Test coverage for new evidence collector module"
  classified_by: "ImmortalDemonGod"
  classified_at: "2026-02-09T01:21:51Z"
```

## Claim(s)

1. Class B collector tests verify SHA-pinned line-range permalinks are generated from git diff hunks
2. Class A tests verify specific test names are included and WARNING is emitted when no covering tests found
3. Class C tests verify deleted assertions, deleted test files, and skip markers are detected from diff
4. Class F tests verify test file integrity scanning from git diff
5. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/aiv-protocol/blob/977b440/SPECIFICATION.md](https://github.com/ImmortalDemonGod/aiv-protocol/blob/977b440/SPECIFICATION.md)
- **Requirements Verified:** See linked spec/issue.

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`977b440`](https://github.com/ImmortalDemonGod/aiv-protocol/tree/977b4407717bdc3a19d258ed1d1e7e50d7570c17))

- [`tests/unit/test_evidence_collector.py#L1-L302`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/977b4407717bdc3a19d258ed1d1e7e50d7570c17/tests/unit/test_evidence_collector.py#L1-L302)
- [`tests/unit/test_evidence_collector.py#L11-L15`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/977b4407717bdc3a19d258ed1d1e7e50d7570c17/tests/unit/test_evidence_collector.py#L11-L15)
- [`tests/unit/test_evidence_collector.py#L56-L59`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/977b4407717bdc3a19d258ed1d1e7e50d7570c17/tests/unit/test_evidence_collector.py#L56-L59)
- [`tests/unit/test_evidence_collector.py#L6`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/977b4407717bdc3a19d258ed1d1e7e50d7570c17/tests/unit/test_evidence_collector.py#L6)

### Class A (Execution Evidence)

- **pytest:** 523 passed, 0 failed in 35.50s
- **Tests covering changed file** (18):
  - `tests/unit/test_evidence_collector.py::test_to_markdown_includes_sha_pinned_links`
  - `tests/unit/test_evidence_collector.py::test_to_markdown_includes_tree_link`
  - `tests/unit/test_evidence_collector.py::test_collect_parses_diff_hunks`
  - `tests/unit/test_evidence_collector.py::test_collect_single_line_hunk`
  - `tests/unit/test_evidence_collector.py::test_collect_new_file_fallback`
  - `tests/unit/test_evidence_collector.py::test_to_markdown_includes_test_names`
  - `tests/unit/test_evidence_collector.py::test_to_markdown_warns_no_tests`
  - `tests/unit/test_evidence_collector.py::test_to_markdown_ruff_errors`
  - `tests/unit/test_evidence_collector.py::test_to_markdown_clean`
  - `tests/unit/test_evidence_collector.py::test_to_markdown_alerts_on_deletions`
  - `tests/unit/test_evidence_collector.py::test_to_markdown_alerts_on_skip_markers`
  - `tests/unit/test_evidence_collector.py::test_collect_detects_deleted_test_file`
  - `tests/unit/test_evidence_collector.py::test_collect_detects_removed_assertion`
  - `tests/unit/test_evidence_collector.py::test_collect_clean_diff`
  - `tests/unit/test_evidence_collector.py::test_to_markdown_clean`
  - `tests/unit/test_evidence_collector.py::test_to_markdown_alerts`
  - `tests/unit/test_evidence_collector.py::test_collect_detects_deleted_test`
  - `tests/unit/test_evidence_collector.py::test_collect_clean`
- **ruff:** 47 error(s)
- **mypy:** Found 18 errors in 1 file (checked 1 source file)

---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence was collected by `aiv commit` running: git diff, pytest -v, ruff, mypy, anti-cheat scan.

---

## Summary

18 unit tests covering all 4 evidence collectors (Class B, A, C, F)
