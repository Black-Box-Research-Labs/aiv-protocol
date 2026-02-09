# AIV Error Code Reference

When `aiv check` or the pre-commit hook rejects a packet, it reports error
codes like `[E004]`. This document explains every code, what triggers it,
and how to fix it.

---

## Severity Levels

| Level | Meaning |
|-------|---------|
| **BLOCK** | Commit/PR is rejected. Must fix before proceeding. |
| **WARN** | Flagged but does not block. Should be addressed. |
| **INFO** | Informational. No action required. |

---

## Error Codes

### E001 — Parse Failure

| | |
|---|---|
| **Severity** | BLOCK |
| **Source** | `pipeline.py` |
| **Trigger** | Packet markdown is malformed — missing required sections, invalid YAML in Classification block, or unrecognizable structure. |
| **Fix** | Use `aiv generate <name> --tier <R0-R3>` to scaffold a valid packet, or run `aiv check <file>` to see the specific parse error. Ensure your packet has `## Claims`, `## Evidence`, and `## Classification` sections. |

### E002 — Verifier Check Too Brief

| | |
|---|---|
| **Severity** | WARN |
| **Source** | `structure.py` |
| **Trigger** | The Verifier Check field in the Intent section is less than 10 characters. |
| **Fix** | Expand the verifier check to describe what the verifier should confirm. Example: `"Verify that expired tokens return HTTP 401, not 500."` |

### E004 — Mutable Link

| | |
|---|---|
| **Severity** | BLOCK |
| **Source** | `links.py`, `evidence.py` |
| **Trigger** | A link in the evidence uses a mutable reference (e.g. `/blob/main/` instead of `/blob/<SHA>/`). Class E links must be SHA-pinned. |
| **Fix** | Replace branch names in URLs with the full commit SHA. Example: change `blob/main/src/auth.py` to `blob/abc1234def5678/src/auth.py`. The `aiv commit` command does this automatically. |

### E005 — Claim Description Too Brief

| | |
|---|---|
| **Severity** | WARN |
| **Source** | `structure.py` |
| **Trigger** | A claim description is less than 15 characters. |
| **Fix** | Write a specific, falsifiable claim. Bad: `"Fixed bug"`. Good: `"TokenValidator rejects expired tokens with HTTP 401"`. |

### E008 — Zero-Touch Violation

| | |
|---|---|
| **Severity** | BLOCK (prohibited pattern) / WARN (high friction) |
| **Source** | `structure.py`, `zero_touch.py` |
| **Trigger** | Reproduction instructions contain local execution commands (`git clone`, `pip install`, `python`, `cd`, etc.), or the packet has high friction (many manual steps). |
| **Fix** | Remove manual reproduction steps. Evidence should be verifiable by inspecting artifacts only (CI links, test output, permalinks). If local execution is truly needed, explain why in the methodology section. |

### E009 — Evidence Artifact Link Mutable

| | |
|---|---|
| **Severity** | BLOCK |
| **Source** | `links.py` |
| **Trigger** | An evidence artifact link uses a mutable reference (branch name, `HEAD`, `latest` tag). |
| **Fix** | Same as E004 — pin all links to a specific commit SHA. |

### E010 — Bug Fix Without Provenance

| | |
|---|---|
| **Severity** | BLOCK |
| **Source** | `evidence.py` |
| **Trigger** | The packet appears to be a bug fix (claim text contains "fix", "bug", "patch") but has no Class F (Provenance) evidence. |
| **Fix** | Add a Class F section showing the chain-of-custody of the relevant test files. The `aiv commit` command collects this automatically for R2+ tiers. |

### E011 — Unjustified Test Modification

| | |
|---|---|
| **Severity** | BLOCK (pipeline anti-cheat) / WARN (evidence) |
| **Source** | `pipeline.py`, `evidence.py` |
| **Trigger** | The diff shows deleted assertions, added skip markers, or removed test files, and there is no Class F justification explaining why. |
| **Fix** | Add a justification in Class F explaining why tests were modified. Example: `"Removed test_old_auth because the auth module was completely rewritten — replaced by test_new_auth with 12 assertions."` |

### E012 — Weak Class A Evidence

| | |
|---|---|
| **Severity** | WARN / INFO |
| **Source** | `evidence.py` |
| **Trigger** | Class A evidence links to a PR (not a CI run), is a text reference (not a link), or a UI claim lacks a GIF/video. |
| **Fix** | Link directly to a CI run URL. For UI claims, include a screenshot or GIF showing the state transition. |

### E013 — Performance Claim Without Benchmarks

| | |
|---|---|
| **Severity** | BLOCK |
| **Source** | `evidence.py` |
| **Trigger** | A claim mentions "performance" but there are no CI-based differential benchmarks in the evidence. |
| **Fix** | Include before/after benchmark results from CI. Example: `"Latency: 42ms → 28ms (33% improvement, measured by benchmark suite run #1234)."` |

