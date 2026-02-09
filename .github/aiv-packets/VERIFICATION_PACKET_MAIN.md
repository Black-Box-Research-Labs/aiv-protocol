# AIV Verification Packet (v2.1)

**Commit:** `e405110`
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R2
  sod_mode: S1
  critical_surfaces: []
  blast_radius: "src/aiv/cli/main.py"
  classification_rationale: "Completes the integration of AST evidence pipeline into the CLI command"
  classified_by: "ImmortalDemonGod"
  classified_at: "2026-02-09T02:20:50Z"
```

## Claim(s)

1. aiv commit now runs resolve_changed_symbols + build_test_graph + find_covering_tests for Python files, populating per-symbol AST coverage in Class A
2. aiv commit now runs find_downstream_callers for Class C at R2+, showing which src/ functions call the changed symbols
3. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/aiv-protocol/blob/3e48e90/docs/CLAIM_AWARE_EVIDENCE_PLAN.md](https://github.com/ImmortalDemonGod/aiv-protocol/blob/3e48e90/docs/CLAIM_AWARE_EVIDENCE_PLAN.md)
- **Requirements Verified:** CLAIM_AWARE_EVIDENCE_PLAN.md: aiv commit must run AST pipeline for Python files and render per-symbol coverage

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`e405110`](https://github.com/ImmortalDemonGod/aiv-protocol/tree/e405110c2a60bdfb1f99f267381051380310ff03))

- [`src/aiv/cli/main.py#L753`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/e405110c2a60bdfb1f99f267381051380310ff03/src/aiv/cli/main.py#L753)
- [`src/aiv/cli/main.py#L758`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/e405110c2a60bdfb1f99f267381051380310ff03/src/aiv/cli/main.py#L758)
- [`src/aiv/cli/main.py#L763-L764`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/e405110c2a60bdfb1f99f267381051380310ff03/src/aiv/cli/main.py#L763-L764)
- [`src/aiv/cli/main.py#L854`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/e405110c2a60bdfb1f99f267381051380310ff03/src/aiv/cli/main.py#L854)
- [`src/aiv/cli/main.py#L863-L893`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/e405110c2a60bdfb1f99f267381051380310ff03/src/aiv/cli/main.py#L863-L893)
- [`src/aiv/cli/main.py#L915-L930`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/e405110c2a60bdfb1f99f267381051380310ff03/src/aiv/cli/main.py#L915-L930)

### Class A (Execution Evidence)

- **pytest:** 551 passed, 0 failed in 29.66s

**Per-symbol test coverage (AST analysis):**

- **`commit_cmd`** (changed at L753):
  - WARNING: No tests import or call `commit_cmd`
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
e405110 test(lib): 39 tests â€” AST coverage, downstream callers, retro-test for xdist
f81b6e6 test(lib): 31 tests for AST symbol resolver, test graph, and semantic coverage
9547980 test(auditor): 3 tests for evidence TODO severity escalation â€” the exact bar
2985156 test(lib): 18 tests for evidence collector module
c88bb9c test(hooks): 41 tests for portable pre-commit hook
```

---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence was collected by `aiv commit` running: git diff, pytest -v, ruff, mypy, anti-cheat scan.

---

## Summary

Wire AST symbol resolver, test graph, and downstream caller analysis into aiv commit
