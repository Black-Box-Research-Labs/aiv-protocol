# AIV Verification Packet (v2.1)

## Classification

```yaml
classification:
  risk_tier: R1
  blast_radius: tooling
  sod_mode: S0
  critical_surfaces: []
  classification_rationale: "Pre-commit hook enhancement — adds aiv audit as a second validation gate after aiv check. Catches quality issues (CLASSIFIED_BY_TODO, COMMIT_PENDING, FIX_NO_CLASS_F) that the pipeline validator does not cover. No runtime code changes."
  classified_by: "cascade-ai"
  classified_at: "2026-02-07T07:35:00Z"
```

## Claim(s)

1. The pre-commit hook now runs `aiv audit` on the staged packet after `aiv check` passes, blocking commits when audit-level errors are found (e.g., CLASSIFIED_BY_TODO, COMMIT_PENDING, FIX_NO_CLASS_F).
2. Packets that pass `aiv check` but fail `aiv audit` with errors are blocked; audit warnings do not block.
3. The staged packet is copied to a temp directory with its real filename so `aiv audit` can scan it using its existing directory-based interface.

## Evidence

### Class E (Intent Alignment)

- **Directive:** Investigation of FILE_PACKET_MAP revealed 4 packets committed with FIX_NO_CLASS_F errors. Root cause: pre-commit hook ran `aiv check` (pipeline validator) but not `aiv audit` (quality auditor). This change closes that gap.

### Class B (Referential Evidence)

**Scope Inventory**
- Modified: `.husky/pre-commit` — added audit step after line 173 (after `aiv check` block), ~25 new lines.

### Class A (Execution Evidence)

- **Test 1 (audit blocks CLASSIFIED_BY_TODO):** Created a packet whose `classified_by` field was still a placeholder. `aiv check` passed (exit 0) but the pre-commit hook blocked the commit with `PACKET AUDIT FAILED` showing the CLASSIFIED_BY_TODO error.
- **Test 2 (aiv check still blocks structural errors):** Created a packet with missing Class F on a bug-fix claim. Pre-commit hook blocked with `PACKET VALIDATION FAILED` showing E010 before audit even ran.
- All 426 existing tests continue to pass.

### Class F (Provenance)

- The `aiv check` flow is preserved unchanged — only an additional audit step is appended after it.
- The early-return on `aiv check` warnings was changed to a fall-through (`:`) so the audit step also runs on warning-only packets.

## Summary

Closes the gap between `aiv check` (structural validation) and `aiv audit` (quality auditing) in the pre-commit hook. Packets must now pass both gates to be committed.
