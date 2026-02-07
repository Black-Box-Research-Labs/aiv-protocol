# AIV Verification Packet (v2.1)

## Classification

- **Risk Tier:** R2
- **Blast Radius:** component
- **SoD Mode:** S1

## Claim(s)

1. SVP validator enforces S015 (AI traces must have verified_output) and S016 (AI falsification scenarios must have test_code), both gated by session_type == ai_adversarial_triage.

## Evidence

### Class E (Intent Alignment)

- **Link:** [Strategic Analysis](https://github.com/ImmortalDemonGod/aiv-protocol/blob/6372a90/.svp/AI_FIRST_PASS_STRATEGIC_ANALYSIS.md)
- **Requirements Verified:**
  1. S015 BLOCKs AI sessions without verified_output on any trace.
  2. S016 BLOCKs AI sessions with prose-only falsification scenarios.
  3. Human sessions are unaffected by S015/S016.

### Class B (Referential Evidence)

**Scope Inventory**
- Modified: src/aiv/svp/lib/validators/session.py

### Class A (Execution Evidence)

- 384 tests pass. S015 and S016 each tested with AI session blocked + AI session passing + human session unaffected.

## Summary

Validator rules that enforce the "Honest AI Protocol" — AI verifiers cannot submit mental traces or prose falsification scenarios.
