# AIV Verification Packet (v2.1)

**Commit:** `60ea728`  
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R2
  sod_mode: S0
  critical_surfaces: []
  blast_radius: service
  classification_rationale: "Primary AIV enforcement CI workflow — validates verification packets on every PR to main. R2 due to: (1) CI/infrastructure nature, (2) gates all merges to main, (3) implements the core AIV validation logic including canonical JSON parsing, evidence class validation, critical surface detection, SoD enforcement, attestation validation, and artifact inspection."
  classified_by: "cascade"
  classified_at: "2026-02-06T22:12:00Z"
```

## Claim(s)

1. `.github/workflows/aiv-guard.yml` validates AIV verification packets on every PR opened/edited/synchronized against main.
2. **Markdown validation**: Checks for required sections (header, claims, evidence classes A/B/E, summary, verification methodology or reproduction).
3. **Immutability enforcement**: Rejects mutable branch links (`/blob/main/`, `/tree/develop/`) in Class E and Class B sections.
4. **Fast-Track**: Docs-only PRs (.md, .txt, .gitignore, .editorconfig) bypass full packet requirements.
5. **Canonical JSON validation** (when `aiv-canonical-json` block present): validates schema completeness, SHA binding (head_sha/base_sha match PR), risk tier, SoD mode, attestations, evidence class requirements by tier, scope inventory vs diff, claim-evidence mapping, and CI artifact inspection.
6. **Critical surface auto-detection**: Regex patterns on file paths and semantic content analysis detect auth, authorization, secrets, crypto, privilege, audit/logging, and PII surfaces — forces R3 classification.
7. **Artifact inspection**: Downloads and validates the `aiv-evidence` artifact from the referenced CI run, checking Class A and Class C JSON manifests for schema compliance and SHA binding.
8. Outputs machine-readable `aiv_validation_result.json` conforming to the §14.2 validation output schema.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [AIV Protocol §9 (Gating Rules), §14 (Conformance Testing), §6 (Evidence Requirements)](https://github.com/ImmortalDemonGod/aiv-protocol/blob/9a41695/SPECIFICATION.md) — the guard implements automated merge-gate enforcement.
- **Requirements Verified:**
  1. ✅ Merge gate enforcement (§9.1 G-001 through G-006)
  2. ✅ Evidence class validation by tier (§6.1)
  3. ✅ Immutability enforcement (§9.2 G-IMM-01 through G-IMM-05)
  4. ✅ Critical surface escalation (§5.2)
  5. ✅ SoD enforcement (§5.4)
  6. ✅ Attestation validation (§7.4)
  7. ✅ Machine-readable output (§14.2)

### Class B (Referential Evidence)

**Scope Inventory (required)**

- Created:
  - `.github/workflows/aiv-guard.yml` (2244 lines)

**Claim 1: Workflow trigger and permissions**
- Lines 1-15: Trigger on pull_request (opened/edited/synchronize) to main; read-only permissions

**Claim 2: Markdown validation**
- Lines 322-435: Required section checks, optional section detection, fast-track eligibility

**Claim 3: Immutability enforcement**
- Lines 437-461: Mutable branch pattern detection in Class E and Class B sections

**Claim 5: Canonical JSON validation**
- Lines 469-598: JSON parsing, field validation, SHA binding, PR ID matching
- Lines 593-724: Risk tier validation, critical surface detection, SoD enforcement
- Lines 726-869: Attestation validation (decision, signature, CONDITIONAL constraints)
- Lines 871-920: Known limitations, evidence items, claims validation
- Lines 1157-1183: Claim-evidence bidirectional mapping with Class B requirement

**Claim 6: Critical surface detection**
- Lines 627-696: Path-based and semantic regex patterns for 7 critical surface categories

**Claim 7: Artifact inspection**
- Lines 1428-1698: Download aiv-evidence.zip, validate Class A and Class C JSON manifests

**Claim 8: Machine-readable output**
- Lines 262-320: `process.on('exit')` handler generating aiv_validation_result.json

### Class A (Execution Evidence)

- N/A for initial commit — workflow will execute on first PR to main.

### Class C (Negative Evidence — Conservation)

- No existing aiv-guard workflow was present; this is a new file. No regressions possible.

---

## Verification Methodology

Visual inspection of workflow JavaScript logic against AIV specification validation rules (Appendix C).

---

## Summary

Primary AIV enforcement workflow implementing PR validation with markdown checks, canonical JSON validation, critical surface detection, SoD enforcement, attestation validation, artifact inspection, and machine-readable output.
