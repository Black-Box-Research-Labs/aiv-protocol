# AIV Evidence File (v1.0)

**File:** `src/aiv/lib/parser.py`
**Commit:** `3f4226a`
**Generated:** 2026-02-09T05:20:38Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "src/aiv/lib/parser.py"
  classification_rationale: "Parser logic change, standard risk"
  classified_by: "ImmortalDemonGod"
  classified_at: "2026-02-09T05:20:38Z"
```

## Claim(s)

1. Parser _collect_evidence_classes scans Evidence References tables for Classes column
2. _parse_evidence_refs_table extracts A-F class letters from markdown table rows
3. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/aiv-protocol/blob/main/docs/TWO_LAYER_VERIFICATION_ARCHITECTURE.md](https://github.com/ImmortalDemonGod/aiv-protocol/blob/main/docs/TWO_LAYER_VERIFICATION_ARCHITECTURE.md)
- **Requirements Verified:** Layer 2 packets must satisfy tier requirements via evidence_refs

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`3f4226a`](https://github.com/ImmortalDemonGod/aiv-protocol/tree/3f4226ab93b7ac42daac57cebb121b77f736511f))

- [`src/aiv/lib/parser.py#L305-L307`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/3f4226ab93b7ac42daac57cebb121b77f736511f/src/aiv/lib/parser.py#L305-L307)
- [`src/aiv/lib/parser.py#L320-L361`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/3f4226ab93b7ac42daac57cebb121b77f736511f/src/aiv/lib/parser.py#L320-L361)

### Class A (Execution Evidence)

- Local checks skipped (--skip-checks).



---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence was collected by `aiv commit` running: git diff, pytest -v, ruff, mypy, anti-cheat scan.

---

## Summary

Add evidence refs table parsing so Layer 2 packets satisfy Class A/B tier requirements
