# AIV Evidence File (v1.0)

**File:** `src/aiv/cli/main.py`
**Commit:** `d5ede86`
**Previous:** `dbbda10`
**Generated:** 2026-02-09T18:42:18Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "src/aiv/cli/main.py"
  classification_rationale: "Anti-verification-theater enforcement in CLI commit"
  classified_by: "ImmortalDemonGod"
  classified_at: "2026-02-09T18:42:18Z"
```

## Claim(s)

1. Phase 7 now blocks R1+ commits when >50% of bindable claims are UNVERIFIED (R3 blocks on any)
2. Methodology text reports AST symbol verification ratio instead of global pytest count
3. Evidence assembly includes Code Quality section separate from Class A
4. aiv close extracts real claims and Class B refs from evidence files
5. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/aiv-protocol/blob/d5ede8644713b70c44c99bbec6bf7c3e6fb7aca8/docs/CLAIM_AWARE_EVIDENCE_PLAN.md](https://github.com/ImmortalDemonGod/aiv-protocol/blob/d5ede8644713b70c44c99bbec6bf7c3e6fb7aca8/docs/CLAIM_AWARE_EVIDENCE_PLAN.md)
- **Requirements Verified:** Theater Gap 3: unverified claims must block, not just warn

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`d5ede86`](https://github.com/ImmortalDemonGod/aiv-protocol/tree/d5ede8644713b70c44c99bbec6bf7c3e6fb7aca8))

- [`src/aiv/cli/main.py#L1630`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/d5ede8644713b70c44c99bbec6bf7c3e6fb7aca8/src/aiv/cli/main.py#L1630)
- [`src/aiv/cli/main.py#L1632-L1653`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/d5ede8644713b70c44c99bbec6bf7c3e6fb7aca8/src/aiv/cli/main.py#L1632-L1653)
- [`src/aiv/cli/main.py#L1670`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/d5ede8644713b70c44c99bbec6bf7c3e6fb7aca8/src/aiv/cli/main.py#L1670)
- [`src/aiv/cli/main.py#L1673-L1679`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/d5ede8644713b70c44c99bbec6bf7c3e6fb7aca8/src/aiv/cli/main.py#L1673-L1679)
- [`src/aiv/cli/main.py#L1684-L1686`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/d5ede8644713b70c44c99bbec6bf7c3e6fb7aca8/src/aiv/cli/main.py#L1684-L1686)
- [`src/aiv/cli/main.py#L1691-L1693`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/d5ede8644713b70c44c99bbec6bf7c3e6fb7aca8/src/aiv/cli/main.py#L1691-L1693)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`commit_cmd`** (L1630): FAIL -- WARNING: No tests import or call `commit_cmd`

**Coverage summary:** 0/1 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** All checks passed
- **mypy:** Success: no issues found in 1 source file

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | Phase 7 now blocks R1+ commits when >50% of bindable claims ... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | Methodology text reports AST symbol verification ratio inste... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 3 | Evidence assembly includes Code Quality section separate fro... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 4 | aiv close extracts real claims and Class B refs from evidenc... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 5 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 5 manual review.

---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (0/1 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

R1+ commits now blocked when claims lack test evidence; methodology is honest about coverage gaps
