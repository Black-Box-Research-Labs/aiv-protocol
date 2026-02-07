# AIV Verification Packet (v2.1)

## Classification

```yaml
classification:
  risk_tier: R1
  blast_radius: tooling
  sod_mode: S0
```

## Claim(s)

1. Pre-commit hook tar step demoted from fatal to warning so commits are not blocked on Windows where tar may be unavailable.

## Evidence

### Class E (Intent Alignment)

- **Link:** [Hook source](https://github.com/ImmortalDemonGod/aiv-protocol/blob/e4cd50b0db2e41eeac38d80e8dddf6b0a2c60f07/.husky/pre-commit)
- **Requirements Verified:**
  1. Safety snapshot tar failure must not gate commits.

### Class B (Referential Evidence)

**Scope Inventory**
- Modified: .husky/pre-commit

### Class A (Execution Evidence)

- Hook now prints WARN instead of exiting 1 when tar fails.
- Atomicity rules (Rules 1-6) are unaffected.

## Summary

Single-line fix: `exit 1` changed to no-op inside the tar failure handler. The safety snapshot is best-effort, not a gating requirement.
