# AIV Verification Packet (v2.1) — Re-Audit Critique Remediation

**Commit:** `pending`
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: component
  classification_rationale: "Addresses 4 critiques from external re-audit: CI split-brain, hollow pre-commit hook, generate toil, trivial Class D validation. Changes span CI workflows, pre-commit hook, CLI generate command, and evidence validator. No changes to core validation pipeline logic."
  classified_by: "ImmortalDemonGod"
  classified_at: "2026-02-07T07:12:56Z"
```

## Claims

1. Disabling `aiv-guard.yml` eliminates the split-brain architecture where two guards with different logic (2244-line JS vs 44-line Python) validate the same PRs — the Python guard in `aiv-guard-python.yml` is now the sole PR validation workflow.
2. The pre-commit hook `validate_staged_packet()` function runs `aiv check` on the staged packet content (extracted via `git show`), rejecting commits with blocking errors while allowing warnings through.
3. The `aiv generate` command auto-detects git context (owner/repo, branch, issue number, HEAD SHA), runs local checks (pytest, ruff, mypy), and fetches the latest CI run URL — all gated behind `--skip-checks` for test performance.
4. The `EvidenceValidator.validate_file_type_triggers()` method inspects changed file paths and demands Class D evidence when database (.sql), dependency (pyproject.toml), API schema (.proto), or infrastructure (Dockerfile) files are modified.
5. All 424 tests pass. No existing tests were weakened — only one test was updated to pass `--skip-checks` to avoid a timeout from the new local checks.

---

## Evidence

### Class E (Intent Alignment)

- **Directive:** Address the 4 critiques from the external re-audit of the AIV protocol codebase (Feb 2026):
  1. Kill the zombie JS workflow (split-brain CI)
  2. Wire real validation into the pre-commit hook (shift-left)
  3. Auto-populate the generate command (reduce toil)
  4. Add file-type triggers to Class D validation (context-aware)

### Class B (Referential Evidence)

**Scope Inventory**

- Modified: `.github/workflows/aiv-guard.yml` — trigger changed from `pull_request` to `workflow_dispatch: {}`
- Modified: `.husky/pre-commit` — added `validate_staged_packet()` function (lines 118-176) called before all packet-accepting rules
- Modified: `src/aiv/cli/main.py` — added `_detect_git_context()`, `_fetch_latest_ci_url()`, `_fetch_issue_title()`, `_run_local_checks()`, `--skip-checks` flag, auto-populated `_build_evidence_sections()`
- Modified: `src/aiv/lib/validators/evidence.py` — added `validate_file_type_triggers()` method with 4 trigger categories (E021/E022 rules)
- Modified: `tests/integration/test_e2e_compliance.py` — added `--skip-checks` to generate roundtrip test
- Modified: `.github/aiv-packets/VERIFICATION_PACKET_FILE_PACKET_MAP.md` — added missing Class E section

### Class A (Execution Evidence)

- Local: `pytest` — 424 passed, 0 failed
- Local: `ruff check src/ tests/` — All checks passed
- Local: `mypy src/aiv/` — Success: 0 errors
- Local: `ruff format --check src/ tests/` — 46 files already formatted
- Local: `aiv audit` — 62 scanned, 6 pre-existing issues (0 new)

---

## Verification Methodology

```bash
python -m ruff check src/ tests/
python -m ruff format --check src/ tests/
python -m mypy src/aiv/
python -m pytest --tb=short -q
python -m aiv audit
```

---

## Summary

Addresses all 4 critiques from the external re-audit: disabled the 2244-line JS guard zombie, wired `aiv check` into the pre-commit hook for real shift-left validation, enhanced `aiv generate` to auto-populate from git context and GitHub API, and added file-type-aware Class D triggers to the evidence validator.
