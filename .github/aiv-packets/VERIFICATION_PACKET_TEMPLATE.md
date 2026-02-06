# AIV Verification Packet (v2.1)

**Commit:** `<latest-commit-sha>`  
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

> [!IMPORTANT]
> **Immutability Requirement (Addendum 2.2):**
> - All Class E links MUST use commit SHAs, NOT `main`/`master`/`develop` branches
> - All Class B code links MUST use commit SHAs, NOT mutable branch names
> - CI run links are naturally immutable (actions/runs/XXXXXX)
> - **Validation will FAIL if mutable branch links are detected**
>
> ✅ Good: `/blob/a1b2c3d/path/to/file.ts#L10-L40` or `/actions/runs/12345`  
> ❌ Bad: `/blob/main/path/to/file.ts` or `/tree/develop/` 

---

## How to use this packet (Sovereign AIV v2.5 workflow)

This repo enforces a **Sovereign AIV atomic unit** at commit-time via Husky:

- Allowed commits:
  - `1 functional file + 1 verification packet`
  - `verification packet only`
  - `package.json + package-lock.json` (explicit exception)
- Forbidden commits:
  - Any staged functional change without a staged packet update
  - Any staged set of 2 files that is not `(functional + packet)` or `(package.json + package-lock.json)`
  - Any staged set of 3+ files

### If you hit a Husky pre-commit error

When Husky rejects your commit, do this:

1. Identify the staged functional file(s) shown in the error.
2. Decide the **Risk Tier** for the change (see below).
3. Update this packet:
   - Add or update **Claim(s)** describing the change.
   - Add **Evidence** for the required classes for your risk tier.
4. Stage exactly the atomic unit:
   - `git add <one-functional-file>`
   - `git add .github/aiv-packets/VERIFICATION_PACKET_<TASK_ID>.md`
5. Retry the commit.

### Progressive workflow (markdown now; canonical JSON later)

- Commit-time: keep this packet markdown-only and focus on writing falsifiable **Claim(s)** plus enough **Evidence** to justify the risk tier.
- PR-time: once the change is ready for review, tighten the packet by:
  - filling in the **classification record** below
  - pinning all permalinks to the final commit SHAs
  - replacing placeholders with immutable **Class A** CI run links
  - (optional) adding the canonical `aiv-canonical-json` block when you are ready for strict machine validation

---

## Classification (required)

```yaml
classification:
  risk_tier: R0 | R1 | R2 | R3
  sod_mode: S0 | S1
  critical_surfaces: []
  blast_radius: local | component | service | cross-service | organization
  classification_rationale: ""
  classified_by: ""
  classified_at: ""
```

## Risk Tiers (choose one)

- **R0 (Trivial)**
  - Typical: docs/comments/formatting only; no runtime effect
  - Minimum evidence: **Class A + Class B**

- **R1 (Low risk)**
  - Typical: isolated logic changes; bounded blast radius; no critical surfaces
  - Minimum evidence: **Class A + Class B + Class E**

- **R2 (Medium risk)**
  - Typical: workflow/CI/config changes, broad refactors, public API changes
  - Minimum evidence: **Class A + Class B + Class C + Class E**

- **R3 (High risk)**
  - Typical: any critical surface (auth/crypto/payments/PII/audit logs) or organization-wide blast radius
  - Minimum evidence: **Class A + Class B + Class C + Class D + Class E + Class F**

If uncertain: pick the higher tier and document why.

### Evidence class requirements by tier

| Risk Tier | Required Evidence Classes |
| --------- | ------------------------- |
| R0        | A, B                      |
| R1        | A, B, E                   |
| R2        | A, B, C, E                |
| R3        | A, B, C, D, E, F          |

---

## Evidence Classes (what they mean)

- **Class A (Execution Evidence)**
  - Proof the change ran: CI run link, artifact link, logs, screenshots.

- **Class B (Referential Evidence)**
  - SHA-pinned permalinks to the exact code and line ranges supporting each claim.

- **Class C (Negative Evidence / Conservation)**
  - Proof regressions did not occur: snapshots, negative tests, invariants preserved.

- **Class D (Differential Evidence)**
  - Explicit before/after diffs of critical behavior, config, schema, or public surface.

