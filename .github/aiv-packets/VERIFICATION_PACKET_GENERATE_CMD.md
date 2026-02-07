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
  classification_rationale: "New CLI command 'aiv generate' scaffolds verification packets with tier-appropriate evidence sections, auto-detected git scope inventory, and pre-filled classification YAML. No existing behavior modified."
  classified_by: "cascade"
  classified_at: "2026-02-07T00:25:00Z"
```

## Claim(s)

1. New `aiv generate <name>` command creates a pre-filled verification packet scaffold with classification YAML, claim stubs, and evidence section headers appropriate for the chosen risk tier (R0-R3).
2. Generator auto-detects changed files from `git diff --cached` (staged) or `git diff` (unstaged) and populates the Class B scope inventory.
3. Evidence sections are tier-aware: R0 gets A+B, R1 adds E, R2 adds C+F, R3 adds D.
4. No existing tests were modified or deleted — 84/84 tests pass.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** AUDIT_REPORT.md — §7.5 P3: "`aiv generate` command for packet scaffolding."
- **Requirements Verified:**
  1. ✅ Command creates properly structured packet file
  2. ✅ Tier-specific evidence sections generated
  3. ✅ Git scope auto-detection works

### Class B (Referential Evidence)

**Scope Inventory (required)**

- Modified:
  - `src/aiv/cli/main.py` — added `generate` command, `_detect_git_scope()`, `_build_evidence_sections()` functions

### Class A (Execution Evidence)

- 84/84 pytest tests pass (no regressions)
- Manual test: `aiv generate test-feature --tier R2 --rationale "Test"` produces correct scaffold

### Class F (Conservation Evidence)

**Claim 4: No regressions**
- No test files modified or deleted. Full test suite passes.

---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.

---

## Summary

Implements `aiv generate` command for verification packet scaffolding with tier-aware evidence sections and git scope auto-detection. Audit roadmap §7.5 P3.
