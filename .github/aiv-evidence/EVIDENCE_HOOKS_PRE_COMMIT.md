# AIV Evidence File (v1.0)

**File:** `src/aiv/hooks/pre_commit.py`
**Commit:** `38c2c0c`
**Generated:** 2026-02-09T05:14:38Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R0
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "src/aiv/hooks/pre_commit.py"
  classification_rationale: "Hook logic changes, standard enforcement layer"
  classified_by: "ImmortalDemonGod"
  classified_at: "2026-02-09T05:14:38Z"
```

## Claim(s)

1. Pre-commit hook allows multi-file commits when active change context exists
2. Evidence-only commits always pass without requiring a change context
3. Protected branch gate blocks functional files without change context or packet
4. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/aiv-protocol/blob/38c2c0cb07b6f8addbf74803d69f75e3642e13d6/docs/TWO_LAYER_VERIFICATION_ARCHITECTURE.md](https://github.com/ImmortalDemonGod/aiv-protocol/blob/38c2c0cb07b6f8addbf74803d69f75e3642e13d6/docs/TWO_LAYER_VERIFICATION_ARCHITECTURE.md)
- **Requirements Verified:** Design doc section 8: Hook Behavior

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`38c2c0c`](https://github.com/ImmortalDemonGod/aiv-protocol/tree/38c2c0cb07b6f8addbf74803d69f75e3642e13d6))

- [`src/aiv/hooks/pre_commit.py#L38`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/38c2c0cb07b6f8addbf74803d69f75e3642e13d6/src/aiv/hooks/pre_commit.py#L38)
- [`src/aiv/hooks/pre_commit.py#L40`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/38c2c0cb07b6f8addbf74803d69f75e3642e13d6/src/aiv/hooks/pre_commit.py#L40)
- [`src/aiv/hooks/pre_commit.py#L119-L122`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/38c2c0cb07b6f8addbf74803d69f75e3642e13d6/src/aiv/hooks/pre_commit.py#L119-L122)
- [`src/aiv/hooks/pre_commit.py#L124`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/38c2c0cb07b6f8addbf74803d69f75e3642e13d6/src/aiv/hooks/pre_commit.py#L124)
- [`src/aiv/hooks/pre_commit.py#L300-L318`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/38c2c0cb07b6f8addbf74803d69f75e3642e13d6/src/aiv/hooks/pre_commit.py#L300-L318)
- [`src/aiv/hooks/pre_commit.py#L338`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/38c2c0cb07b6f8addbf74803d69f75e3642e13d6/src/aiv/hooks/pre_commit.py#L338)
- [`src/aiv/hooks/pre_commit.py#L347-L363`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/38c2c0cb07b6f8addbf74803d69f75e3642e13d6/src/aiv/hooks/pre_commit.py#L347-L363)
- [`src/aiv/hooks/pre_commit.py#L368-L372`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/38c2c0cb07b6f8addbf74803d69f75e3642e13d6/src/aiv/hooks/pre_commit.py#L368-L372)
- [`src/aiv/hooks/pre_commit.py#L403-L432`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/38c2c0cb07b6f8addbf74803d69f75e3642e13d6/src/aiv/hooks/pre_commit.py#L403-L432)
- [`src/aiv/hooks/pre_commit.py#L443`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/38c2c0cb07b6f8addbf74803d69f75e3642e13d6/src/aiv/hooks/pre_commit.py#L443)

### Class A (Execution Evidence)

- Local checks skipped (--skip-checks).
- **Skip reason:** Legacy evidence file; predates anti-theater gates.



---

## Verification Methodology

**R0 (trivial) -- local checks skipped.**
Legacy evidence file; predates anti-theater gates.
Only git diff scope inventory was collected. No execution evidence.

---

## Summary

Add change-context awareness: evidence recognition, active-change multi-file allowance, protected branch gate
