# AIV Evidence File (v1.0)

**File:** `pyproject.toml`
**Commit:** `e83b26d`
**Previous:** `8903a45`
**Generated:** 2026-02-10T20:46:22Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "pyproject.toml"
  classification_rationale: "R1: new optional dependency group"
  classified_by: "Miguel Ingram"
  classified_at: "2026-02-10T20:46:22Z"
```

## Claim(s)

1. Added [polyglot] optional dep group with tree-sitter, tree-sitter-javascript, tree-sitter-typescript; also added to [dev] group
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/aiv-protocol/blob/e83b26d77b592ae024f7b5f57c8230cffa78a1eb/docs/EXTERNAL_READINESS_AUDIT.md](https://github.com/ImmortalDemonGod/aiv-protocol/blob/e83b26d77b592ae024f7b5f57c8230cffa78a1eb/docs/EXTERNAL_READINESS_AUDIT.md)
- **Requirements Verified:** P1-6: polyglot symbol resolution requires tree-sitter grammars

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`e83b26d`](https://github.com/ImmortalDemonGod/aiv-protocol/tree/e83b26d77b592ae024f7b5f57c8230cffa78a1eb))

- [`pyproject.toml#L37-L41`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/e83b26d77b592ae024f7b5f57c8230cffa78a1eb/pyproject.toml#L37-L41)
- [`pyproject.toml#L49-L51`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/e83b26d77b592ae024f7b5f57c8230cffa78a1eb/pyproject.toml#L49-L51)
- [`pyproject.toml#L88-L91`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/e83b26d77b592ae024f7b5f57c8230cffa78a1eb/pyproject.toml#L88-L91)

### Class A (Execution Evidence)

**WARNING:** No tests found that directly import or reference the changed file.
This file has no claim-specific execution evidence.

### Code Quality (Linting & Types)

- **ruff:** All checks passed
- **mypy:** Found 1 error in 1 file (errors prevented further checking)

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | Added [polyglot] optional dep group with tree-sitter, tree-s... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 2 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), pytest (no claim-specific tests found).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

pyproject.toml
