# AIV Verification Packet (v2.1)

**Commit:** `5aa0e0f`
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R0
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "src/aiv/cli/main.py"
  classification_rationale: "Help text and docstring improvements only — no logic, validation, or behavior changes"
  classified_by: "ImmortalDemonGod"
  classified_at: "2026-02-09T04:53:16Z"
```

## Claim(s)

1. `aiv commit --help` displays REQUIRED prefix and inline examples for all mandatory flags (--claim, --intent, --requirement, --rationale, --summary).
2. `aiv commit --help` docstring example includes the --requirement flag that was previously missing.
3. Unicode em-dash characters in help text are replaced with ASCII equivalents to prevent Windows cp1252 encoding crashes.
4. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [SPECIFICATION.md](https://github.com/ImmortalDemonGod/aiv-protocol/blob/5aa0e0f06bb0396aa56be0664e69fcff0210a51f/SPECIFICATION.md)
- **Requirements Verified:**
  1. CLI must be self-documenting so that an LLM or new user can operate it from --help output alone.

### Class B (Referential Evidence)

**Scope Inventory**

- Modified: `src/aiv/cli/main.py` — help text strings and docstring only

### Class A (Execution Evidence)

- pytest: 621 passed, 0 failed in 41.59s
- `aiv commit --help` renders cleanly on Windows without cp1252 crash

---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Verified by running `python -m aiv commit --help` on Windows and confirming clean rendering.
621 tests pass with no regressions.

---

## Summary

Improve aiv commit CLI help text with REQUIRED markers, inline examples, and Windows cp1252 encoding fix.
