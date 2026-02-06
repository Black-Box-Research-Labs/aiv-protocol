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
  classification_rationale: "Shared test fixtures providing valid/invalid packet samples and diff fixtures. R1 because all tests depend on these fixtures for correctness."
  classified_by: "cascade"
  classified_at: "2026-02-07T00:00:00Z"
```

## Claim(s)

1. `tests/conftest.py` provides 4 valid/invalid packet fixtures and 3 diff fixtures per AIV-SUITE-SPEC Section 10.1.
2. `valid_minimal_packet` — minimal packet with SHA-pinned Class E link, 1 claim, CI Automation reproduction.
3. `valid_full_packet` — comprehensive packet with Claims for Class A, B, and F evidence including justification.
4. `invalid_missing_header` — packet missing `# AIV Verification Packet` header.
5. `invalid_mutable_link` — packet with `/blob/main/` Class E link (mutable).
6. `invalid_manual_reproduction` — packet with Zero-Touch violation (git clone + npm install).
7. `diff_with_deleted_assertion` — diff removing an `assert` statement from a test file.
8. `diff_with_skip_decorator` — diff adding `@pytest.mark.skip` to a test.
9. `diff_clean` — diff with only source code additions, no anti-cheat violations.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** AIV-SUITE-SPEC-V1.0-CANONICAL Section 10.1 — Test Categories and fixtures specification.
- **Requirements Verified:**
  1. ✅ All fixture categories from spec Section 10.1

### Class B (Referential Evidence)

**Scope Inventory (required)**

- Created:
  - `tests/conftest.py` (~155 lines)

### Class A (Execution Evidence)

- N/A — fixtures are exercised by test files.

---

## Summary

Shared test fixtures for valid/invalid packets and diff scenarios per AIV-SUITE-SPEC Section 10.1.
