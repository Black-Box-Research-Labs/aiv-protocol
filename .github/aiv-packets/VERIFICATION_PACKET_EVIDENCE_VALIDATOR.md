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
  classification_rationale: "Evidence class-specific validator implementing per-class rules (A-F). R1 because it enforces evidence quality requirements per risk tier."
  classified_by: "cascade"
  classified_at: "2026-02-06T23:05:00Z"
```

## Claim(s)

1. `src/aiv/lib/validators/evidence.py` implements `EvidenceValidator` per AIV-SUITE-SPEC Section 7.2.
2. Dispatches to 6 class-specific validators: _validate_execution (A), _validate_referential (B), _validate_negative (C), _validate_state (D), _validate_intent (E), _validate_conservation (F).
3. Class A validates CI link type and detects performance/UI claims requiring specific evidence formats (rules E012, E013).
4. Class D blocks manual database queries in reproduction instructions (Zero-Touch enforcement).
5. Bug fix heuristic detects fix/bug/issue/patch keywords and requires Class F conservation evidence (rule E010).
6. Class F warns when test-related claims lack justification (rule E011).

---

## Evidence

### Class E (Intent Alignment)

- **Link:** AIV-SUITE-SPEC-V1.0-CANONICAL Section 7.2 — Evidence Class-Specific Validation specification.
- **Requirements Verified:**
  1. ✅ All 6 evidence class validators from spec Section 7.2
  2. ✅ Bug fix detection heuristic per Addendum 2.4
  3. ✅ Class-specific rules E004, E007, E010, E011, E012, E013

### Class B (Referential Evidence)

**Scope Inventory (required)**

- Created:
  - `src/aiv/lib/validators/evidence.py` (~230 lines)

### Class A (Execution Evidence)

- N/A for initial commit.

---

## Summary

Evidence class-specific validator with per-class rules (A-F) and bug fix detection per AIV-SUITE-SPEC Section 7.2.
