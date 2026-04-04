# AIV Evidence File (v1.0)

**File:** `src/aiv/lib/parser.py`
**Commit:** `49b3d8b`
**Previous:** `8903a45`
**Generated:** 2026-04-04T23:07:10Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "src/aiv/lib/parser.py"
  classification_rationale: "Isolated logic fix in parser evidence enrichment — no critical surfaces"
  classified_by: "Miguel Ingram"
  classified_at: "2026-04-04T23:07:10Z"
```

## Claim(s)

1. Unlinked evidence is consumed one-per-claim instead of applying the same artifact to every unenriched claim
2. Parser extracts Justification text from Class F evidence sections into claim.justification
3. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/Black-Box-Research-Labs/aiv-protocol/pull/8](https://github.com/Black-Box-Research-Labs/aiv-protocol/pull/8)
- **Requirements Verified:** Code audit CRITICAL-1: fix parser evidence mapping bug at line 561

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`49b3d8b`](https://github.com/ImmortalDemonGod/aiv-protocol/tree/49b3d8bbb606e426d7ccfb601f087339975facbc))

- [`src/aiv/lib/parser.py#L472-L477`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/49b3d8bbb606e426d7ccfb601f087339975facbc/src/aiv/lib/parser.py#L472-L477)
- [`src/aiv/lib/parser.py#L488-L495`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/49b3d8bbb606e426d7ccfb601f087339975facbc/src/aiv/lib/parser.py#L488-L495)
- [`src/aiv/lib/parser.py#L501-L504`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/49b3d8bbb606e426d7ccfb601f087339975facbc/src/aiv/lib/parser.py#L501-L504)
- [`src/aiv/lib/parser.py#L506-L507`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/49b3d8bbb606e426d7ccfb601f087339975facbc/src/aiv/lib/parser.py#L506-L507)
- [`src/aiv/lib/parser.py#L525-L531`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/49b3d8bbb606e426d7ccfb601f087339975facbc/src/aiv/lib/parser.py#L525-L531)
- [`src/aiv/lib/parser.py#L556-L557`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/49b3d8bbb606e426d7ccfb601f087339975facbc/src/aiv/lib/parser.py#L556-L557)
- [`src/aiv/lib/parser.py#L559`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/49b3d8bbb606e426d7ccfb601f087339975facbc/src/aiv/lib/parser.py#L559)
- [`src/aiv/lib/parser.py#L563-L564`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/49b3d8bbb606e426d7ccfb601f087339975facbc/src/aiv/lib/parser.py#L563-L564)
- [`src/aiv/lib/parser.py#L575-L577`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/49b3d8bbb606e426d7ccfb601f087339975facbc/src/aiv/lib/parser.py#L575-L577)
- [`src/aiv/lib/parser.py#L594-L598`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/49b3d8bbb606e426d7ccfb601f087339975facbc/src/aiv/lib/parser.py#L594-L598)
- [`src/aiv/lib/parser.py#L600`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/49b3d8bbb606e426d7ccfb601f087339975facbc/src/aiv/lib/parser.py#L600)
- [`src/aiv/lib/parser.py#L602-L616`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/49b3d8bbb606e426d7ccfb601f087339975facbc/src/aiv/lib/parser.py#L602-L616)
- [`src/aiv/lib/parser.py#L626`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/49b3d8bbb606e426d7ccfb601f087339975facbc/src/aiv/lib/parser.py#L626)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`PacketParser`** (L472-L477): PASS -- 7 test(s) call `PacketParser` directly
  - `tests/unit/test_validators.py::test_unlinked_evidence_not_repeated_across_all_claims`
  - `tests/unit/test_validators.py::test_single_claim_single_unlinked_still_works`
  - `tests/unit/test_validators.py::test_justification_field_populated_from_class_f`
  - `tests/unit/test_validators.py::test_class_f_without_justification_marker_leaves_field_none`
  - `tests/integration/test_e2e_compliance.py::test_every_real_packet_parses_classification`
  - `tests/integration/test_e2e_compliance.py::test_todo_only_evidence_section_not_counted`
  - `tests/integration/test_e2e_compliance.py::test_generate_produces_parseable_packet`
- **`PacketParser._enrich_claims_with_evidence`** (L488-L495): FAIL -- WARNING: No tests import or call `_enrich_claims_with_evidence`

**Coverage summary:** 1/2 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** All checks passed
- **mypy:** Success: no issues found in 1 source file

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | Unlinked evidence is consumed one-per-claim instead of apply... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | Parser extracts Justification text from Class F evidence sec... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 3 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 0 unverified, 3 manual review.
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (1/2 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Fix unlinked evidence reuse and add Justification extraction