### E014 — Missing Classification Section

| | |
|---|---|
| **Severity** | WARN |
| **Source** | `pipeline.py` |
| **Trigger** | The packet has no `## Classification` section with a YAML block specifying risk_tier. |
| **Fix** | Add a Classification section. The `aiv commit` and `aiv generate` commands include this automatically. |

### E015 — Class B Should Link to Code

| | |
|---|---|
| **Severity** | WARN |
| **Source** | `evidence.py` |
| **Trigger** | Class B (Referential) evidence doesn't link to a GitHub blob (code file). |
| **Fix** | Include SHA-pinned permalinks to the exact lines changed. The `aiv commit` command generates these from `git diff`. |

### E016 — Class B Missing File References

| | |
|---|---|
| **Severity** | WARN |
| **Source** | `evidence.py` |
| **Trigger** | Class B evidence doesn't reference specific file locations. |
| **Fix** | Include paths like `src/auth.py#L42-L58` in your Class B section. |

### E017 — Class C Should State Negatives

| | |
|---|---|
| **Severity** | WARN |
| **Source** | `evidence.py` |
| **Trigger** | Class C (Negative) evidence doesn't clearly state what is NOT present (missing negative framing like "no", "none", "absent", "not found"). |
| **Fix** | Explicitly state what you searched for and didn't find. Example: `"Searched all test files for deleted assertions — none found."` |

### E018 — Class D Manual Database Queries

| | |
|---|---|
| **Severity** | BLOCK |
| **Source** | `evidence.py` |
| **Trigger** | Class D (Differential) evidence requires manual database queries to verify. |
| **Fix** | Replace manual verification with automated evidence. Show the diff output, API surface changes, or config deltas directly in the packet. |

### E019 — Required Evidence Class Missing

| | |
|---|---|
| **Severity** | BLOCK |
| **Source** | `pipeline.py` |
| **Trigger** | The risk tier requires an evidence class that is not present in the packet. Example: R2 requires Class C but the packet has no Class C section. |
| **Fix** | Add the missing evidence class. Check the requirements: R0/R1 need A+B, R2 adds C+E, R3 adds D+F. The `aiv commit` command collects all required classes automatically. |

### E020 — Optional Evidence Missing / Code Blob Warning

| | |
|---|---|
| **Severity** | INFO (pipeline) / WARN (evidence) |
| **Source** | `pipeline.py`, `evidence.py` |
| **Trigger** | An optional evidence class for the tier is missing (INFO), or Class A links to a code file instead of a CI run (WARN). |
| **Fix** | For the INFO variant, consider adding the optional class for completeness. For the WARN, link to a CI run URL instead of a source file. |

### E021 — Unreachable Link / API Change Without Class D

| | |
|---|---|
| **Severity** | BLOCK / WARN |
| **Source** | `links.py`, `evidence.py` |
| **Trigger** | An evidence link returns HTTP 4xx/5xx (BLOCK), cannot be reached (WARN), or an API-related file was changed without Class D evidence (WARN). |
| **Fix** | For broken links: verify the URL is correct and the resource exists. For API changes: add a Class D section documenting what changed. |

### E022 — Class D Missing Keyword

| | |
|---|---|
| **Severity** | INFO |
| **Source** | `evidence.py` |
| **Trigger** | Class D evidence is present but doesn't mention a relevant keyword (e.g., "API", "config", "schema") triggered by the changed files. |
| **Fix** | Ensure your Class D section explicitly addresses the type of change. This is informational — it won't block your commit. |

---

## Quick Reference

| Code | Severity | One-Line Summary |
|------|----------|------------------|
| E001 | BLOCK | Packet parse failure |
| E002 | WARN | Verifier check too brief |
| E004 | BLOCK | Link not SHA-pinned |
| E005 | WARN | Claim too brief |
| E008 | BLOCK/WARN | Zero-Touch violation |
| E009 | BLOCK | Evidence link mutable |
| E010 | BLOCK | Bug fix needs Class F |
| E011 | BLOCK/WARN | Unjustified test modification |
| E012 | WARN/INFO | Weak Class A evidence |
| E013 | BLOCK | Performance claim needs benchmarks |
| E014 | WARN | Missing Classification section |
| E015 | WARN | Class B should link to code |
| E016 | WARN | Class B missing file refs |
| E017 | WARN | Class C needs negative framing |
| E018 | BLOCK | Class D can't require manual DB |
| E019 | BLOCK | Required evidence class missing |
| E020 | INFO/WARN | Optional evidence / code blob |
| E021 | BLOCK/WARN | Broken link / API needs Class D |
| E022 | INFO | Class D missing keyword |
