# External Readiness Audit

**Purpose:** Reusable Class E reference for any work that improves AIV's
external usability. Link this doc from `--intent` when committing fixes.

**Audit date:** 2026-02-09
**Auditor:** Cascade + ImmortalDemonGod
**Scope:** Can an external user (human or LLM) install AIV in their own
project and use it autonomously?

---

## Methodology

1. Traced the full external-user journey: `pip install` → `aiv init` →
   first commit → hook rejection → fix → successful commit
2. Checked each step for: silent failures, missing docs, hardcoded assumptions
3. Classified issues by impact: P0 (blocks use), P1 (degrades autonomy),
   P2 (rough edges)

---

## Findings

### P0 — Blocks External Use

#### P0-1: `FUNCTIONAL_PREFIXES` hardcoded — silently bypasses hook

**File:** `src/aiv/hooks/pre_commit.py` lines 41-50

**Problem:** The pre-commit hook uses a hardcoded tuple of directory prefixes
to decide what counts as "functional code" requiring a verification packet:

```python
FUNCTIONAL_PREFIXES = (
    "src/",
    "engine/",
    "infrastructure/",
    "scripts/",
    "tests/",
    ".github/workflows/",
    ".github/PULL_REQUEST_TEMPLATE.md",
    ".husky/",
)
```

Any project using `lib/`, `app/`, `pkg/`, `cmd/`, `internal/`, `backend/`,
`frontend/`, or any non-standard layout will have the hook **silently do
nothing**. Files outside these prefixes are classified as "non-functional"
by `_is_functional()`, which means the docs-only exception (rule 7) applies
and no packet is required. The user gets **zero feedback** that their code
bypassed all verification.

**Root cause:** The hook doesn't read `.aiv.yml`. `AIVConfig` in `config.py`
has no `functional_prefixes` field. The hook is entirely standalone.

**Fix:**
- Add `functional_prefixes` and `functional_root_files` to `AIVConfig`
- Have the hook load `.aiv.yml` at startup and use configured prefixes
- Fall back to current defaults if no config exists
- Update `aiv init` to generate config with commented-out prefix options

**Verification:** After fix, a project with `lib/mycode.py` staged should
trigger the hook's "functional code without packet" rejection.

---

#### P0-2: `FUNCTIONAL_ROOT_FILES` contains project-specific artifacts

**File:** `src/aiv/hooks/pre_commit.py` lines 52-62

**Problem:** The set includes `astro.config.mjs` and `tailwind.config.js` —
artifacts of this project's history, not generic choices. Projects using
Vite, Webpack, Next.js, etc. aren't covered.

**Fix:** Remove framework-specific entries. Keep only universal config files
(`pyproject.toml`, `package.json`, `setup.py`, `setup.cfg`, `.gitignore`).
Make the full list configurable via `.aiv.yml` (same fix as P0-1).

---

### P1 — Degrades LLM Autonomy

#### P1-3: No error code reference documentation

**Problem:** There are **15+ distinct error codes** enforced across the
validators, but none are documented outside the source code. When
`aiv check` fails with `[E004] Class E Evidence must be immutable`, neither
an LLM nor a human has documentation explaining what E004 means, what causes
it, or how to fix it.

**Complete error code catalog (from source audit):**

| Code | Source File(s) | Severity | What It Means |
|------|---------------|----------|---------------|
| E001 | pipeline.py | BLOCK | Failed to parse packet (malformed markdown/YAML) |
| E002 | structure.py | WARN | Verifier Check in Intent section too brief (<10 chars) |
| E004 | links.py, evidence.py | BLOCK | Link is mutable / not SHA-pinned |
| E005 | structure.py | WARN | Claim description too brief (<15 chars) |
| E008 | structure.py, zero_touch.py | BLOCK/WARN | Missing reproduction / Zero-Touch violation / high friction |
| E009 | links.py | BLOCK | Evidence artifact link is mutable |
| E010 | evidence.py | BLOCK | Bug fix detected but no Class F (Provenance) evidence |
| E011 | pipeline.py, evidence.py | BLOCK/WARN | Anti-cheat: unjustified test modification |
| E012 | evidence.py | WARN/INFO | Class A links to PR not CI, or UI claim without GIF |
| E013 | evidence.py | BLOCK | Performance claim without CI-based benchmarks |
| E014 | pipeline.py | WARN | Missing ## Classification YAML section |
| E015 | evidence.py | WARN | Class B should link to GitHub code blob |
| E016 | evidence.py | WARN | Class B should reference specific file locations |
| E017 | evidence.py | WARN | Class C should state what is NOT present |
| E018 | evidence.py | BLOCK | Class D must not require manual database queries |
| E019 | pipeline.py | BLOCK | Required evidence class missing for risk tier |
| E020 | pipeline.py, evidence.py | INFO/WARN | Optional evidence missing / Class A links to code file |
| E021 | links.py, evidence.py | BLOCK/WARN | Evidence link unreachable / API change without Class D |
| E022 | evidence.py | INFO | Class D present but doesn't mention relevant keyword |

