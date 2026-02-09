# AIV Evidence File (v1.0)

**File:** `src/aiv/hooks/pre_push.py`
**Commit:** `42610ae`
**Generated:** 2026-02-09T05:14:48Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "src/aiv/hooks/pre_push.py"
  classification_rationale: "Hook logic changes, standard enforcement layer"
  classified_by: "ImmortalDemonGod"
  classified_at: "2026-02-09T05:14:48Z"
```

## Claim(s)

1. Pre-push hook blocks push on protected branch when unclosed change context has commits
2. Pre-push hook recognizes PACKET_ prefix and EVIDENCE_ prefix in addition to VERIFICATION_PACKET_
3. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/aiv-protocol/blob/main/docs/TWO_LAYER_VERIFICATION_ARCHITECTURE.md](https://github.com/ImmortalDemonGod/aiv-protocol/blob/main/docs/TWO_LAYER_VERIFICATION_ARCHITECTURE.md)
- **Requirements Verified:** Design doc section 8.2: Pre-push behavior

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`42610ae`](https://github.com/ImmortalDemonGod/aiv-protocol/tree/42610ae0d2e21dab2552c7bde0cd25a1aca37cb8))

- [`src/aiv/hooks/pre_push.py#L37`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/42610ae0d2e21dab2552c7bde0cd25a1aca37cb8/src/aiv/hooks/pre_push.py#L37)
- [`src/aiv/hooks/pre_push.py#L40`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/42610ae0d2e21dab2552c7bde0cd25a1aca37cb8/src/aiv/hooks/pre_push.py#L40)
- [`src/aiv/hooks/pre_push.py#L159-L183`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/42610ae0d2e21dab2552c7bde0cd25a1aca37cb8/src/aiv/hooks/pre_push.py#L159-L183)
- [`src/aiv/hooks/pre_push.py#L192-L213`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/42610ae0d2e21dab2552c7bde0cd25a1aca37cb8/src/aiv/hooks/pre_push.py#L192-L213)

### Class A (Execution Evidence)

- Local checks skipped (--skip-checks).



---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence was collected by `aiv commit` running: git diff, pytest -v, ruff, mypy, anti-cheat scan.

---

## Summary

Add unclosed-change detection on protected branches and new naming recognition
