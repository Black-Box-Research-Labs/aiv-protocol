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
  classification_rationale: "Zero-Touch compliance validator enforcing Addendum 2.7. R1 because it gates reproduction instructions in verification packets."
  classified_by: "cascade"
  classified_at: "2026-02-06T22:55:00Z"
```

## Claim(s)

1. `src/aiv/lib/validators/zero_touch.py` implements `ZeroTouchValidator` per AIV-SUITE-SPEC Section 5.2.
2. Validates reproduction instructions against prohibited patterns (git clone, npm install, pytest, manual GUI steps) with BLOCK severity (rule E008).
3. Detects multi-step instructions via separators (`;`, `&&`, numbered steps) and warns when exceeding max_steps threshold.
4. Computes `FrictionScore` per claim with prohibited pattern count and step count weighting.
5. Generates actionable recommendations based on violation type (git → permalinks, install → CI, run → CI artifact).
6. Allowed patterns bypass validation: N/A, CI Automation, See CI, Link above, Automated via, URLs.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** AIV-SUITE-SPEC-V1.0-CANONICAL Section 5.2 — Zero-Touch Validator specification.
- **Requirements Verified:**
  1. ✅ Prohibited patterns from spec Section 2.4 zero_touch_rules
  2. ✅ Allowed patterns from spec Section 2.4
  3. ✅ Multi-step detection with configurable threshold
  4. ✅ FrictionScore computation per spec Section 4.1

### Class B (Referential Evidence)

**Scope Inventory (required)**

- Created:
  - `src/aiv/lib/validators/zero_touch.py` (~165 lines)

### Class A (Execution Evidence)

- N/A for initial commit.

---

## Summary

Zero-Touch compliance validator enforcing Addendum 2.7 reproduction instruction requirements per AIV-SUITE-SPEC Section 5.2.
