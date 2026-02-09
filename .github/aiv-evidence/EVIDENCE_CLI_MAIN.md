# AIV Evidence File (v1.0)

**File:** `src/aiv/cli/main.py`
**Commit:** `06ad610`
**Previous:** `38c2c0c`
**Generated:** 2026-02-09T05:30:49Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R0
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "src/aiv/cli/main.py"
  classification_rationale: "Trivial string change, no logic"
  classified_by: "ImmortalDemonGod"
  classified_at: "2026-02-09T05:30:49Z"
```

## Claim(s)

1. aiv init tip message now directs users to aiv begin instead of aiv generate
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/aiv-protocol/blob/main/README.md](https://github.com/ImmortalDemonGod/aiv-protocol/blob/main/README.md)
- **Requirements Verified:** README quickstart references aiv begin as primary workflow

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`06ad610`](https://github.com/ImmortalDemonGod/aiv-protocol/tree/06ad610005f1f48afbd87d43e6967c1e3c5eb253))

- [`src/aiv/cli/main.py#L229`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/06ad610005f1f48afbd87d43e6967c1e3c5eb253/src/aiv/cli/main.py#L229)

### Class A (Execution Evidence)

- Local checks skipped (--skip-checks).



---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence was collected by `aiv commit` running: git diff, pytest -v, ruff, mypy, anti-cheat scan.

---

## Summary

Update aiv init tip from aiv generate to aiv begin
