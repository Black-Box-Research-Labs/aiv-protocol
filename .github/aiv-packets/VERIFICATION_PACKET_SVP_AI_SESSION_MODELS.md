# AIV Verification Packet (v2.1)

## Classification

- **Risk Tier:** R2
- **Blast Radius:** component
- **SoD Mode:** S1

## Claim(s)

1. SVP models add SessionType enum (human_verification vs ai_adversarial_triage), verified_output field on TraceRecord (S015), and test_code field on FalsificationScenario (S016) to bifurcate AI and human verification paths.

## Evidence

### Class E (Intent Alignment)

- **Link:** [Strategic Analysis](https://github.com/ImmortalDemonGod/aiv-protocol/blob/6372a90/.svp/AI_FIRST_PASS_STRATEGIC_ANALYSIS.md)
- **Requirements Verified:**
  1. AI sessions must provide execution evidence (not mental simulation).
  2. AI falsification scenarios must be code, not prose.
  3. Session type distinguishes human verification from AI adversarial triage.

### Class B (Referential Evidence)

**Scope Inventory**
- Modified: src/aiv/svp/lib/models.py

### Class A (Execution Evidence)

- 384 tests pass after change. SessionType enum serializes correctly.
- TraceRecord accepts verified_output field. FalsificationScenario accepts test_code field.
- SVPSession defaults to human_verification, backwards-compatible.

## Summary

Model-layer changes for the "Honest AI Protocol" redesign. Adds fields that S015/S016 validator rules will enforce for AI sessions.
