# AIV Verification Packet (v2.1)

**Commit:** `03c4bd0`  
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R2
  sod_mode: S0
  critical_surfaces: []
  blast_radius: service
  classification_rationale: "CI workflow that runs on push/PR to main. Generates machine-readable Class A and Class C evidence artifacts (JSON manifests), runs type checking, linting, build validation, content validation, and semantic test integrity reports. R2 due to CI/infrastructure nature and broad impact on evidence generation pipeline."
  classified_by: "cascade"
  classified_at: "2026-02-06T22:10:00Z"
```

## Claim(s)

1. `.github/workflows/verify-architecture.yml` defines a CI job that validates content collections, runs Astro type checking, TypeScript checking, linting, and builds the site.
2. The workflow generates `class_a_execution.json` (Class A evidence) and `class_c_negative.json` (Class C evidence) as machine-readable JSON manifests.
3. The workflow generates a semantic test integrity report (`test_integrity_semantic.json`) that validates CI workflow integrity via YAML parsing.
4. All evidence artifacts are uploaded as the `aiv-evidence` artifact for downstream consumption by `aiv-guard.yml`.
5. Negative evidence checks verify: robots.txt blocks /audit/, audit pages are noindex, API routes are not prerendered.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** AIV Protocol §6.2 (Class A — Execution Evidence) and §6.4 (Class C — Negative Evidence) — CI must generate machine-readable evidence artifacts.
- **Requirements Verified:**
  1. ✅ Class A manifest includes: head_sha, run metadata, execution environment, test results, test list
  2. ✅ Class C manifest includes: search_method, search_scope, patterns, test_integrity
  3. ✅ Semantic test integrity report generated
  4. ✅ Artifacts uploaded for aiv-guard inspection

### Class B (Referential Evidence)

**Scope Inventory (required)**

- Created:
  - `.github/workflows/verify-architecture.yml` (528 lines)

**Claim 1: Build validation steps**
- Lines 34-61: Astro check, TypeScript check, content validation, build, lint

**Claim 2-3: Evidence manifest generation**
- Lines 78-171: Python script generating class_a_execution.json and class_c_negative.json
- Lines 173-528: Node.js script generating semantic test integrity report

**Claim 4-5: Negative evidence checks**
- Lines 63-76: grep-based checks for robots.txt, noindex, prerender settings

### Class A (Execution Evidence)

- N/A for initial commit — workflow will execute on first PR to main.

### Class C (Negative Evidence — Conservation)

- No existing CI workflow was present; this is a new file. No regressions possible.

---

## Verification Methodology

Visual inspection of workflow YAML against AIV evidence generation requirements.

---

## Summary

CI workflow generating Class A and Class C evidence artifacts with semantic test integrity validation. Runs type checking, linting, build, and content validation.
