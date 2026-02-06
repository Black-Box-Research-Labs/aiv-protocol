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
  classification_rationale: "New pyproject.toml defining Python project build configuration, dependencies, and tooling. Affects build/install behavior for the aiv-protocol Python package. R1 due to dependency declarations and build system setup."
  classified_by: "cascade"
  classified_at: "2026-02-06T22:15:00Z"
```

## Claim(s)

1. `pyproject.toml` defines the Python package build system using hatchling, with proper package metadata (name, version, description, license, classifiers).
2. Dependencies are pinned to compatible ranges: pydantic v2, pydantic-settings v2, mistune v3, typer <1.0, rich v13, PyYAML v6.
3. CLI entry point `aiv` is registered pointing to `aiv.cli.main:app`.
4. Dev tooling configured: pytest (testpaths, pythonpath), mypy (strict mode), ruff (linting rules).
5. Package source layout uses `src/aiv` via hatch build targets.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** AIV-SUITE-SPEC-V1.0-CANONICAL Section 3.3 — Repository structure specifies `pyproject.toml` at root with the defined package layout.
- **Requirements Verified:**
  1. ✅ Package name `aiv-protocol` matches spec
  2. ✅ Source layout `src/aiv/` matches spec Section 3.3
  3. ✅ CLI entry point `aiv` registered per spec Section 6.1
  4. ✅ Dependencies match spec requirements (pydantic v2, mistune, typer, rich)
  5. ✅ Python >=3.11 per spec Section 7

### Class B (Referential Evidence)

**Scope Inventory (required)**

- Created:
  - `pyproject.toml`

**Claim 1: Build system configuration**
- Lines 1-3: hatchling build backend
- Lines 5-26: Project metadata and classifiers

**Claim 2: Dependencies**
- Lines 27-34: Runtime dependencies with version ranges

**Claim 3: CLI entry point**
- Lines 45-46: `aiv = "aiv.cli.main:app"`

**Claim 4: Tooling configuration**
- Lines 56-62: pytest configuration
- Lines 64-68: mypy strict mode
- Lines 70-76: ruff linting rules

**Claim 5: Package layout**
- Lines 53-54: hatch wheel build targets pointing to `src/aiv`

### Class A (Execution Evidence)

- N/A for initial commit — build system will be exercised when `pip install -e .` is run.

---

## Verification Methodology

Visual inspection of pyproject.toml against AIV-SUITE-SPEC-V1.0-CANONICAL Section 3.3 repository structure and Section 6.1 CLI specification.

---

## Summary

Python project configuration establishing the aiv-protocol package with hatchling build system, Pydantic v2 dependencies, CLI entry point, and strict development tooling.
