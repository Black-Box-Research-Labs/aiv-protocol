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
  classification_rationale: "Validator protocol and abstract base class. All concrete validators depend on this interface. R1 due to being an API contract."
  classified_by: "cascade"
  classified_at: "2026-02-06T22:48:00Z"
```

## Claim(s)

1. `src/aiv/lib/validators/base.py` defines a `Validator` Protocol (runtime_checkable) and `BaseValidator` ABC per AIV-SUITE-SPEC Section 3.3.
2. `Validator` protocol requires a `validate(packet) -> list[ValidationFinding]` method.
3. `BaseValidator` provides a `_make_finding()` helper to reduce boilerplate in concrete validators.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** AIV-SUITE-SPEC-V1.0-CANONICAL Section 3.3 — specifies `src/aiv/lib/validators/base.py` as validator protocol.
- **Requirements Verified:**
  1. ✅ Validator Protocol defined with validate() signature
  2. ✅ BaseValidator ABC with abstract validate()

### Class B (Referential Evidence)

**Scope Inventory (required)**

- Created:
  - `src/aiv/lib/validators/base.py` (~68 lines)

### Class A (Execution Evidence)

- N/A for initial commit.

---

## Summary

Validator protocol and abstract base class defining the interface for all AIV validators.
