# AIV Verification Packet (v2.1)

**Commit:** `pending`  
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R0
  sod_mode: S0
  critical_surfaces: []
  blast_radius: local
  classification_rationale: "PR template defining the standard PR body format. Documentation-only — no runtime effect. Instructs PR authors to reference their verification packet source file."
  classified_by: "cascade"
  classified_at: "2026-02-06T22:08:00Z"
```

## Claim(s)

1. `.github/PULL_REQUEST_TEMPLATE.md` provides a standard PR body template that includes the `Packet Source:` pointer and an executive summary section.
2. No runtime or behavioral effect.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** AIV Sovereign Packet Source convention — PR bodies contain a pointer to the packet file, not the full packet.
- **Requirements Verified:**
  1. ✅ Template includes `Packet Source:` line pointing to `.github/aiv-packets/`
  2. ✅ Template includes executive summary section

### Class B (Referential Evidence)

**Scope Inventory (required)**

- Created:
  - `.github/PULL_REQUEST_TEMPLATE.md` (6 lines)

### Class A (Execution Evidence)

- N/A — markdown template, no execution required.

---

## Verification Methodology

Visual inspection of template content.

---

## Summary

Standard PR template with AIV packet source pointer.
