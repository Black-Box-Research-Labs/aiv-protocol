# AIV Verification Packet (v2.1)

**Commit:** `pending`  
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: component
  classification_rationale: "Diff analyzer providing file-level statistics and critical surface detection from unified diffs. R1 because it informs risk tier classification and scope inventory validation."
  classified_by: "cascade"
  classified_at: "2026-02-06T23:55:00Z"
```

## Claim(s)

1. `src/aiv/lib/analyzers/diff.py` implements `DiffAnalyzer` per AIV-SUITE-SPEC Section 3.3 with unified diff parsing and critical surface detection.
2. Parses unified diffs into `DiffAnalysis` with per-file statistics (additions, deletions, status: added/modified/deleted/renamed).
3. `detect_critical_surfaces()` matches file paths and diff content against 6 critical surface patterns: authentication, cryptography, payments, PII, audit-logging, secrets.
4. `DiffAnalysis` provides computed properties for filtering by file status (added_files, modified_files, deleted_files).

---

## Evidence

### Class E (Intent Alignment)

- **Link:** AIV-SUITE-SPEC-V1.0-CANONICAL Section 3.3 — specifies `src/aiv/lib/analyzers/diff.py`.
- **Requirements Verified:**
  1. ✅ Diff parsing with file-level statistics
  2. ✅ Critical surface auto-detection per aiv-guard threat model

### Class B (Referential Evidence)

**Scope Inventory (required)**

- Created:
  - `src/aiv/lib/analyzers/diff.py` (~160 lines)

### Class A (Execution Evidence)

- N/A for initial commit.

---

## Summary

Diff analyzer with unified diff parsing and critical surface detection per AIV-SUITE-SPEC Section 3.3.
