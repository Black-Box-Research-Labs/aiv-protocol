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
  classification_rationale: "Implements Classification YAML parsing and risk-tier evidence enforcement (§4.4.3, §5.1, §6.1). New RiskTier enum, parser extraction, and pipeline enforcement stage. Affects validation behavior for all packets with classification sections."
  classified_by: "cascade"
  classified_at: "2026-02-07T00:00:00Z"
```

## Claim(s)

1. New `RiskTier` enum (R0-R3) added to models.py with `from_string()` parser.
2. Parser now extracts `risk_tier` from `## Classification (required)` YAML code block using regex (no PyYAML dependency needed).
3. Parser collects all evidence classes present in `### Class X` sections via `_collect_evidence_classes()` and stores them in `VerificationPacket.evidence_classes_present`.
4. Pipeline enforces evidence class requirements per tier: A+B for R0, +E for R1, +C for R2, +D+F for R3. Missing required classes produce E014 BLOCK findings.
5. Missing classification section produces E014 WARN (graceful degradation for older packets).
6. No existing tests were modified or deleted — 39/39 tests pass, all 20+ real packets pass strict mode.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** AUDIT_REPORT.md — §4.4.3: "Classification YAML block is present in all real packets but completely ignored by the parser."
- **Requirements Verified:**
  1. ✅ Parser extracts risk_tier from YAML
  2. ✅ Pipeline enforces tier-specific evidence requirements
  3. ✅ Graceful degradation for packets without classification

### Class B (Referential Evidence)

**Scope Inventory (required)**

- Modified:
  - `src/aiv/lib/models.py` — added `RiskTier` enum, `risk_tier` and `evidence_classes_present` fields to `VerificationPacket`
  - `src/aiv/lib/parser.py` — added `_parse_classification()`, `_collect_evidence_classes()` methods; wired into `parse()`
  - `src/aiv/lib/validators/pipeline.py` — added `_TIER_REQUIRED`, `_TIER_OPTIONAL` dicts and `_check_tier_requirements()` method; new Stage 5

### Class A (Execution Evidence)

- 39/39 pytest tests pass (no regressions)
- All real packets pass strict mode validation

### Class C (Negative Evidence)

- No pre-existing classification enforcement existed. This is entirely new functionality — no regressions possible from the enforcement logic itself.

### Class F (Conservation Evidence)

**Claim 6: No regressions**
- No test files modified or deleted. Full test suite passes.

---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.

---

## Summary

Implements Classification YAML parsing and risk-tier evidence enforcement per §5.1 and §6.1 of the AIV specification. Audit finding §4.4.3.
