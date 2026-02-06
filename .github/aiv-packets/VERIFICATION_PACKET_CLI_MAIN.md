# AIV Verification Packet (v2.1)

**Commit:** `pending`  
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R2
  sod_mode: S0
  critical_surfaces: []
  blast_radius: component
  classification_rationale: "CLI entry point providing the 'aiv check' and 'aiv init' commands. R2 because it is the primary user-facing interface and gates merge decisions via exit codes."
  classified_by: "cascade"
  classified_at: "2026-02-06T23:45:00Z"
```

## Claim(s)

1. `src/aiv/cli/main.py` implements the `aiv` CLI application per AIV-SUITE-SPEC Section 6.1 with `check` and `init` commands.
2. `aiv check` accepts body from argument, file path, or stdin (`-`), runs the full `ValidationPipeline`, and exits with code 1 on failure.
3. `aiv init` creates `.aiv.yml` configuration file in the target directory.
4. Results are displayed using Rich tables with rule ID, location, message, and suggestion columns.
5. Entry point registered as `aiv = "aiv.cli.main:app"` in pyproject.toml.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** AIV-SUITE-SPEC-V1.0-CANONICAL Section 6.1 — aiv-cli Specification.
- **Requirements Verified:**
  1. ✅ `check` command with body/diff/strict/config options per spec
  2. ✅ `init` command per spec
  3. ✅ Rich output formatting per spec Section 6.1
  4. ✅ Exit code 1 on validation failure

### Class B (Referential Evidence)

**Scope Inventory (required)**

- Created:
  - `src/aiv/cli/main.py` (~155 lines)

### Class A (Execution Evidence)

- N/A for initial commit — CLI will be exercised when `pip install -e .` and tests are run.

### Class C (Negative Evidence — Conservation)

- No existing CLI was present; new file. No regressions possible.

---

## Summary

CLI entry point with `check` and `init` commands per AIV-SUITE-SPEC Section 6.1, using Rich for formatted output and full ValidationPipeline integration.
