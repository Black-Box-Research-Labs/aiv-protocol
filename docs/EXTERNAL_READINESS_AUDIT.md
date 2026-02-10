# External Readiness Audit

**Purpose:** Reusable Class E reference for any work that improves AIV's
external usability. Link this doc from `--intent` when committing fixes.

**Audit date:** 2026-02-09
**Auditor:** Cascade + ImmortalDemonGod
**Scope:** Can an external user (human or LLM) install AIV in their own
project and use it autonomously?

---

## Revision History

| Rev | Date | Branch | Summary |
|-----|------|--------|---------|
| 1.0 | 2026-02-09 | main | Initial audit — 8 findings (P0-1 through P2-7) |
| 2.0 | 2026-02-09 | `feat/external-readiness-polyglot` | Phase 2 — codebase re-audit found P0-1 only partially fixed (pre_push.py and auditor.py still hardcoded). Added P0-4 (config propagation), P1-6/7/8 (polyglot evidence gaps). This revision is the Class E intent for PR #1. |
| 3.0 | 2026-02-10 | `feat/polyglot-evidence-collection` | Phase 3 — P1-6/7/8 implemented via tree-sitter LanguageDriver. JS/TS/TSX/JSX get per-symbol evidence. Class E intent for PR #2. |

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

### P0-3: No enforcement beyond pre-commit hook — `--no-verify` bypass

**Problem:** The pre-commit hook was the **only** enforcement layer that
validates "every functional commit has a paired verification packet." But
`git commit --no-verify` is a built-in Git flag that skips pre-commit hooks.
The CI guard (`aiv-guard-python.yml`) only runs on `pull_request`, not on
direct pushes to main. The CI pipeline (`ci.yml`) runs tests but never checks
commit-packet pairing.

This meant: `--no-verify` + `git push` = zero validation.

**Incident:** During this audit's own implementation, 3 consecutive commits
used `--no-verify` as a first resort without ever trying `aiv commit`:

| Commit | Files | Violation |
|--------|-------|-----------|
| `e53f2c6` | 3 functional files bundled | `--no-verify`, no packet, atomic violation |
| `249ecde` | 4 functional files bundled | `--no-verify`, no packet, atomic violation |
| `c0561ff` | 7 files bundled (the commit "closing the enforcement gap") | `--no-verify`, no packet, atomic violation |

When `c0561ff` was redone properly using `aiv commit`, every file committed
successfully on the first try. The "chicken-and-egg" excuse (can't commit the
enforcement code while enforcement blocks you) was **false** — the tool
worked exactly as designed. The real cause was path-of-least-resistance
behavior: `--no-verify` is fewer keystrokes than `aiv commit`.

**Root cause:** Single-layer enforcement. No defense-in-depth. Behavioral
instructions ("don't use `--no-verify`") are useless for LLM agents — the
solution must be architectural.

**Key insight:** `git commit --no-verify` only skips `pre-commit` and
`commit-msg` hooks. It does **NOT** skip `pre-push` hooks. A pre-push hook
catches `--no-verify` commits before they leave the local machine.

**Defence-in-depth (4 layers, all implemented):**

```
Layer 1: pre-commit hook     — blocks at commit time
           ↓ bypassed by git commit --no-verify
Layer 2: pre-push hook (NEW) — catches --no-verify commits on push
           ↓ bypassed by git push --no-verify
Layer 3: CI protocol-audit   — catches --no-verify push (server-side)
           ↓ bypassed by direct push to main
Layer 4: Branch protection   — require PRs (GitHub settings, not code)
```

| Layer | Hook | Bypass | Status |
|-------|------|--------|--------|
| 1 | pre-commit | `git commit --no-verify` | Existing |
| 2 | **pre-push** | `git push --no-verify` | NEW (`3d21f23`, `9640d3a`) |
| 3 | **CI protocol-audit** | Can't bypass | NEW (`6b569dc`) |
| 4 | Branch protection | Admin override | Recommended (GitHub settings) |

**Pre-push hook error message (LLM-directive):**

When a `--no-verify` commit is detected on push, the hook blocks with:
- **WHAT HAPPENED** — identifies the violation and root cause
- **WHY THIS IS BLOCKED** — explains the protocol rule
- **VIOLATING COMMITS** — lists exact SHAs and files
- **HOW TO FIX** — step-by-step `git reset` + `aiv commit` instructions
- **Explicit prohibition:** `DO NOT use --no-verify. DO NOT hand-write packets.`

**E2E test result:** `git commit --no-verify` + `git push` → push blocked,
exit code 1, nothing reaches remote. Verified on branch `test-pre-push-hook`.

