# AIV Evidence File (v1.0)

**File:** `README.md`
**Commit:** `a99851d`
**Previous:** `6a0c403`
**Generated:** 2026-02-09T20:15:40Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R0
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "README.md"
  classification_rationale: "Documentation update for LLM readiness"
  classified_by: "ImmortalDemonGod"
  classified_at: "2026-02-09T20:15:40Z"
```

## Claim(s)

1. README now documents quickstart command in CLI Commands section
2. README flag table includes --skip-reason
3. README audit section documents EVIDENCE_UNVERIFIED_CLAIM, EVIDENCE_HIGH_UNVERIFIED, EVIDENCE_MANUAL_REVIEW
4. README explains claim verification gate blocking behavior with no --force bypass
5. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/aiv-protocol/blob/a99851d25b5d562f6b0fbd8f1c8b7fac74bee937/docs/CLAIM_AWARE_EVIDENCE_PLAN.md](https://github.com/ImmortalDemonGod/aiv-protocol/blob/a99851d25b5d562f6b0fbd8f1c8b7fac74bee937/docs/CLAIM_AWARE_EVIDENCE_PLAN.md)
- **Requirements Verified:** README must be complete enough for an LLM to use AIV correctly given only the README

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`a99851d`](https://github.com/ImmortalDemonGod/aiv-protocol/tree/a99851d25b5d562f6b0fbd8f1c8b7fac74bee937))

- [`README.md#L193`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/a99851d25b5d562f6b0fbd8f1c8b7fac74bee937/README.md#L193)
- [`README.md#L196-L207`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/a99851d25b5d562f6b0fbd8f1c8b7fac74bee937/README.md#L196-L207)
- [`README.md#L284-L291`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/a99851d25b5d562f6b0fbd8f1c8b7fac74bee937/README.md#L284-L291)
- [`README.md#L343`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/a99851d25b5d562f6b0fbd8f1c8b7fac74bee937/README.md#L343)
- [`README.md#L349-L351`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/a99851d25b5d562f6b0fbd8f1c8b7fac74bee937/README.md#L349-L351)
- [`README.md#L606`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/a99851d25b5d562f6b0fbd8f1c8b7fac74bee937/README.md#L606)

### Class A (Execution Evidence)

- Local checks skipped (--skip-checks).
- **Skip reason:** Documentation only: adding missing CLI command docs, flag reference, gate explanation


---

## Verification Methodology

**R0 (trivial) -- local checks skipped.**
**Reason:** Documentation only: adding missing CLI command docs, flag reference, gate explanation
Only git diff scope inventory was collected. No execution evidence.

---

## Summary

Fix 5 README gaps: quickstart cmd, --skip-reason, audit checks, verification gate, test count
