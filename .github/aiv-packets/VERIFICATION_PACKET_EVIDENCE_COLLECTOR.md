# AIV Verification Packet (v2.1)

**Commit:** `0fe983b`
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R2
  sod_mode: S1
  critical_surfaces: []
  blast_radius: "src/aiv/lib/evidence_collector.py"
  classification_rationale: "R2: Changes evidence collection output for all Python commits"
  classified_by: "ImmortalDemonGod"
  classified_at: "2026-02-09T03:53:42Z"
```

## Claim(s)

1. resolve_changed_symbols collects every function and class whose line range overlaps with each diff hunk
2. Previous single-symbol-per-hunk behavior starved the claim binder of matchable symbols
3. Claim Verification Matrix now receives all changed symbols for substring matching against claim text
4. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/aiv-protocol/blob/0fe983b/docs/CLAIM_AWARE_EVIDENCE_PLAN.md](https://github.com/ImmortalDemonGod/aiv-protocol/blob/0fe983b/docs/CLAIM_AWARE_EVIDENCE_PLAN.md)
- **Requirements Verified:** V4: Phase 1 resolver limitation — single-symbol-per-hunk caused claim matrix theater

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`0fe983b`](https://github.com/ImmortalDemonGod/aiv-protocol/tree/0fe983b37f5a422ed3a2776f5820cc9d7dc1bdf5))

- [`src/aiv/lib/evidence_collector.py#L626`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/0fe983b37f5a422ed3a2776f5820cc9d7dc1bdf5/src/aiv/lib/evidence_collector.py#L626)
- [`src/aiv/lib/evidence_collector.py#L628-L629`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/0fe983b37f5a422ed3a2776f5820cc9d7dc1bdf5/src/aiv/lib/evidence_collector.py#L628-L629)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`resolve_changed_symbols`** (L626): PASS — 6 test(s) call `resolve_changed_symbols` directly
  - `tests/unit/test_evidence_collector.py::test_resolves_function`
  - `tests/unit/test_evidence_collector.py::test_resolves_class`
  - `tests/unit/test_evidence_collector.py::test_module_level_change`
  - `tests/unit/test_evidence_collector.py::test_nonexistent_file`
  - `tests/unit/test_evidence_collector.py::test_multi_symbol_hunk`
  - `tests/unit/test_evidence_collector.py::test_multi_symbol_class_methods`

**Coverage summary:** 1/1 symbols verified by tests.
- **ruff:** All checks passed
- **mypy:** Found 1 error in 1 file (checked 1 source file)

### Class C (Negative Evidence)

**Search methodology:** Ran `git diff --cached` and scanned for regression indicators.

- Test file deletions: **none**
- Test file modifications: **none**
- Deleted assertions (`assert` removals in diff): **none found**
- Added skip markers (`@pytest.mark.skip`, `@unittest.skip`): **none found**

**Downstream impact analysis (AST):**

- `resolve_changed_symbols` is called by:
  - `src/aiv/cli/main.py::commit_cmd`

### Class F (Provenance Evidence)

**Test file chain-of-custody:**

| File | Commits | Created By | Last Modified By | Assertions |
|------|---------|------------|------------------|------------|
| `tests/unit/test_evidence_collector.py` | 4 | ImmortalDemonGod (2985156) | ImmortalDemonGod (e53f2c6) | 144 |
| `tests/unit/test_auditor.py` | 5 | ImmortalDemonGod (0a6f437) | ImmortalDemonGod (c1a2dbb) | 62 |

**Recent test directory history** (`git log --oneline -5 -- tests/`):

```
7d12d07 test(hooks): 15 tests for pre-push hook â€” violation detection, clean commits, stdin parsing
c1a2dbb test(auditor): 14 tests for audit_commits â€” HOOK_BYPASS, ATOMIC_VIOLATION, helpers
249ecde feat(hooks): P0-1 + P0-2 â€” configurable functional prefixes via .aiv.yml, remove project-specific artifacts (580 green)
e53f2c6 feat(lib): Phases 5-8 â€” claim verification matrix, R3 blocking, Class D diff stat, 16 new tests (569 green)
e405110 test(lib): 39 tests â€” AST coverage, downstream callers, retro-test for xdist
```

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | resolve_changed_symbols collects every function and class wh... | symbol | 6 test(s) call `resolve_changed_symbols` | PASS VERIFIED |
| 2 | Previous single-symbol-per-hunk behavior starved the claim b... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 3 | Claim Verification Matrix now receives all changed symbols f... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 4 | No existing tests were modified or deleted during this chang... | structural | Class C: all structural indicators clean | PASS VERIFIED |

**Verdict summary:** 2 verified, 0 unverified, 2 manual review.

---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence was collected by `aiv commit` running: git diff, pytest -v, ruff, mypy, anti-cheat scan.

---

## Summary

AST symbol resolver now reports all overlapping symbols per hunk instead of only the innermost
