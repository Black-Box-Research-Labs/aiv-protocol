# AIV Verification Packet (v2.1)

**Commit:** `0d6b1ea`  
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: module
  classification_rationale: "New validation rule E020 enforcing evidence class coherence for Class A"
  classified_by: "cascade"
  classified_at: "2026-02-07T03:04:40Z"
```

## Claim(s)

1. Added rule E020 (WARN) in `EvidenceValidator._validate_execution`: Class A (Execution) evidence linking to a GitHub code blob instead of a CI run triggers a warning, since execution evidence should prove the code was *run*, not that it *exists*.
2. All 334 tests pass with zero regressions.
3. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [Mastery-level critique analysis](https://github.com/ImmortalDemonGod/aiv-protocol/blob/dd4daf0/tests/integration/test_e2e_compliance.py)
- **Requirements Verified:**
  1. Class A evidence with `link_type == "github_blob"` triggers E020 WARN
  2. Class A evidence with `link_type == "github_actions"` does NOT trigger E020
  3. Existing E012 (UI) and E013 (performance) checks preserved — E020 only fires as fallback

### Class B (Referential Evidence)

**Scope Inventory (required)**

- Modified:
  - `src/aiv/lib/validators/evidence.py`

### Class A (Execution Evidence)

- 334/334 pytest tests pass (328 existing + 6 new)

### Class F (Provenance Evidence)

**Claim 3: No tests weakened**
- No existing tests were modified, deleted, or skipped during this change.
- All pre-existing tests pass unchanged alongside the new rule.

---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.

---

## Summary

Add E020 rule: Class A execution evidence linking to code blob (not CI run) triggers WARN for evidence class coherence.
