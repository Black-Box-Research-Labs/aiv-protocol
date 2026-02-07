# AIV Verification Packet (v2.1)

## Classification

```yaml
classification:
  risk_tier: R0
  blast_radius: local
  sod_mode: S0
  critical_surfaces: []
  classification_rationale: "Adds --audit-links flag to aiv check CLI command and passes it to ValidationPipeline. Two lines changed."
  classified_by: "cascade-ai"
  classified_at: "2026-02-07T08:04:00Z"
```

## Claim(s)

1. `aiv check --audit-links` enables E021 link vitality checking, forwarding the flag through `ValidationPipeline` to `LinkValidator`.

## Evidence

### Class E (Intent Alignment)

- **Directive:** Required to expose the E021 link vitality feature to end users via the CLI.

### Class B (Referential Evidence)

**Scope Inventory**
- Modified: `src/aiv/cli/main.py` — added `audit_links` parameter to `check()` and passed it to `ValidationPipeline()`.

### Class A (Execution Evidence)

- 436/436 tests pass unchanged.

## Summary

Exposes `--audit-links` flag on `aiv check` CLI command.
