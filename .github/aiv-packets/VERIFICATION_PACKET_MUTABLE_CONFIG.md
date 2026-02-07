# AIV Verification Packet (v2.1)

**Commit:** `1b22fc5`  
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: component
  classification_rationale: "Plumbs MutableBranchConfig through to ArtifactLink.from_url() so mutable branch set and min SHA length are configurable instead of hardcoded. Audit finding L08."
  classified_by: "cascade"
  classified_at: "2026-02-07T00:00:00Z"
```

## Claim(s)

1. `ArtifactLink.from_url()` now accepts optional `mutable_branches` and `min_sha_length` parameters, using configurable values instead of hardcoded sets.
2. `LinkValidator.validate_packet_links()` now re-checks blob/tree links using `MutableBranchConfig.mutable_branches` and `min_sha_length` from its config, making the config actually effective.
3. No existing tests were modified or deleted — 39/39 tests pass.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [AUDIT_REPORT.md — Finding L08: "Mutable branch set is hardcoded in model AND defined in config, but config is never consulted."](https://github.com/ImmortalDemonGod/aiv-protocol/blob/1b22fc5/AUDIT_REPORT.md)
- **Requirements Verified:**
  1. ✅ from_url() accepts configurable mutable_branches and min_sha_length
  2. ✅ LinkValidator uses its MutableBranchConfig when checking blob links
  3. ✅ Default behavior preserved (same hardcoded set used when no config provided)

### Class B (Referential Evidence)

**Scope Inventory (required)**

- Modified:
  - `src/aiv/lib/models.py` — lines 91-97: added mutable_branches/min_sha_length params to from_url(); lines 134-146: use params instead of hardcoded values
  - `src/aiv/lib/validators/links.py` — lines 78-98: re-check blob links with configured mutable branches

### Class A (Execution Evidence)

- 39/39 pytest tests pass (no regressions)

### Class F (Conservation Evidence)

**Claim 3: No regressions**
- No test files modified or deleted. Full test suite passes.

---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.

---

## Summary

Plumbs MutableBranchConfig through to ArtifactLink.from_url() so mutable branch checking is configurable. Audit finding L08.
