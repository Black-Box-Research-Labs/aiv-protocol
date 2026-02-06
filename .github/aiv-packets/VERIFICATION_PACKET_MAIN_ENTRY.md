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
  classification_rationale: "New __main__.py entry point enabling `python -m aiv` execution. 5-line delegation file with no logic — only imports and calls existing app()."
  classified_by: "cascade"
  classified_at: "2026-02-06T23:39:00Z"
```

## Claim(s)

1. `src/aiv/__main__.py` enables running the aiv package as `python -m aiv`, delegating to `aiv.cli.main:app`.
2. No existing behavior is modified — this is a new file that fills a missing entry point.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** AIV Protocol Suite — CLI must be invocable via `python -m aiv` for development and CI use without requiring the `aiv` console script to be on PATH.
- **Requirements Verified:**
  1. ✅ `python -m aiv` now invokes the Typer CLI app
  2. ✅ `python -m aiv check <packet>` works end-to-end

### Class B (Referential Evidence)

**Scope Inventory (required)**

- Created:
  - `src/aiv/__main__.py`

### Class A (Execution Evidence)

- 39/39 pytest tests pass after addition (no regressions)
- `python -m aiv check` successfully validates all 6 real packets in `.github/aiv-packets/`
- Prior to this file, `python -m aiv` failed with: `No module named aiv.__main__`

---

## Verification Methodology

```bash
python -m pytest tests/ -v --tb=short
python -m aiv check .github/aiv-packets/VERIFICATION_PACKET_PRECOMMIT.md
```

---

## Summary

Adds missing `__main__.py` to enable `python -m aiv` CLI invocation. Pure delegation file, no logic.
