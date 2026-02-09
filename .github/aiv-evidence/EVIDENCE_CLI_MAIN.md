# AIV Evidence File (v1.0)

**File:** `src/aiv/cli/main.py`
**Commit:** `3715874`
**Previous:** `5e72d42`
**Generated:** 2026-02-09T08:49:10Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "src/aiv/cli/main.py"
  classification_rationale: "CLI behavior change for audit command -- standard R1"
  classified_by: "ImmortalDemonGod"
  classified_at: "2026-02-09T08:49:10Z"
```

## Claim(s)

1. aiv audit scans .github/aiv-evidence/ by default alongside .github/aiv-packets/
2. aiv audit --no-evidence skips Layer 1 evidence file scanning
3. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/aiv-protocol/blob/3715874d2b61deba585b4120c6bfdb95c2e1bf52/docs/TWO_LAYER_VERIFICATION_ARCHITECTURE.md](https://github.com/ImmortalDemonGod/aiv-protocol/blob/3715874d2b61deba585b4120c6bfdb95c2e1bf52/docs/TWO_LAYER_VERIFICATION_ARCHITECTURE.md)
- **Requirements Verified:** Two-Layer Architecture requires auditor to scan both layers

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`3715874`](https://github.com/ImmortalDemonGod/aiv-protocol/tree/3715874d2b61deba585b4120c6bfdb95c2e1bf52))

- [`src/aiv/cli/main.py#L245-L249`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/3715874d2b61deba585b4120c6bfdb95c2e1bf52/src/aiv/cli/main.py#L245-L249)
- [`src/aiv/cli/main.py#L252`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/3715874d2b61deba585b4120c6bfdb95c2e1bf52/src/aiv/cli/main.py#L252)
- [`src/aiv/cli/main.py#L254-L255`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/3715874d2b61deba585b4120c6bfdb95c2e1bf52/src/aiv/cli/main.py#L254-L255)
- [`src/aiv/cli/main.py#L257`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/3715874d2b61deba585b4120c6bfdb95c2e1bf52/src/aiv/cli/main.py#L257)
- [`src/aiv/cli/main.py#L267`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/3715874d2b61deba585b4120c6bfdb95c2e1bf52/src/aiv/cli/main.py#L267)
- [`src/aiv/cli/main.py#L271`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/3715874d2b61deba585b4120c6bfdb95c2e1bf52/src/aiv/cli/main.py#L271)
- [`src/aiv/cli/main.py#L273`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/3715874d2b61deba585b4120c6bfdb95c2e1bf52/src/aiv/cli/main.py#L273)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`audit`** (L245-L249): FAIL — WARNING: No tests import or call `audit`

**Coverage summary:** 0/1 symbols verified by tests.
- **ruff:** All checks passed
- **mypy:** Success: no issues found in 1 source file

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | aiv audit scans .github/aiv-evidence/ by default alongside .... | symbol | 0 tests call `audit` | FAIL UNVERIFIED |
| 2 | aiv audit --no-evidence skips Layer 1 evidence file scanning | symbol | 0 tests call `audit` | FAIL UNVERIFIED |
| 3 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 2 unverified, 1 manual review.

---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff, pytest (677 passed, 10 failed), ruff (clean), mypy (Success: no issues found in 1 source file), AST symbol-to-test binding (1 symbols).

---

## Summary

aiv audit now scans evidence files by default with --no-evidence opt-out
