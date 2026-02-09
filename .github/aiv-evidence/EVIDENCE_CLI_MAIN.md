# AIV Evidence File (v1.0)

**File:** `src/aiv/cli/main.py`
**Commit:** `6295235`
**Previous:** `875f37e`
**Generated:** 2026-02-09T09:16:40Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R0
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "src/aiv/cli/main.py"
  classification_rationale: "Formatting only"
  classified_by: "ImmortalDemonGod"
  classified_at: "2026-02-09T09:16:40Z"
```

## Claim(s)

1. Ruff auto-format applied to main.py with no logic changes
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/aiv-protocol/blob/62952356eba82e64a7abc3feca46c7e297a68c1f/pyproject.toml](https://github.com/ImmortalDemonGod/aiv-protocol/blob/62952356eba82e64a7abc3feca46c7e297a68c1f/pyproject.toml)
- **Requirements Verified:** All code must pass ruff format check in CI

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`6295235`](https://github.com/ImmortalDemonGod/aiv-protocol/tree/62952356eba82e64a7abc3feca46c7e297a68c1f))

- [`src/aiv/cli/main.py#L661-L663`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/62952356eba82e64a7abc3feca46c7e297a68c1f/src/aiv/cli/main.py#L661-L663)
- [`src/aiv/cli/main.py#L962-L967`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/62952356eba82e64a7abc3feca46c7e297a68c1f/src/aiv/cli/main.py#L962-L967)
- [`src/aiv/cli/main.py#L975`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/62952356eba82e64a7abc3feca46c7e297a68c1f/src/aiv/cli/main.py#L975)

### Class A (Execution Evidence)

- Local checks skipped (--skip-checks).
- **Skip reason:** Formatting only, no logic changes



---

## Verification Methodology

**R0 (trivial) -- local checks skipped.**
**Reason:** Formatting only, no logic changes
Only git diff scope inventory was collected. No execution evidence.

---

## Summary

Apply ruff format to main.py
