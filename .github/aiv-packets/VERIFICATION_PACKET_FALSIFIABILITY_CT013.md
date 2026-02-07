# AIV Verification Packet (v2.1)

**Commit:** `90557ff`  
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: module
  classification_rationale: "Add CT-013 canonical rule: R2+ claims with Class A evidence must include test_refs for falsifiability"
  classified_by: "cascade"
  classified_at: "2026-02-07T03:25:00Z"
```

## Claim(s)

1. The `_validate_claim_test_refs` function warns (CT-013) when R2+ claims reference Class A evidence but provide no `test_refs` array.
2. The validator warns (CT-013) when a claim's `test_refs` reference a `test_id` not found in the Class A `test_list`.
3. CT-013 validation is skipped for R0/R1 packets to avoid over-toil on low-risk changes.
4. All 347 tests pass with zero regressions; 4 new E2E tests added for CT-013.
5. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [AIV-SUITE-SPEC-V1.0-CANONICAL](https://github.com/ImmortalDemonGod/aiv-protocol/blob/d8b6225/docs/specs/AIV-SUITE-SPEC-V1.0-CANONICAL_2025-12-19.md)
- **Requirements Verified:**
  1. R2+ claims must map to specific test IDs for machine-verifiable falsifiability
  2. R0/R1 bypass CT-013 to avoid toil on trivial changes
  3. Unknown test_id references trigger WARN

### Class B (Referential Evidence)

**Scope Inventory (required)**

- Modified:
  - `src/aiv/guard/canonical.py`
  - `tests/integration/test_e2e_compliance.py`

### Class A (Execution Evidence)

- 347/347 pytest tests pass (338 existing + 4 new CT-013 + 5 new SVP)

### Class F (Provenance Evidence)

**Claim 5: No tests weakened**
- No existing tests were modified, deleted, or skipped during this change.
- All pre-existing canonical tests pass unchanged alongside the new additions.

---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.

---

## Summary

Add CT-013 canonical rule: R2+ claims with Class A evidence must include test_refs for machine-verifiable falsifiability.
