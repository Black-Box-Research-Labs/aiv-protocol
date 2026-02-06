# AIV Verification Packet (v2.1)

**Commit:** `pending`  
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R2
  sod_mode: S0
  critical_surfaces: []
  blast_radius: component
  classification_rationale: "Core Pydantic data models used by every component in the AIV Protocol Suite — parser, validators, CLI, guard. R2 due to broad blast radius: all downstream components depend on these types."
  classified_by: "cascade"
  classified_at: "2026-02-06T22:35:00Z"
```

## Claim(s)

1. `src/aiv/lib/models.py` implements all 12 core data models specified in AIV-SUITE-SPEC Section 4.1: EvidenceClass, Severity, ValidationStatus, ArtifactLink, Claim, IntentSection, VerificationPacket, ValidationFinding, ValidationResult, AntiCheatFinding, AntiCheatResult, FrictionScore.
2. All models are immutable (frozen=True via Pydantic ConfigDict) to ensure validation integrity per spec Section 4.1.
3. `EvidenceClass` enum maps A-F to the six evidence classes with a flexible `from_string()` parser accepting "A", "Class A", "A (Execution)" etc.
4. `ArtifactLink.from_url()` implements immutability detection: SHA-pinned GitHub blob/tree links (7+ hex chars), Actions run IDs (always immutable), mutable branch detection (main/master/develop/staging/trunk/dev/HEAD).
5. `ValidationFinding` uses rule_id pattern `^E\d{3}$` matching the E001-E015 validation rules matrix from spec Section 2.3.
6. No regressions — this is a new file with no prior implementation.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** AIV-SUITE-SPEC-V1.0-CANONICAL Section 4.1 — Core Models specification with complete Pydantic model definitions.
- **Requirements Verified:**
  1. ✅ All 12 models from spec Section 4.1 implemented
  2. ✅ Frozen (immutable) models per spec requirement
  3. ✅ EvidenceClass enum with A-F mapping
  4. ✅ ArtifactLink immutability detection per Addendum 2.2
  5. ✅ ValidationFinding rule_id pattern per spec Section 2.3

### Class B (Referential Evidence)

**Scope Inventory (required)**

- Created:
  - `src/aiv/lib/models.py` (~310 lines)

**Claim 1: Core model classes**
- Lines 25-60: `EvidenceClass` enum with A-F mapping and `from_string()` parser
- Lines 63-67: `Severity` enum (BLOCK/WARN/INFO)
- Lines 70-74: `ValidationStatus` enum (PASS/FAIL/WARN)
- Lines 77-173: `ArtifactLink` with `from_url()` immutability detection
- Lines 176-200: `Claim` model with evidence fields
- Lines 203-215: `IntentSection` model
- Lines 218-248: `VerificationPacket` model with computed properties
- Lines 251-266: `ValidationFinding` model
- Lines 269-295: `ValidationResult` model with computed properties
- Lines 298-318: `AntiCheatFinding` and `AntiCheatResult` models
- Lines 321-330: `FrictionScore` model

### Class A (Execution Evidence)

- N/A for initial commit — models will be validated when tests are added in Phase 11.

### Class C (Negative Evidence — Conservation)

- No existing models.py was present; this is a new file. No regressions possible.
- No test files modified.

---

## Verification Methodology

Visual inspection of Pydantic model definitions against AIV-SUITE-SPEC-V1.0-CANONICAL Section 4.1 code blocks.

---

## Summary

All 12 core Pydantic v2 data models implemented per AIV-SUITE-SPEC Section 4.1, with immutable (frozen) configuration, evidence class enum, artifact link immutability detection, and validation result types.
