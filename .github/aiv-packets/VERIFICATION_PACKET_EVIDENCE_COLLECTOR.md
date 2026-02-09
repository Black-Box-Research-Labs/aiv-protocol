# AIV Verification Packet (v2.1)

**Commit:** `3e48e90`
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R3
  sod_mode: S1
  critical_surfaces: []
  blast_radius: "src/aiv/lib/evidence_collector.py"
  classification_rationale: "R3: this module gates all verification quality — AST analysis eliminates the last forms of evidence theater"
  classified_by: "ImmortalDemonGod"
  classified_at: "2026-02-09T02:08:36Z"
```

## Claim(s)

1. resolve_changed_symbols maps diff line ranges to enclosing Python functions/classes via ast.parse
2. build_test_graph parses all test files to build import map and call graph using ast.NodeVisitor
3. find_covering_tests deterministically maps changed symbols to tests that import AND call them — no keywords, no grep
4. Class F rewritten: git log chain-of-custody per covering test file replaces redundant Class C+A restatement
5. Retro-test proves xdist import error would be caught: 0 tests call collect_class_a directly so WARNING is emitted
6. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/aiv-protocol/blob/3e48e90/docs/CLAIM_AWARE_EVIDENCE_PLAN.md](https://github.com/ImmortalDemonGod/aiv-protocol/blob/3e48e90/docs/CLAIM_AWARE_EVIDENCE_PLAN.md)
- **Requirements Verified:** CLAIM_AWARE_EVIDENCE_PLAN.md V2: keyword matching REJECTED; AST analysis required for deterministic claim-to-test mapping

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`3e48e90`](https://github.com/ImmortalDemonGod/aiv-protocol/tree/3e48e9001e9cb2a6d318ae17fc1dbed350fb7946))

- [`src/aiv/lib/evidence_collector.py#L13`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/3e48e9001e9cb2a6d318ae17fc1dbed350fb7946/src/aiv/lib/evidence_collector.py#L13)
- [`src/aiv/lib/evidence_collector.py#L16`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/3e48e9001e9cb2a6d318ae17fc1dbed350fb7946/src/aiv/lib/evidence_collector.py#L16)
- [`src/aiv/lib/evidence_collector.py#L133-L145`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/3e48e9001e9cb2a6d318ae17fc1dbed350fb7946/src/aiv/lib/evidence_collector.py#L133-L145)
- [`src/aiv/lib/evidence_collector.py#L148-L153`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/3e48e9001e9cb2a6d318ae17fc1dbed350fb7946/src/aiv/lib/evidence_collector.py#L148-L153)
- [`src/aiv/lib/evidence_collector.py#L155-L156`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/3e48e9001e9cb2a6d318ae17fc1dbed350fb7946/src/aiv/lib/evidence_collector.py#L155-L156)
- [`src/aiv/lib/evidence_collector.py#L159`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/3e48e9001e9cb2a6d318ae17fc1dbed350fb7946/src/aiv/lib/evidence_collector.py#L159)
- [`src/aiv/lib/evidence_collector.py#L161-L163`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/3e48e9001e9cb2a6d318ae17fc1dbed350fb7946/src/aiv/lib/evidence_collector.py#L161-L163)
- [`src/aiv/lib/evidence_collector.py#L166-L176`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/3e48e9001e9cb2a6d318ae17fc1dbed350fb7946/src/aiv/lib/evidence_collector.py#L166-L176)
- [`src/aiv/lib/evidence_collector.py#L178-L184`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/3e48e9001e9cb2a6d318ae17fc1dbed350fb7946/src/aiv/lib/evidence_collector.py#L178-L184)
- [`src/aiv/lib/evidence_collector.py#L440-L483`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/3e48e9001e9cb2a6d318ae17fc1dbed350fb7946/src/aiv/lib/evidence_collector.py#L440-L483)
- [`src/aiv/lib/evidence_collector.py#L486-L487`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/3e48e9001e9cb2a6d318ae17fc1dbed350fb7946/src/aiv/lib/evidence_collector.py#L486-L487)
- [`src/aiv/lib/evidence_collector.py#L489-L490`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/3e48e9001e9cb2a6d318ae17fc1dbed350fb7946/src/aiv/lib/evidence_collector.py#L489-L490)
- [`src/aiv/lib/evidence_collector.py#L492-L496`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/3e48e9001e9cb2a6d318ae17fc1dbed350fb7946/src/aiv/lib/evidence_collector.py#L492-L496)
- [`src/aiv/lib/evidence_collector.py#L498`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/3e48e9001e9cb2a6d318ae17fc1dbed350fb7946/src/aiv/lib/evidence_collector.py#L498)
- [`src/aiv/lib/evidence_collector.py#L500-L523`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/3e48e9001e9cb2a6d318ae17fc1dbed350fb7946/src/aiv/lib/evidence_collector.py#L500-L523)
- [`src/aiv/lib/evidence_collector.py#L526-L527`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/3e48e9001e9cb2a6d318ae17fc1dbed350fb7946/src/aiv/lib/evidence_collector.py#L526-L527)
- [`src/aiv/lib/evidence_collector.py#L529-L752`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/3e48e9001e9cb2a6d318ae17fc1dbed350fb7946/src/aiv/lib/evidence_collector.py#L529-L752)

### Class A (Execution Evidence)

- **pytest:** 543 passed, 0 failed in 25.53s
- **Tests covering changed file** (31):
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
  - `tests/unit/test_evidence_collector.py::test_to_markdown_shows_provenance_table`
  - `tests/unit/test_evidence_collector.py::test_to_markdown_no_covering_tests`
  - `tests/unit/test_evidence_collector.py::test_to_markdown_includes_git_log`
  - `tests/unit/test_evidence_collector.py::test_collect_with_covering_files`
  - `tests/unit/test_evidence_collector.py::test_collect_no_covering_files_discovers_from_diff`
  - `tests/unit/test_evidence_collector.py::test_resolves_function`
- **ruff:** All checks passed
- **mypy:** Found 1 error in 1 file (checked 1 source file)

### Class C (Negative Evidence)

**Search methodology:** Ran `git diff --cached` and scanned for regression indicators.

- Test file deletions: **none**
- Test file modifications: **none**
- **ALERT:** 1 assertion(s) removed:
  - `3. How many ``assert`` statements were removed from ``tests/``.`
- Added skip markers (`@pytest.mark.skip`, `@unittest.skip`): **none found**

### Class D (Differential Evidence)

- See Class B scope inventory for line-range change details.

### Class F (Provenance Evidence)

**Test file chain-of-custody:**

| File | Commits | Created By | Last Modified By | Assertions |
|------|---------|------------|------------------|------------|
| `tests/unit/test_evidence_collector.py` | 1 | ImmortalDemonGod (2985156) | ImmortalDemonGod (2985156) | 81 |

**Recent test directory history** (`git log --oneline -5 -- tests/`):

```
9547980 test(auditor): 3 tests for evidence TODO severity escalation â€” the exact bar
2985156 test(lib): 18 tests for evidence collector module
c88bb9c test(hooks): 41 tests for portable pre-commit hook
157ccbb style: fix ruff format, lint, and mypy strict errors for CI
a244df3 test(validator): add 6 unit tests for E021 link vitality checking
```

---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence was collected by `aiv commit` running: git diff, pytest -v, ruff, mypy, anti-cheat scan.

---

## Summary

AST symbol resolver + test graph + find_covering_tests + distinct Class F provenance
