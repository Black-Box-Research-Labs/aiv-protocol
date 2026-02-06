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
  classification_rationale: "Markdown packet parser converting PR body text into structured VerificationPacket objects. R2 because incorrect parsing would cause false positives/negatives in all downstream validation."
  classified_by: "cascade"
  classified_at: "2026-02-06T23:20:00Z"
```

## Claim(s)

1. `src/aiv/lib/parser.py` implements `PacketParser` per AIV-SUITE-SPEC Section 5.1 using regex-based section extraction.
2. Parses packet header with version detection (default v2.1), Intent section (Section 0) with Class E link and Verifier Check, and numbered claim sections.
3. Extracts evidence class, artifact (URL or text), reproduction instructions, and justification from each claim section.
4. Uses `ArtifactLink.from_url()` for URL artifacts to get immutability detection.
5. Reports parse errors as `ValidationFinding` objects with rule IDs (E002, E003, E006, E007) and raises `PacketParseError` for fatal failures (E001, missing intent, no claims).
6. No external AST dependency — uses regex heading detection to minimize dependency footprint.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** AIV-SUITE-SPEC-V1.0-CANONICAL Section 5.1 — Markdown Packet Parser specification.
- **Requirements Verified:**
  1. ✅ Header detection with version parsing
  2. ✅ Intent section parsing with Class E link extraction
  3. ✅ Claim section parsing with all field extraction
  4. ✅ Error reporting with rule IDs per spec Section 2.3

### Class B (Referential Evidence)

**Scope Inventory (required)**

- Created:
  - `src/aiv/lib/parser.py` (~300 lines)

### Class A (Execution Evidence)

- N/A for initial commit — parser will be validated when tests are added.

### Class C (Negative Evidence — Conservation)

- No existing parser was present; this is a new file. No regressions possible.

---

## Summary

Markdown packet parser with regex-based section extraction, intent/claim parsing, and structured error reporting per AIV-SUITE-SPEC Section 5.1.
