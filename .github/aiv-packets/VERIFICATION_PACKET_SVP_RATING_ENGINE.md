# AIV Verification Packet (v2.1)

## Classification

```yaml
classification:
  risk_tier: R2
  blast_radius: component
  sod_mode: S1
```

## Claim(s)

1. SVP rating engine automatically calculates ELO scores from session data by scoring confirmed bugs, falsified scenarios, ownership quality, and session completion per RATING_POINTS map.

## Evidence

### Class E (Intent Alignment)

- **Link:** [SVP Spec §9 Verifier Rating System](https://github.com/ImmortalDemonGod/aiv-protocol/blob/067ff2c/docs/specs/SVP-SUITE-SPEC-V1.0-CANONICAL-2025-12-20.md)
- **Requirements Verified:**
  1. score_session() generates RatingEvents from SVPSession probe findings.
  2. calculate_rating() aggregates events across sessions into VerifierRating.
  3. Persistence via load_ratings()/save_ratings() to .svp/ratings.json.

### Class B (Referential Evidence)

**Scope Inventory**
- New: src/aiv/svp/lib/rating.py

### Class A (Execution Evidence)

- `aiv svp rating cascade-ai-first-pass --verbose` produces ELO 635, COMPETENT tier, 7 bugs caught.
- 410 tests pass including 12 new rating engine tests.

### Class C (Negative Evidence)

- Unconfirmed findings (is_confirmed_bug=False) produce zero rating events — verified by test.
- Unchecked falsification scenarios produce zero events — verified by test.
- Sessions from other verifiers are filtered out — verified by test.

## Summary

Implements svp-rating component per spec §9. Automated ELO calculation replaces manual scoring.