- **Class E (Intent Alignment)**
  - Why this change exists: links to directive/spec/issue (SHA-pinned).

- **Class F (Provenance)**
  - Content-addressed integrity: hashes/digests, signed artifacts, immutable storage.

---

## Sovereign Packet Source (PR body)

PR bodies should contain a pointer to this file (not the full packet), using this exact pattern:

`Packet Source: .github/aiv-packets/VERIFICATION_PACKET_<TASK_ID>.md`

AIV Guard CI reads the file from `Packet Source:` (fallback to PR body if missing).

---

## Claim(s)
<!-- List atomic, falsifiable claims. Number each claim. -->

1. [Primary claim - what changed]
2. [Quality claim - typecheck/build/lint]
3. [Safety claim - no regressions / no policy violations]

---

## Evidence

### Class E (Intent Alignment)
<!-- Must use commit SHA permalinks -->

- **Link:** [Spec/Directive](https://github.com/OWNER/REPO/blob/COMMIT_SHA/docs/...#LXX-YY)
- **Requirements Verified:**
  1. ✅ [Requirement 1]
  2. ✅ [Requirement 2]

### Class B (Referential Evidence)
<!-- All code links must use commit SHA permalinks -->
<!-- Get permalink: View file on GitHub → Press 'y' key → Copy URL -->

**Scope Inventory (required)**

- Created:
  - [`path/to/new_file`](https://github.com/OWNER/REPO/blob/COMMIT_SHA/path/to/new_file#L1-L1)
- Modified:
  - [`path/to/changed_file`](https://github.com/OWNER/REPO/blob/COMMIT_SHA/path/to/changed_file#L1-L1)
- Deleted:
  - `path/to/deleted_file`

**Claim 1: [Description]**
- [`path/to/file`](https://github.com/OWNER/REPO/blob/COMMIT_SHA/path/to/file#LXX-LYY) - Description
- Signature: [`functionName`](https://github.com/OWNER/REPO/blob/COMMIT_SHA/path/to/file#LXX)

### Class A (Execution Evidence)
<!-- CI run links are naturally immutable (actions/runs/XXXXXX) -->

**Claim 2: Build and typecheck pass**
- [CI Run #XXXXXXX - All Jobs Successful](https://github.com/OWNER/REPO/actions/runs/XXXXXXX)

Minimum required details:
- Test results: `X passed, Y failed, Z skipped`
- Test list / suite names executed
- Static analysis: lint/typecheck result (or explicit N/A with justification)
- Execution environment: OS + runtime version

### Class C (Negative Evidence - Conservation)
<!-- Required for R2+ -->

- [Artifact / Report](https://github.com/OWNER/REPO/actions/runs/XXXXXX/artifacts/YYYYY)
- Shows:
  - [Invariant 1 preserved]
  - [Invariant 2 preserved]

Minimum required details for R2+:
- Search scope: `src/`, `engine/`, `.github/`, etc.
- Search method: tool + version
- Patterns checked: enumerated allow/deny list
- Results: explicit "no matches" or empty output

### Class D (Differential Evidence)
<!-- Required for R3 -->

- Before/After diff:
  - [Permalink to previous behavior]
  - [Permalink to new behavior]

### Class F (Provenance)
<!-- Required for R3 -->

- Digest / Hash:
  - `sha256:...`
- Immutable location:
  - [Content-addressed storage reference]

---

## Critical Safety Guidelines (What NOT to Do)

- **MIND YOUR OWN BUSINESS** - Don't touch files you didn't modify!
- **NEVER discard changes you don’t recognize.** If `git status` shows unexpected modifications, investigate them first. They may be intentional, required, or part of a coordinated change set.
- **NEVER assume a file is “unrelated” because you didn’t modify it.** Other processes (linters, formatters, dependency updates, team members) may have made necessary changes.
- **ALWAYS verify the nature of unexpected changes** before staging or discarding. Use `git diff` to review content and context.
- **If uncertain, ask for clarification** rather than making irreversible decisions.

---

## Verification Methodology
<!-- Zero-Touch Mandate: verifier inspects ARTIFACTS, not runs commands locally -->

**Build verification commands (context only):**
```bash
npm ci
npx astro check
npm run build
```

---

## Summary

All claims supported by immutable links and CI evidence at commit `<latest-commit-sha>`.