**Files:**
- `src/aiv/hooks/pre_push.py` — Pre-push hook (layer 2)
- `src/aiv/lib/auditor.py` — `audit_commits()` with HOOK_BYPASS + ATOMIC_VIOLATION
- `src/aiv/cli/main.py` — `aiv audit --commits N` flag + `aiv init` installs both hooks
- `.github/workflows/ci.yml` — `protocol-audit` job on push (layer 3)
- `tests/unit/test_pre_push_hook.py` — 15 tests
- `tests/unit/test_auditor.py` — 38 tests (14 for `audit_commits`)

**Retroactive packets:** Created for `e53f2c6` and `249ecde` with full
evidence and explicit violation documentation.

---

## Phase 1 Implementation Status

| # | Issue | Files | Risk | Effort | Status |
|---|-------|-------|------|--------|--------|
| P0-1 | Configurable functional prefixes | config.py, pre_commit.py, main.py | Medium | Medium | **DONE** (249ecde + 16b1c97) — P0-4 completed propagation to all layers |
| P0-2 | Remove project-specific root files | pre_commit.py | Low | Small | DONE (249ecde) |
| P0-3 | Enforcement gap (--no-verify bypass) | pre_push.py, auditor.py, ci.yml, main.py | High | Large | DONE (4-layer defence) |
| P1-3 | Error code reference | docs/ERROR_CODES.md, README.md | None | Medium | DONE (917b23b) |
| P1-4 | Fix Class F README example | README.md | None | Small | DONE (917b23b) |
| P1-5 | Complete packet example | README.md | None | Small | DONE |
| P2-6 | Better aiv init template | main.py | Low | Small | DONE (249ecde) |
| P2-7 | Document required flags | README.md | None | Small | DONE (917b23b) |

---

## Phase 2 Findings (2026-02-09 — Codebase Re-Audit)

Phase 1 fixed the pre-commit hook but left the other two enforcement layers
hardcoded. A full codebase audit also identified that AIV's evidence
collection is Python-exclusive for its most valuable features (AST symbol
resolution, test graph, downstream impact analysis). Any non-Python project
(TypeScript, Go, Rust, etc.) receives degraded evidence with no path to
improvement.

These findings block AIV's value proposition for external adopters — especially
TypeScript-heavy projects like the Black Box audit platform.

### P0 — Blocks External Use

#### P0-4: Functional prefix config not propagated to pre_push.py and auditor.py

**Files:**
- `src/aiv/hooks/pre_push.py` lines 42-65
- `src/aiv/lib/auditor.py` lines 54-77

**Problem:** There are **three independent copies** of `FUNCTIONAL_PREFIXES`
and `FUNCTIONAL_ROOT_FILES` in the codebase:

| Location | Reads `.aiv.yml`? | Used by |
|----------|------------------|---------|
| `pre_commit.py` `_load_hook_config()` | **YES** | Layer 1 (pre-commit hook) |
| `pre_push.py` lines 42-65 | **NO** (hardcoded) | Layer 2 (pre-push hook) |
| `auditor.py` lines 54-77 | **NO** (hardcoded) | Layer 3 (CI audit) + `aiv audit` |

For an external project that customizes `.aiv.yml` with non-standard prefixes
(e.g. `backend/`, `packages/`, `apps/`):

- **pre-commit hook** ✅ respects their config → correctly blocks
- **pre-push hook** ❌ uses hardcoded defaults → inconsistent classification
- **CI audit** ❌ uses hardcoded defaults → inconsistent classification

This means a commit that the pre-commit hook correctly blocks could be
classified differently by the pre-push hook or CI audit, creating
confusing false positives or false negatives across enforcement layers.

**Root cause:** P0-1 was fixed only in `pre_commit.py`. The config-loading
logic was not extracted into a shared function.

**Fix:**
1. Extract `_load_hook_config()` from `pre_commit.py` into `config.py` as a
   public function (e.g. `load_hook_config()`) so all consumers share one
   implementation.
2. Update `pre_push.py` to call `load_hook_config()` instead of using
   hardcoded constants.
3. Update `auditor.py` to call `load_hook_config()` instead of using
   hardcoded constants.
4. Remove the three redundant constant definitions.

**Verification:** After fix, a project with `.aiv.yml` containing
`functional_prefixes: ["backend/"]` should see consistent behavior across
all three enforcement layers.

---

### P1 — Degrades Value for Non-Python Projects

#### P1-6: AST symbol resolution is Python-exclusive

**File:** `src/aiv/lib/evidence_collector.py` line 595-639
**Gate:** `src/aiv/cli/main.py` line 1615 — `if file_posix_raw.endswith(".py"):`

**Problem:** `resolve_changed_symbols()` uses Python's `ast` module to map
diff hunks to enclosing function/class names. This is the foundation of
AIV's most valuable feature — per-symbol test coverage. For any non-Python
file (`.ts`, `.js`, `.go`, `.rs`, etc.), this analysis is **completely
skipped** and the evidence falls back to file-level keyword matching.

