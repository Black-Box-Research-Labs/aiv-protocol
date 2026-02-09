# AIV Evidence File (v1.0)

**File:** `src/aiv/hooks/pre_push.py`
**Commit:** `20e6a60`
**Previous:** `270abf2`
**Generated:** 2026-02-09T07:48:44Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "src/aiv/hooks/pre_push.py"
  classification_rationale: "Hook enforcement logic change affecting push blocking behavior"
  classified_by: "ImmortalDemonGod"
  classified_at: "2026-02-09T07:48:44Z"
```

## Claim(s)

1. Pre-push hook allows functional-only commits when Layer 2 packets or evidence files exist in the push range
2. Pre-push hook still blocks functional-only commits when no evidence exists anywhere in the push range
3. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/aiv-protocol/blob/main/docs/TWO_LAYER_VERIFICATION_ARCHITECTURE.md](https://github.com/ImmortalDemonGod/aiv-protocol/blob/main/docs/TWO_LAYER_VERIFICATION_ARCHITECTURE.md)
- **Requirements Verified:** Two-Layer Architecture requires pre-push hook to recognize range-level evidence coverage

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`20e6a60`](https://github.com/ImmortalDemonGod/aiv-protocol/tree/20e6a60778a83826efbd22fcb05d88170ebea102))

- [`src/aiv/hooks/pre_push.py#L140-L143`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/20e6a60778a83826efbd22fcb05d88170ebea102/src/aiv/hooks/pre_push.py#L140-L143)
- [`src/aiv/hooks/pre_push.py#L148-L151`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/20e6a60778a83826efbd22fcb05d88170ebea102/src/aiv/hooks/pre_push.py#L148-L151)
- [`src/aiv/hooks/pre_push.py#L155-L156`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/20e6a60778a83826efbd22fcb05d88170ebea102/src/aiv/hooks/pre_push.py#L155-L156)
- [`src/aiv/hooks/pre_push.py#L158-L169`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/20e6a60778a83826efbd22fcb05d88170ebea102/src/aiv/hooks/pre_push.py#L158-L169)
- [`src/aiv/hooks/pre_push.py#L172-L183`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/20e6a60778a83826efbd22fcb05d88170ebea102/src/aiv/hooks/pre_push.py#L172-L183)
- [`src/aiv/hooks/pre_push.py#L185-L186`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/20e6a60778a83826efbd22fcb05d88170ebea102/src/aiv/hooks/pre_push.py#L185-L186)

### Class A (Execution Evidence)

- Local checks skipped (--skip-checks).



---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence was collected by `aiv commit` running: git diff, pytest -v, ruff, mypy, anti-cheat scan.

---

## Summary

Pre-push hook checks entire push range for evidence before blocking
