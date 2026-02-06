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
  classification_rationale: "Protocol exception handlers for bootstrap, flake, and fast-track cases per Addendum 2.3. R1 because they modify validation strictness for specific edge cases."
  classified_by: "cascade"
  classified_at: "2026-02-06T23:15:00Z"
```

## Claim(s)

1. `src/aiv/lib/validators/exceptions.py` implements 3 exception handlers per AIV-SUITE-SPEC Section 9: BootstrapExceptionHandler, FlakeReportHandler, FastTrackHandler.
2. BootstrapExceptionHandler detects infrastructure PRs via file patterns (Dockerfile, Terraform, etc.) and validates single-command reproducibility.
3. FlakeReportHandler requires 3 CI run URLs to prove flakiness (rule E014).
4. FastTrackHandler detects docs-only changes eligible for simplified evidence requirements per Addendum 2.3.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** AIV-SUITE-SPEC-V1.0-CANONICAL Section 9 — Edge Case Handling specification.
- **Requirements Verified:**
  1. ✅ Bootstrap exception per Section 9.1
  2. ✅ Flake report per Section 9.1
  3. ✅ Fast-track per Addendum 2.3

### Class B (Referential Evidence)

**Scope Inventory (required)**

- Created:
  - `src/aiv/lib/validators/exceptions.py` (~200 lines)

### Class A (Execution Evidence)

- N/A for initial commit.

---

## Summary

Protocol exception handlers for bootstrap, flake, and fast-track edge cases per AIV-SUITE-SPEC Section 9.
