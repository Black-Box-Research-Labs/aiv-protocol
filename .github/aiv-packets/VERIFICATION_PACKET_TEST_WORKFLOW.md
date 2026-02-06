# AIV Verification Packet (v2.1)

**Commit:** `pending`  
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: component
  classification_rationale: "Integration tests validating the complete validation pipeline end-to-end. R1 because they verify the correctness of the full pipeline orchestration."
  classified_by: "cascade"
  classified_at: "2026-02-07T00:15:00Z"
```

## Claim(s)

1. `tests/integration/test_full_workflow.py` provides 8 integration tests per AIV-SUITE-SPEC Section 10.3.
2. Tests cover: valid packet passes, missing header fails (E001), mutable link fails (E004), manual reproduction blocks (E008), deleted assertion without justification fails (E011), clean diff passes, skip decorator detected (E011), non-strict mode allows warnings.
3. Uses shared fixtures from `tests/conftest.py` for packet and diff data.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** AIV-SUITE-SPEC-V1.0-CANONICAL Section 10.3 — Integration Test Examples.
- **Requirements Verified:**
  1. ✅ All integration test scenarios from spec Section 10.3
  2. ✅ Pipeline end-to-end validation coverage

### Class B (Referential Evidence)

**Scope Inventory (required)**

- Created:
  - `tests/integration/test_full_workflow.py` (~100 lines)

### Class A (Execution Evidence)

- Will be validated when `pytest` is run in Phase 12.

---

## Summary

Integration tests for full validation pipeline per AIV-SUITE-SPEC Section 10.3.