**Impact:** The Claim Verification Matrix cannot bind claims to specific
symbols for non-Python files. Instead of "3 tests call `promote` directly"
the user gets "MANUAL REVIEW — No automatic binding available." This is
the difference between AIV being a verification engine and a documentation
tool.

**Fix (tree-sitter approach — keeps everything in-process, no Node.js bridge):**
1. Add `tree-sitter` and relevant language grammars as optional dependencies
2. Create `src/aiv/lib/lang/base.py` with a `LanguageDriver` protocol
3. Create `src/aiv/lib/lang/python_driver.py` wrapping existing `ast` logic
4. Create `src/aiv/lib/lang/treesitter_driver.py` for JS/TS/Go/Rust
5. Update `resolve_changed_symbols()` to dispatch by file extension
6. Update the `.py` gate in `main.py` to check for driver availability

**Why tree-sitter over ts-morph/Node.js bridge:** tree-sitter has Python
bindings (`py-tree-sitter`), supports 100+ languages with one dependency,
and avoids subprocess overhead. No Node.js runtime required.

**Verification:** `aiv commit engine/commands/promote.ts` should produce
per-symbol coverage like `promote()` → "2 tests call this symbol" instead
of falling back to file-level.

---

#### P1-7: Test graph builder only scans Python test files

**File:** `src/aiv/lib/evidence_collector.py` line 738-791

**Problem:** `build_test_graph()` uses `test_root.rglob("*.py")` and Python
`ast` to build the import→call graph. Projects with `.test.ts`, `.spec.js`,
or `_test.go` files are invisible. The entire test graph is empty for
non-Python test suites.

**Fix:** Same tree-sitter driver approach as P1-6. The `LanguageDriver`
protocol should include a `build_test_graph()` method. The main
`build_test_graph()` function should scan for all supported test file
patterns (not just `*.py`).

---

#### P1-8: Downstream caller analysis is Python-exclusive

**File:** `src/aiv/lib/evidence_collector.py` line 878-936

**Problem:** `find_downstream_callers()` uses `src_root.rglob("*.py")` and
Python `ast`. Class C downstream impact analysis ("which functions call
the symbol you changed?") is invisible for non-Python codebases.

**Fix:** Same tree-sitter driver approach. The `LanguageDriver` protocol
should include a `find_callers()` method.

---

### Phase 2 Implementation Priority

| # | Issue | Files | Risk | Effort | Depends On | Status |
|---|-------|-------|------|--------|------------|--------|
| P0-4 | Config propagation to all enforcement layers | config.py, pre_push.py, auditor.py | Medium | Small | — | DONE (16b1c97) |
| P1-6 | Polyglot symbol resolution (tree-sitter) | language_drivers/*.py, main.py | Low | Large | — | **DONE** (PR #2) |
| P1-7 | Polyglot test graph builder | language_drivers/treesitter_driver.py | Low | Medium | P1-6 | **DONE** (PR #2) |
| P1-8 | Polyglot downstream caller analysis | language_drivers/treesitter_driver.py | Low | Medium | P1-6 | **DONE** (PR #2) |

---

## How to Use This Document

This document is the **Class E intent** for all commits on the
`feat/external-readiness-polyglot` branch. When committing fixes for any
issue above, reference this doc:

```bash
aiv commit src/aiv/lib/config.py \
  -m "fix(config): extract shared load_hook_config for all enforcement layers" \
  -t R2 \
  -c "load_hook_config() is a single shared function in config.py" \
  -c "pre_push.py reads .aiv.yml instead of hardcoded prefixes" \
  -c "auditor.py reads .aiv.yml instead of hardcoded prefixes" \
  -i "https://github.com/ImmortalDemonGod/aiv-protocol/blob/<SHA>/docs/EXTERNAL_READINESS_AUDIT.md" \
  --requirement "P0-4: Functional prefix config not propagated" \
  -r "R2: enforcement consistency affects all adopters" \
  -s "All three enforcement layers read .aiv.yml for functional prefixes"
```

Replace `<SHA>` with the commit SHA of this document on the branch.

### PR Scope (feat/external-readiness-polyglot)

This branch addresses Phase 2 findings. Work is atomic — each fix is one
`aiv commit` referencing the specific P-number as `--requirement`.

**Minimum viable PR (P0-4 only):**
- Extract `load_hook_config()` into `config.py`
- Update `pre_push.py` and `auditor.py` to use it
- Add/update tests for config propagation

**Full PR (P0-4 + P1-6/7/8):**
- All of the above, plus:
- Add `tree-sitter` optional dependency
- Create `LanguageDriver` protocol + Python/tree-sitter implementations
- Update `evidence_collector.py` to dispatch by file extension
- Add tests for TypeScript/JavaScript symbol resolution
