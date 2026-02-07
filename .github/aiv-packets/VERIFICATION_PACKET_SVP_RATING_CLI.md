# AIV Verification Packet (v2.1)

## Classification

```yaml
classification:
  risk_tier: R1
  blast_radius: tooling
  sod_mode: S0
```

## Claim(s)

1. `svp rating` CLI command calculates and displays ELO rating for a verifier from all sessions, with verbose event log and persistence to .svp/ratings.json.

## Evidence

### Class E (Intent Alignment)

- **Link:** [SVP Spec §9](https://github.com/ImmortalDemonGod/aiv-protocol/blob/067ff2c/docs/specs/SVP-SUITE-SPEC-V1.0-CANONICAL-2025-12-20.md)
- **Requirements Verified:**
  1. CLI command displays ELO, tier, defects found, false positives.
  2. --verbose flag shows individual rating events with point values.
  3. Rating persisted to .svp/ratings.json by default.

### Class B (Referential Evidence)

**Scope Inventory**
- Modified: src/aiv/svp/cli/main.py

### Class A (Execution Evidence)

- `aiv svp rating cascade-ai-first-pass --verbose` runs successfully, outputs ELO 585.

## Summary

CLI integration for the rating engine. Exposes `svp rating <verifier-id>` with verbose and save options.
