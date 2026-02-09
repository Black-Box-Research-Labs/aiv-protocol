# AIV Verification Packet (v2.1)

**Commit:** `e58b81c`
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R3
  sod_mode: S1
  critical_surfaces: []
  blast_radius: "src/aiv/lib/evidence_collector.py"
  classification_rationale: "R3: completes the AST evidence pipeline — all four phases of the design plan are now implemented"
  classified_by: "ImmortalDemonGod"
  classified_at: "2026-02-09T02:18:53Z"
```

## Claim(s)

1. ClassAEvidence.to_markdown renders per-symbol AST coverage when symbol_coverage is populated, falls back to grep list otherwise
2. ClassCEvidence.to_markdown renders downstream impact analysis showing which src/ functions call changed symbols
3. find_downstream_callers scans src/ AST for callers of changed symbols, excluding the committed file
4. DownstreamCaller dataclass groups callers by symbol in Class C output
5. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/aiv-protocol/blob/3e48e90/docs/CLAIM_AWARE_EVIDENCE_PLAN.md](https://github.com/ImmortalDemonGod/aiv-protocol/blob/3e48e90/docs/CLAIM_AWARE_EVIDENCE_PLAN.md)
- **Requirements Verified:** CLAIM_AWARE_EVIDENCE_PLAN.md Phase 3-4: Class A must show per-symbol coverage, Class C must show downstream callers

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`e58b81c`](https://github.com/ImmortalDemonGod/aiv-protocol/tree/e58b81cc1addd9d34478450da0704efdf8f4e27e))

- [`src/aiv/lib/evidence_collector.py#L62`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/e58b81cc1addd9d34478450da0704efdf8f4e27e/src/aiv/lib/evidence_collector.py#L62)
- [`src/aiv/lib/evidence_collector.py#L67-L69`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/e58b81cc1addd9d34478450da0704efdf8f4e27e/src/aiv/lib/evidence_collector.py#L67-L69)
- [`src/aiv/lib/evidence_collector.py#L73-L90`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/e58b81cc1addd9d34478450da0704efdf8f4e27e/src/aiv/lib/evidence_collector.py#L73-L90)
- [`src/aiv/lib/evidence_collector.py#L92`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/e58b81cc1addd9d34478450da0704efdf8f4e27e/src/aiv/lib/evidence_collector.py#L92)
- [`src/aiv/lib/evidence_collector.py#L96`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/e58b81cc1addd9d34478450da0704efdf8f4e27e/src/aiv/lib/evidence_collector.py#L96)
- [`src/aiv/lib/evidence_collector.py#L102-L110`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/e58b81cc1addd9d34478450da0704efdf8f4e27e/src/aiv/lib/evidence_collector.py#L102-L110)
- [`src/aiv/lib/evidence_collector.py#L120`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/e58b81cc1addd9d34478450da0704efdf8f4e27e/src/aiv/lib/evidence_collector.py#L120)
- [`src/aiv/lib/evidence_collector.py#L128-L130`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/e58b81cc1addd9d34478450da0704efdf8f4e27e/src/aiv/lib/evidence_collector.py#L128-L130)
- [`src/aiv/lib/evidence_collector.py#L163-L175`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/e58b81cc1addd9d34478450da0704efdf8f4e27e/src/aiv/lib/evidence_collector.py#L163-L175)
- [`src/aiv/lib/evidence_collector.py#L799-L862`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/e58b81cc1addd9d34478450da0704efdf8f4e27e/src/aiv/lib/evidence_collector.py#L799-L862)

### Class A (Execution Evidence)

- **pytest:** 551 passed, 0 failed in 29.19s

**Per-symbol test coverage (AST analysis):**

- **`ClassAEvidence`** (changed at L62):
  - 6 test(s) call `ClassAEvidence` directly
  - `tests/unit/test_evidence_collector.py::test_to_markdown_includes_test_names`
  - `tests/unit/test_evidence_collector.py::test_to_markdown_warns_no_tests`
  - `tests/unit/test_evidence_collector.py::test_to_markdown_ruff_errors`
  - `tests/unit/test_evidence_collector.py::test_renders_per_symbol_coverage`
  - `tests/unit/test_evidence_collector.py::test_renders_warning_for_uncovered_symbol`
  - `tests/unit/test_evidence_collector.py::test_falls_back_to_grep_when_no_ast`
- **`ClassAEvidence.to_markdown`** (changed at L67-L69):
  - WARNING: No tests import or call `to_markdown`
- **`DownstreamCaller`** (changed at L73-L90):
  - 1 test(s) call `DownstreamCaller` directly
  - `tests/unit/test_evidence_collector.py::test_renders_downstream_callers`
- **`ClassCEvidence`** (changed at L92):
  - 5 test(s) call `ClassCEvidence` directly
  - `tests/unit/test_evidence_collector.py::test_to_markdown_clean`
  - `tests/unit/test_evidence_collector.py::test_to_markdown_alerts_on_deletions`
  - `tests/unit/test_evidence_collector.py::test_to_markdown_alerts_on_skip_markers`
  - `tests/unit/test_evidence_collector.py::test_renders_downstream_callers`
  - `tests/unit/test_evidence_collector.py::test_no_downstream_callers_omits_section`
- **`ClassCEvidence.to_markdown`** (changed at L96):
  - WARNING: No tests import or call `to_markdown`
- **`find_downstream_callers`** (changed at L102-L110):
  - 3 test(s) call `find_downstream_callers` directly
  - `tests/unit/test_evidence_collector.py::test_finds_caller_in_src`
  - `tests/unit/test_evidence_collector.py::test_excludes_committed_file`
  - `tests/unit/test_evidence_collector.py::test_no_callers_returns_empty`
- **ruff:** All checks passed
- **mypy:** Found 1 error in 1 file (checked 1 source file)

### Class C (Negative Evidence)

**Search methodology:** Ran `git diff --cached` and scanned for regression indicators.

- Test file deletions: **none**
- Test file modifications: **none**
- Deleted assertions (`assert` removals in diff): **none found**
- Added skip markers (`@pytest.mark.skip`, `@unittest.skip`): **none found**

**Downstream impact analysis (AST):**

- `find_downstream_callers` is called by:
  - `src/aiv/cli/main.py::commit_cmd`

### Class D (Differential Evidence)

- See Class B scope inventory for line-range change details.

### Class F (Provenance Evidence)

**Test file chain-of-custody:**

| File | Commits | Created By | Last Modified By | Assertions |
|------|---------|------------|------------------|------------|
| `tests/unit/test_evidence_collector.py` | 2 | ImmortalDemonGod (2985156) | ImmortalDemonGod (f81b6e6) | 100 |

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

Wire AST per-symbol coverage into Class A and downstream caller analysis into Class C