**Fix:** Create `docs/ERROR_CODES.md` with the full reference. Add top-5
most common errors + fixes to the README.

---

#### P1-4: README Class F example IS verification theater

**File:** `README.md` lines 320-324

**Problem:** The example shown for Class F evidence is:

```markdown
- No test files modified or deleted. Full test suite passes.
- Commit signed with GPG key `2A55...52C6`.
```

This is the **exact pattern** identified as theater in the V2 audit of
`CLAIM_AWARE_EVIDENCE_PLAN.md` — "No test files deleted" is Class C, "full
test suite passes" is Class A. Class F should show git log chain-of-custody.

**Fix:** Replace with the new format:

```markdown
**Test file chain-of-custody:**

| File | Commits | Created By | Last Modified By | Assertions |
|------|---------|------------|------------------|------------|
| `tests/unit/test_auth.py` | 12 | alice (a1b2c3d) | bob (e4f5g6h) | 47 |
```

---

#### P1-5: No complete packet example in README

**Problem:** The README shows evidence snippets per class but never a
complete minimal valid packet. An LLM trying to write or understand a
packet has no reference. `aiv generate` produces templates with TODOs.

**Fix:** Add a "Complete Minimal Packet (R1)" section in the README showing
a real, `aiv check`-passing packet with all required sections.

---

### P2 — Rough Edges

#### P2-6: `aiv init` generates minimal `.aiv.yml`

**File:** `src/aiv/cli/main.py` lines 121-127

**Problem:** Generated config only has `version` and `strict_mode`. No
`functional_prefixes`, no `packet_dir`, no hint that these are configurable
(because they aren't yet — see P0-1).

**Fix:** After P0-1 is implemented, update `aiv init` to generate a config
with all available options as comments:

```yaml
# AIV Protocol Configuration
version: "1.0"
strict_mode: true

# Uncomment and customize for your project layout:
# functional_prefixes:
#   - "src/"
#   - "lib/"
#   - "app/"
#   - "tests/"
# functional_root_files:
#   - "pyproject.toml"
#   - "package.json"
```

---

#### P2-7: Required `aiv commit` flags not documented in README

**Problem:** `--claim`, `--intent`, `--requirement`, `--rationale`, and
`--summary` are all required, but the README doesn't say so. An LLM would
discover this only by getting an error.

**Fix:** Add a flag reference table:

```markdown
| Flag | Required | Description |
|------|----------|-------------|
| `--claim` / `-c` | Yes (repeatable) | Falsifiable claim about the change |
| `--intent` / `-i` | Yes | Class E: URL to spec/issue/directive |
| `--requirement` | Yes | Which specific requirement the URL satisfies |
| `--rationale` / `-r` | Yes | Why this risk tier was chosen |
| `--summary` / `-s` | Yes | One-line summary of the change |
| `--tier` / `-t` | No (default: R1) | Risk tier: R0, R1, R2, R3 |
| `--skip-checks` | No | Skip pytest/ruff/mypy |
| `--dry-run` | No | Generate + validate, don't commit |
| `--force` | No | Override R3 unverified-claim block (requires justification) |
```

---

## Implementation Priority

| # | Issue | Files | Risk | Effort | Status |
|---|-------|-------|------|--------|--------|
| P0-1 | Configurable functional prefixes | config.py, pre_commit.py, main.py | Medium | Medium | TODO |
| P0-2 | Remove project-specific root files | pre_commit.py | Low | Small | TODO |
| P1-3 | Error code reference | docs/ERROR_CODES.md, README.md | None | Medium | TODO |
| P1-4 | Fix Class F README example | README.md | None | Small | TODO |
| P1-5 | Complete packet example | README.md | None | Small | TODO |
| P2-6 | Better aiv init template | main.py | Low | Small | TODO |
| P2-7 | Document required flags | README.md | None | Small | TODO |

---

## How to Use This Document

When committing fixes for any issue above, use this doc as Class E:

```bash
aiv commit src/aiv/hooks/pre_commit.py \
  -m "feat(hooks): configurable functional prefixes via .aiv.yml" \
  -t R2 \
  -c "Hook reads functional_prefixes from .aiv.yml" \
  -c "Falls back to default prefixes if no config" \
  -i "https://github.com/ImmortalDemonGod/aiv-protocol/blob/<SHA>/docs/EXTERNAL_READINESS_AUDIT.md" \
  --requirement "P0-1: FUNCTIONAL_PREFIXES hardcoded" \
  -r "R2: hook behavior change affects all projects" \
  -s "Make pre-commit hook configurable for non-src/ projects"
```

Replace `<SHA>` with the commit SHA of this document.
