# AIV Evidence File (v1.0)

**File:** `src/aiv/cli/main.py`
**Commit:** `7bf7060`
**Previous:** `3125e84`
**Generated:** 2026-02-10T20:50:37Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "src/aiv/cli/main.py"
  classification_rationale: "R1: refactor dispatch logic"
  classified_by: "Miguel Ingram"
  classified_at: "2026-02-10T20:50:37Z"
```

## Claim(s)

1. AST analysis and downstream caller detection now use lang_driver from registry instead of file_posix_raw.endswith('.py'). Enables polyglot evidence for any registered language.
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/aiv-protocol/blob/7bf7060a3a24d166830feed03004a84ce6c84953/docs/EXTERNAL_READINESS_AUDIT.md](https://github.com/ImmortalDemonGod/aiv-protocol/blob/7bf7060a3a24d166830feed03004a84ce6c84953/docs/EXTERNAL_READINESS_AUDIT.md)
- **Requirements Verified:** P1-6: evidence collection must dispatch by file extension via driver registry

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`7bf7060`](https://github.com/ImmortalDemonGod/aiv-protocol/tree/7bf7060a3a24d166830feed03004a84ce6c84953))

- [`src/aiv/cli/main.py#L1605-L1607`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/7bf7060a3a24d166830feed03004a84ce6c84953/src/aiv/cli/main.py#L1605-L1607)
- [`src/aiv/cli/main.py#L1615-L1617`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/7bf7060a3a24d166830feed03004a84ce6c84953/src/aiv/cli/main.py#L1615-L1617)
- [`src/aiv/cli/main.py#L1632-L1633`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/7bf7060a3a24d166830feed03004a84ce6c84953/src/aiv/cli/main.py#L1632-L1633)
- [`src/aiv/cli/main.py#L1664`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/7bf7060a3a24d166830feed03004a84ce6c84953/src/aiv/cli/main.py#L1664)
- [`src/aiv/cli/main.py#L1666-L1668`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/7bf7060a3a24d166830feed03004a84ce6c84953/src/aiv/cli/main.py#L1666-L1668)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`commit_cmd`** (L1605-L1607): PASS -- 5 test(s) call `commit_cmd` directly
  - `tests/unit/test_cli_commit_skip.py::test_skip_checks_rejected_for_higher_tiers`
  - `tests/unit/test_cli_commit_skip.py::test_skip_checks_without_reason_fails`
  - `tests/unit/test_cli_commit_skip.py::test_skip_checks_with_reason_succeeds`
  - `tests/unit/test_cli_commit_skip.py::test_reason_in_class_a`
  - `tests/unit/test_cli_commit_skip.py::test_reason_in_methodology`

**Coverage summary:** 1/1 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** All checks passed
- **mypy:** Success: no issues found in 1 source file

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | AST analysis and downstream caller detection now use lang_dr... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 2 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (1/1 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

commit_cmd
