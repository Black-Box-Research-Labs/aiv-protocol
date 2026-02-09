# AIV Evidence File (v1.0)

**File:** `src/aiv/cli/main.py`
**Commit:** `022d5df`
**Previous:** `f6fb5a9`
**Generated:** 2026-02-09T19:38:06Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "src/aiv/cli/main.py"
  classification_rationale: "Anti-theater enforcement: removing the escape hatch that made the gate meaningless"
  classified_by: "ImmortalDemonGod"
  classified_at: "2026-02-09T19:38:06Z"
```

## Claim(s)

1. commit_cmd no longer accepts --force flag (no bypass for unverified claims)
2. Blocking message shows only two options: write tests or downgrade to R0
3. quickstart enforcement text states no bypass exists
4. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/aiv-protocol/blob/022d5dfcefbd7a1a93230b716e2e6e7b80540dbe/docs/CLAIM_AWARE_EVIDENCE_PLAN.md](https://github.com/ImmortalDemonGod/aiv-protocol/blob/022d5dfcefbd7a1a93230b716e2e6e7b80540dbe/docs/CLAIM_AWARE_EVIDENCE_PLAN.md)
- **Requirements Verified:** Verification theater: --force bypass undermines the entire claim verification gate

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`022d5df`](https://github.com/ImmortalDemonGod/aiv-protocol/tree/022d5dfcefbd7a1a93230b716e2e6e7b80540dbe))

- [`src/aiv/cli/main.py#L314`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/022d5dfcefbd7a1a93230b716e2e6e7b80540dbe/src/aiv/cli/main.py#L314)
- [`src/aiv/cli/main.py#L1741`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/022d5dfcefbd7a1a93230b716e2e6e7b80540dbe/src/aiv/cli/main.py#L1741)
- [`src/aiv/cli/main.py#L1756`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/022d5dfcefbd7a1a93230b716e2e6e7b80540dbe/src/aiv/cli/main.py#L1756)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`quickstart`** (L314): FAIL -- WARNING: No tests import or call `quickstart`
- **`commit_cmd`** (L1741): PASS -- 5 test(s) call `commit_cmd` directly
  - `tests/unit/test_cli_commit_skip.py::test_skip_checks_rejected_for_higher_tiers`
  - `tests/unit/test_cli_commit_skip.py::test_skip_checks_without_reason_fails`
  - `tests/unit/test_cli_commit_skip.py::test_skip_checks_with_reason_succeeds`
  - `tests/unit/test_cli_commit_skip.py::test_reason_in_class_a`
  - `tests/unit/test_cli_commit_skip.py::test_reason_in_methodology`

**Coverage summary:** 1/2 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** All checks passed
- **mypy:** Success: no issues found in 1 source file

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | commit_cmd no longer accepts --force flag (no bypass for unv... | symbol | 5 test(s) call `commit_cmd` | PASS VERIFIED |
| 2 | Blocking message shows only two options: write tests or down... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 3 | quickstart enforcement text states no bypass exists | symbol | 0 tests call `quickstart` | FAIL UNVERIFIED |
| 4 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 1 verified, 1 unverified, 2 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (1/2 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Remove --force from aiv commit; no bypass for unverified claims
