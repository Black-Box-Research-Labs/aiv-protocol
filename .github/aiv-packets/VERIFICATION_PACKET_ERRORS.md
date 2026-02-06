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
  classification_rationale: "Exception hierarchy used by all aiv-lib components. R1 because downstream validators, parser, and CLI depend on these exception types for error handling."
  classified_by: "cascade"
  classified_at: "2026-02-06T22:28:00Z"
```

## Claim(s)

1. `src/aiv/lib/errors.py` defines 6 exception classes: AIVError (base), PacketParseError, PacketValidationError, ConfigurationError, GitHubAPIError, EvidenceResolutionError.
2. All exceptions inherit from `AIVError` enabling broad try/except catching.
3. `PacketValidationError` carries an optional `rule_id` for mapping to the E001-E015 rule matrix.
4. `GitHubAPIError` carries an optional `status_code` for HTTP error context.
5. `EvidenceResolutionError` carries an optional `url` for identifying broken evidence links.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** AIV-SUITE-SPEC-V1.0-CANONICAL Section 3.3 — specifies `src/aiv/lib/errors.py` in the repository structure.
- **Requirements Verified:**
  1. ✅ Exception hierarchy covers all failure modes: parsing, validation, config, API, evidence resolution
  2. ✅ Base class `AIVError` per spec

### Class B (Referential Evidence)

**Scope Inventory (required)**

- Created:
  - `src/aiv/lib/errors.py` (68 lines)

**Claim 1: Exception classes**
- Lines 11-13: `AIVError` base
- Lines 16-23: `PacketParseError`
- Lines 26-34: `PacketValidationError` with `rule_id`
- Lines 37-42: `ConfigurationError`
- Lines 45-53: `GitHubAPIError` with `status_code`
- Lines 56-65: `EvidenceResolutionError` with `url`

### Class A (Execution Evidence)

- N/A for initial commit — exceptions will be exercised by validators and parser.

---

## Summary

Exception hierarchy for aiv-lib covering all validation pipeline failure modes per AIV-SUITE-SPEC Section 3.3.
