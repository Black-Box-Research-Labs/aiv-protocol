# AIV Verification Packet (v2.1)

**Commit:** `c4128a1`  
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R2
  sod_mode: S0
  critical_surfaces: []
  blast_radius: component
  classification_rationale: "Pre-commit hook enforcing AIV atomic commit policy across the entire repository. Affects all contributors' commit workflow. R2 due to broad blast radius (every commit passes through this gate) and infrastructure nature."
  classified_by: "cascade"
  classified_at: "2026-02-06T22:05:00Z"
```

## Claim(s)

1. `.husky/pre-commit` enforces the AIV atomic commit policy: exactly 1 functional file + 1 verification packet per commit.
2. The hook creates safety snapshots (status, diff, cached diff, untracked files) before every commit attempt.
3. Allowed commit patterns: (a) 1 functional file + 1 packet, (b) packet-only, (c) package.json + package-lock.json, (d) .gitkeep + packet, (e) submodule + packet.
4. The hook prints the full AIV compliance rubric when code is staged without a packet, serving as cognitive context restoration for AI agents.
5. The hook runs lint-staged for valid commits when package.json and node_modules are present.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** AIV Protocol Addendum 2.5 — Sovereign AIV atomic unit enforcement at commit-time.
- **Requirements Verified:**
  1. ✅ Atomic commit policy enforced (1 functional file + 1 packet)
  2. ✅ Safety snapshots created before each commit
  3. ✅ Cognitive context restoration rubric printed on violation
  4. ✅ Dependency pair exception (package.json + package-lock.json)
  5. ✅ Submodule commit exceptions supported

### Class B (Referential Evidence)

**Scope Inventory (required)**

- Created:
  - `.husky/pre-commit` (184 lines)

**Claim 1-3: Atomic commit enforcement**
- Lines 43-46: Staged file capture
- Lines 47-65: Pattern detection (packet, functional, gitkeep, submodule)
- Lines 108-167: Atomicity rules 1-6
- Lines 34-39: Untracked file archival in safety snapshot

**Claim 4: Cognitive context restoration**
- Lines 68-104: `print_aiv_rubric()` function — prints risk tiers, evidence taxonomy, and agent instructions

**Claim 5: lint-staged integration**
- Lines 170-183: Conditional lint-staged execution

### Class A (Execution Evidence)

- N/A for initial commit — hook will be exercised on all subsequent commits in this repository.

### Class C (Negative Evidence — Conservation)

- No existing pre-commit hook was present; this is a new file. No regressions possible.

---

## Verification Methodology

Visual inspection of shell script logic against AIV atomic commit policy requirements.

---

## Summary

Pre-commit hook implementing AIV atomic commit enforcement with safety snapshots, cognitive context restoration, and lint-staged integration.
