# AIV Verification Packet (v2.1)

**Commit:** `779b9d2`  
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R2
  sod_mode: S1
  critical_surfaces: []
  blast_radius: service
  classification_rationale: "Refactors the 2244-line inline JS aiv-guard.yml into a clean Python module (src/aiv/guard/) backed by aiv-lib. This is a service-level change affecting CI enforcement infrastructure. The original JS workflow is preserved as-is; a new Python-based workflow is added alongside it."
  classified_by: "cascade"
  classified_at: "2026-02-07T00:45:00Z"
```

## Claim(s)

1. Created `src/aiv/guard/` module with 5 files: models.py (data models + regex helpers), github_api.py (GitHub REST API wrapper), canonical.py (canonical JSON validator), manifest.py (evidence artifact manifest validators), runner.py (main orchestrator).
2. The Python guard replicates all validation logic from the JS guard: packet resolution, markdown validation via aiv-lib pipeline, canonical JSON field validation, SHA matching, risk tier enforcement, SoD checks, attestation validation, scope inventory matching, immutability enforcement, critical surface detection, Class A CI run verification, and evidence class results.
3. Created `.github/workflows/aiv-guard-python.yml` — a 45-line workflow replacing 2244 lines of inline JS with `python -m aiv.guard`.
4. Added 36 unit tests covering guard models, regex patterns, canonical validation, manifest validation, and runner orchestration with mocked API.
5. No existing code or tests were modified or deleted — 120/120 tests pass.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [AUDIT_REPORT.md — §7.5 P2: "Guard refactor (JS → Python)"](https://github.com/ImmortalDemonGod/aiv-protocol/blob/779b9d2/AUDIT_REPORT.md)
- **Requirements Verified:**
  1. ✅ All JS validation logic ported to Python
  2. ✅ Uses aiv-lib pipeline for markdown validation
  3. ✅ Produces identical aiv_validation_result.json output format

### Class B (Referential Evidence)

**Scope Inventory (required)**

- Created:
  - `src/aiv/guard/models.py` — Guard data models, finding types, regex patterns
  - `src/aiv/guard/github_api.py` — GitHub REST API wrapper (urllib-based, no deps)
  - `src/aiv/guard/canonical.py` — Canonical JSON packet validator
  - `src/aiv/guard/manifest.py` — Evidence artifact manifest validators
  - `src/aiv/guard/runner.py` — Main guard orchestrator (GuardRunner class)
  - `src/aiv/guard/__main__.py` — python -m aiv.guard entry point
  - `.github/workflows/aiv-guard-python.yml` — New Python-based workflow
  - `tests/unit/test_guard.py` — 36 unit tests
- Modified:
  - `src/aiv/guard/__init__.py` — Added public API exports

### Class A (Execution Evidence)

- 120/120 pytest tests pass (84 existing + 36 new guard tests)
- Guard module imports successfully: `from aiv.guard import GuardRunner`

### Class C (Negative Evidence)

- Original `aiv-guard.yml` (JS) preserved unchanged — no regression risk
- No existing tests modified or deleted
- All 25 real verification packets still pass strict validation

### Class F (Conservation Evidence)

**Claim 5: No regressions**
- No test files modified or deleted. Full test suite passes (120/120).

---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.

---

## Summary

Refactors 2244-line JS aiv-guard.yml into clean Python `src/aiv/guard/` module (5 files, ~750 lines) backed by aiv-lib pipeline. 36 new tests. §7.5 P2 complete.
