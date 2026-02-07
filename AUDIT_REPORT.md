# AIV Protocol — Codebase Audit Report

**Original Date:** 2026-02-06  
**Re-Audit Date:** 2026-02-06 (later session, same day)  
**Auditor:** Cascade (Senior Software Engineer role)  
**Scope:** Full Python implementation in `src/aiv/`, `src/svp/`, tests in `tests/`, CI workflows, pre-commit hook  
**Method:** Static analysis, code tracing, execution verification (163/163 tests pass)  
**Previous baseline:** 39 tests, 22 Python source files, ~2,318 lines  
**Current baseline:** 163 tests, 32 Python source files, ~6,500+ lines

> **Re-Audit Note:** This report has been updated in-place. Each finding now
> includes a **Status** tag: ✅ FIXED, ⚠️ PARTIALLY FIXED, ❌ STILL PRESENT,
> or 🆕 NEW FINDING. A consolidated delta summary appears in §8.

---

## 1. Overview of the Codebase

### 1.1 Directory Structure

```
aiv-protocol/
├── src/aiv/                          # Python package (aiv-lib + aiv-cli + aiv-guard)
│   ├── __init__.py                   # Package root, exports __version__ = "1.0.0"
│   ├── __main__.py                   # Entry point for `python -m aiv`
│   ├── py.typed                      # PEP 561 typed marker
│   ├── cli/
│   │   ├── __init__.py
│   │   └── main.py                   # Typer CLI: check, init, generate commands (366 lines)
│   ├── guard/                        # 🆕 Python AIV Guard (replaced dead security.py)
│   │   ├── __init__.py
│   │   ├── __main__.py               # Entry point for `python -m aiv.guard`
│   │   ├── models.py                 # Guard data models (215 lines)
│   │   ├── github_api.py             # GitHub REST API client (196 lines)
│   │   ├── canonical.py              # Canonical JSON packet validator (522 lines)
│   │   ├── manifest.py               # Manifest handling (211 lines)
│   │   └── runner.py                 # Guard orchestrator (427 lines)
│   └── lib/
│       ├── __init__.py
│       ├── config.py                 # Pydantic configuration models (152 lines)
│       ├── errors.py                 # Exception hierarchy (69 lines)
│       ├── models.py                 # Core Pydantic models (381 lines)
│       ├── parser.py                 # Markdown packet parser (516 lines)
│       ├── analyzers/
│       │   └── __init__.py           # ✅ diff.py removed (was dead code)
│       └── validators/
│           ├── __init__.py
│           ├── base.py               # ABC for validators (44 lines, Protocol removed)
│           ├── anti_cheat.py         # Test manipulation detection (198 lines)
│           ├── evidence.py           # Evidence class-specific validation (280 lines)
│           ├── links.py              # URL immutability checking (100 lines)
│           ├── pipeline.py           # Orchestrator + risk-tier enforcement (252 lines)
│           ├── structure.py          # Packet structural completeness (76 lines)
│           └── zero_touch.py         # Zero-Touch compliance checking (202 lines)
├── src/svp/                          # 🆕 SVP Protocol Suite (cognitive verification)
│   ├── __init__.py
│   ├── cli/
│   │   ├── __init__.py
│   │   └── main.py                   # SVP CLI: status/predict/trace/probe/validate
│   └── lib/
│       ├── __init__.py
│       ├── models.py                 # SVP Pydantic models (phases 0-4, session, rating)
│       └── validators/
│           ├── __init__.py
│           └── session.py            # SVP session validator (rules S001-S013)
├── tests/
│   ├── conftest.py                   # Shared fixtures (286 lines)
│   ├── unit/
│   │   ├── test_models.py            # Model unit tests (270 lines)
│   │   ├── test_parser.py            # 🆕 Parser unit tests (251 lines)
│   │   ├── test_validators.py        # 🆕 Validator unit tests (382 lines)
│   │   ├── test_guard.py             # 🆕 Guard unit tests (36 tests)
│   │   └── test_svp.py              # 🆕 SVP unit tests (43 tests)
│   └── integration/
│       └── test_full_workflow.py      # Pipeline integration tests
├── .github/
│   ├── workflows/
│   │   ├── aiv-guard.yml             # CI PR validation (2243 lines, JS — preserved)
│   │   ├── aiv-guard-python.yml      # 🆕 Python guard workflow (45 lines)
│   │   └── verify-architecture.yml   # CI build/evidence generation
│   ├── aiv-packets/                  # 30 verification packet files (was 13)
│   └── PULL_REQUEST_TEMPLATE.md
├── .husky/
│   └── pre-commit                    # Atomic commit enforcer (shell)
├── docs/specs/                       # Canonical specification documents
├── pyproject.toml                    # Build config, dependencies
├── SPECIFICATION.md                  # Canonical AIV spec v1.0.0
└── README.md
```

**Total Python source:** ~4,700+ lines across 32 files (was ~2,318 across 22)  
**Total test code:** ~2,600+ lines across 7 test files (was ~705 across 3)  
**CI workflows:** aiv-guard.yml (JS, preserved) + aiv-guard-python.yml (45 lines, new)

### 1.2 Entry Points

1. **CLI:** `aiv check <packet>` / `aiv init <path>` / `aiv generate <name>` — via `src/aiv/cli/main.py:app` (Typer)
2. **SVP CLI:** `aiv svp status/predict/trace/probe/validate` — via `src/svp/cli/main.py:svp_app`, integrated into main CLI
3. **Module:** `python -m aiv` — via `src/aiv/__main__.py`
4. **Guard Module:** `python -m aiv.guard` — via `src/aiv/guard/__main__.py` (🆕)
5. **Console script:** `aiv` — registered in `pyproject.toml` → `aiv.cli.main:app`
6. **CI (JS):** `.github/workflows/aiv-guard.yml` — standalone JavaScript (preserved)
7. **CI (Python):** `.github/workflows/aiv-guard-python.yml` — uses Python guard module (🆕)
8. **Pre-commit:** `.husky/pre-commit` — standalone shell, does NOT use the Python package

### 1.3 High-Level Architecture

**Pattern:** Pipeline architecture with plugin-style validators.

```
CLI (Typer)
  └─→ ValidationPipeline
        ├─→ PacketParser         (markdown → VerificationPacket)
        ├─→ StructureValidator   (completeness checks)
        ├─→ LinkValidator        (URL immutability)
        ├─→ EvidenceValidator    (class-specific rules)
        ├─→ ZeroTouchValidator   (reproduction compliance)
        └─→ AntiCheatScanner     (diff analysis, optional)
```

All validators implement `BaseValidator.validate(packet) → list[ValidationFinding]`. The pipeline collects findings, distributes them by severity (block/warn/info), and determines pass/fail based on strict mode.

**Data flow is strictly unidirectional:** markdown string → parsed packet → findings → result. Models are frozen (immutable). No shared mutable state between validators.

---

## 2. Functional Modules

### 2.1 `models.py` — Core Data Models (381 lines, was 352)

**Stated purpose:** Immutable Pydantic models for the AIV domain.

**Actual behavior — verified:**
- `EvidenceClass` enum maps A–F correctly. `from_string()` handles letter, name, and prefix formats. Case-insensitive.
- `ArtifactLink.from_url()` classifies URLs into 4 types: `github_blob`, `github_actions`, `github_pr`, `external`. SHA detection works for 7+ hex chars. 🆕 Now accepts `mutable_branches` and `min_sha_length` parameters — config is respected.
- `Claim`, `IntentSection`, `VerificationPacket` are all frozen. `VerificationPacket.all_links` correctly filters for `ArtifactLink` instances.
- `ValidationFinding.rule_id` enforced by regex `^E\d{3}$`.
- 🆕 `RiskTier` enum added (R0–R3) with `from_string()`.
- 🆕 `VerificationPacket.risk_tier` and `evidence_classes_present` fields added.
- `ValidationResult.validated_at` uses `datetime.now(timezone.utc)`.

**Inconsistencies found:**
- ✅ FIXED: **DEAD IMPORT: `Annotated`** — removed.
- ✅ FIXED: **DEAD IMPORT: `field_validator`** — removed.
- ✅ FIXED: **DEAD IMPORT: `model_validator`** — removed.
- ✅ FIXED: **DEPRECATION: `datetime.utcnow()`** — replaced with `datetime.now(timezone.utc)` at line 321.
- ❌ STILL PRESENT: **NAMING INCONSISTENCY:** `EvidenceClass.CONSERVATION` (value "F") is documented as "Conservation (non-regression)" in the docstring, but the spec calls Class F "Provenance" in the template and `SPECIFICATION.md`. The model's docstring says "F: Conservation (non-regression)" while the canonical spec says "F: Provenance — Content-addressed integrity." These are different concepts. The `generate` command (cli/main.py:337) labels it "Conservation Evidence" rather than "Provenance."

### 2.2 `parser.py` — Markdown Parser (516 lines, was 453)

**Stated purpose:** Convert markdown verification packets into structured `VerificationPacket` objects.

**Actual behavior — verified against 30 real packets:**
- Section extraction via heading detection works correctly.
- Intent parsing: tries `### Class E` first (level 3), falls back to legacy `## 0. Intent Alignment`. Extracts `**Link:**` and `**Requirements Verified:**` fields via regex.
- Claim parsing: extracts numbered list items from `## Claim(s)` section. Minimum description length enforced (10 chars).
- Evidence enrichment: maps `### Class X` sections to claims via `Claim N:` references. Unlinked evidence now uses best-match logic.
- 🆕 `_parse_classification()` extracts `risk_tier` from `## Classification (required)` YAML block via regex.
- 🆕 `_collect_evidence_classes()` scans all `### Class X` sections and populates `evidence_classes_present`.
- 🆕 `## Verification Methodology` content is extracted as the `reproduction` field for all claims (instead of hardcoding `"N/A"`).

**Inconsistencies found:**
- ✅ FIXED: **DEAD METHOD: `_find_sections()`** — removed entirely. Only `_find_section()` (singular) exists.
- ❌ STILL PRESENT: **STATEFUL PARSER:** `PacketParser.errors` is an instance variable reset in `parse()`. This means the parser is **not thread-safe** and repeated calls clobber previous errors. The pipeline reads `self.parser.errors` after `parse()`, so this works in practice, but if the parser were reused concurrently it would fail.
- ✅ FIXED: **FIRST-ONLY UNLINKED EVIDENCE:** Now at lines 480-489, unlinked evidence uses best-match logic: prefers evidence whose class matches the claim's default, then falls back to the first available. This is a meaningful improvement — claims with matching evidence class get the right evidence.
- ❌ STILL PRESENT: **LEGACY PARSER UNTESTED:** `_build_intent_from_legacy()` (lines 308-342) handles `## 0. Intent Alignment` format, but no real packet uses this format and no test exercises it. Dead code path.
- ❌ STILL PRESENT: **VERSION FALLBACK:** If the header lacks a version (e.g., `# AIV Verification Packet`), version defaults to `"2.1"` (line 101). This is an assumption, not a parsing result.

### 2.3 `config.py` — Configuration Models (152 lines)

**Stated purpose:** Pydantic-based configuration for all validators.

**Actual behavior — verified:**
- `AIVConfig` extends `pydantic_settings.BaseSettings` with `env_prefix="AIV_"`.
- `from_file()` loads YAML via PyYAML (lazy import).
- Sub-configs: `ZeroTouchConfig`, `AntiCheatConfig`, `MutableBranchConfig` with sensible defaults.

**Inconsistencies found:**
- ❌ STILL PRESENT: **YAML IMPORT NOT GUARDED:** `from_file()` does `import yaml` inside the method. If PyYAML isn't installed, this raises `ModuleNotFoundError` at call time, not import time. But PyYAML IS listed as a required dependency, so this is a style issue rather than a bug.
- ⚠️ PARTIALLY FIXED: **`fast_track_patterns` UNUSED:** `AIVConfig.fast_track_patterns` (line 128) is still defined in config but never consulted by the pipeline or CLI. However, the `guard/runner.py` has its own `FAST_TRACK_EXT` and `FAST_TRACK_NAMES` constants (lines 71-72) — so fast-track logic now exists in the guard module but doesn't use this config field. The config field remains dead in `aiv-lib`.
- ✅ FIXED: **`MutableBranchConfig` DUPLICATED:** `ArtifactLink.from_url()` now accepts `mutable_branches` and `min_sha_length` parameters (line 95-96). `LinkValidator.validate_packet_links()` re-checks blob links using `self.config.mutable_branches` and `self.config.min_sha_length` (lines 79-83). Config is now respected.

### 2.4 `errors.py` — Exception Hierarchy (69 lines)

**Stated purpose:** Exception classes for distinct failure modes.

**Actual behavior — verified:**
- Clean hierarchy: `AIVError` → `PacketParseError`, `PacketValidationError`, `ConfigurationError`, `GitHubAPIError`, `EvidenceResolutionError`.
- Each exception has appropriate metadata fields (rule_id, status_code, url).

**Inconsistencies found:**
- ❌ STILL PRESENT: **4 of 5 exceptions are NEVER RAISED:** Only `PacketParseError` is used (in `parser.py`). The other four — `PacketValidationError`, `ConfigurationError`, `GitHubAPIError`, `EvidenceResolutionError` — are defined but never imported or raised anywhere in the codebase. The guard module (`github_api.py`) catches `HTTPError` from `urllib` directly rather than wrapping it in `GitHubAPIError`. These remain speculative infrastructure.

### 2.5 `guard/` — ✅ REPLACED: Now a Full Python Guard Module

**Previous state:** `guard/security.py` — 82 lines of dead code (5 unused functions).

**Current state:** ✅ FIXED — `security.py` has been **deleted entirely** and replaced with a complete Python Guard module (6 files, ~1,571 lines total):
- `models.py` (215 lines) — `GuardContext`, `GuardResult`, `GuardFinding`, `EvidenceClassResult`, regex helpers
- `github_api.py` (196 lines) — Minimal GitHub REST API client using only `urllib` (no deps)
- `canonical.py` (522 lines) — Canonical JSON packet validator (replaces core JS guard logic)
- `manifest.py` (211 lines) — Manifest handling
- `runner.py` (427 lines) — Full guard orchestrator with 9-stage pipeline
- `__main__.py` — Entry point for `python -m aiv.guard`

**Key improvements over previous state:**
- Guard module now **uses `aiv-lib` pipeline** internally (`runner.py:215` calls `ValidationPipeline`)
- GitHub API client fetches PR files, workflow runs, CI artifacts
- Critical surface detection ported from JS guard (path + semantic patterns)
- Fast-track detection for docs-only changes
- Canonical JSON validation (required fields, immutability, SoD, attestations)
- CI artifact inspection (Class A run URL verification, aiv-evidence artifact check)
- 36 unit tests in `tests/unit/test_guard.py`

**New inconsistencies found:**
- 🆕 **GUARD USES OWN FAST-TRACK LOGIC:** `runner.py` defines `FAST_TRACK_EXT` and `FAST_TRACK_NAMES` (lines 71-72) independently of `AIVConfig.fast_track_patterns`. Two separate fast-track definitions exist.
- 🆕 **GUARD MODELS USE DATACLASSES, NOT PYDANTIC:** Guard models (`models.py`) use plain `@dataclass` rather than Pydantic `BaseModel`. This is intentional (minimal deps for CI), but means guard models lack Pydantic validation that `aiv-lib` models have.

### 2.6 `analyzers/diff.py` — ✅ DELETED (was 166 lines of dead code)

**Previous state:** Entire module was dead code — never imported or used.

**Current state:** ✅ FIXED — `diff.py` has been **deleted**. The `analyzers/` directory now contains only `__init__.py` (6 lines). Critical surface detection functionality has been re-implemented in `guard/runner.py` (lines 37-68) with proper file tracking per pattern match.

### 2.7 `validators/base.py` — Validator Interface (44 lines, was 67)

**Stated purpose:** ABC defining the validator interface.

**Actual behavior — verified:**
- `BaseValidator` is an ABC with `validate()` and `_make_finding()` helper.

**Inconsistencies found:**
- ✅ FIXED: **PROTOCOL IS UNUSED / DUAL ABSTRACTION:** The `Validator` protocol and `runtime_checkable` import have been removed. Only the `BaseValidator` ABC remains (44 lines, down from 67). Clean single abstraction.

### 2.8 `validators/exceptions.py` — ✅ DELETED (was 220 lines of dead code)

**Previous state:** Entire module was dead code — 3 handler classes, 0 callers.

**Current state:** ✅ FIXED — `exceptions.py` has been **deleted entirely**. Fast-track logic now lives in `guard/runner.py` (lines 107-118). Bootstrap and flake report handlers were not re-implemented — their functionality was not needed for the current validation workflow.

### 2.9 `validators/pipeline.py` — Validation Pipeline (252 lines, was 181)

**Stated purpose:** Orchestrates all validators in sequence.

**Actual behavior — verified by execution:**
- 8-stage pipeline: Parse → Structure → Links → Evidence → Risk-Tier Requirements → Zero-Touch → Anti-Cheat → Cross-Reference.
- Anti-cheat only runs if diff is provided. Cross-reference checks unjustified findings.
- Strict mode: warnings become failures.
- 🆕 **Risk-tier enforcement** implemented via `_check_tier_requirements()` (lines 187-235). Uses `_TIER_REQUIRED` and `_TIER_OPTIONAL` dicts mapping `RiskTier` → required/optional `EvidenceClass` sets. Missing required classes produce BLOCK findings; missing optional classes produce INFO findings.

**Inconsistencies found:**
- ✅ FIXED: **EXCEPTION HANDLERS NOT INTEGRATED:** `exceptions.py` was deleted. Fast-track logic now lives in `guard/runner.py`. The pipeline's responsibility is narrower and cleaner.
- ❌ STILL PRESENT: **BROAD EXCEPTION CATCH:** Stage 1 parse (line 98) still catches `Exception` instead of `PacketParseError`. This masks unexpected errors (e.g., Pydantic validation errors, regex errors) behind a generic E001 message.
- 🆕 **E014 RULE ID OVERLOADED:** `_check_tier_requirements()` uses rule ID `E014` for three different meanings: (1) missing classification section (WARN), (2) missing required evidence class (BLOCK), and (3) missing optional evidence class (INFO). While less ambiguous than the old E007 collision (4 different rules), findings within E014 require reading the message text to distinguish the specific violation.

### 2.10 `validators/structure.py` — Structure Validator (76 lines)

**Stated purpose:** Validates packet structural completeness.

**Actual behavior — verified:**
- Checks `verifier_check` minimum length (10 chars).
- Checks claim description minimum length (15 chars — stricter than parser's 10 char check).
- Checks reproduction field exists and isn't whitespace.

**Inconsistencies found:**
- ❌ STILL PRESENT: **DUAL LENGTH THRESHOLDS:** The parser skips claims with description < 10 chars (line 366), but the structure validator warns on claims with description < 15 chars (line 50). A 12-char description passes the parser but gets a warning from the structure validator. This dual threshold is confusing.
- ⚠️ PARTIALLY FIXED: **REPRODUCTION CHECK:** The parser now extracts `## Verification Methodology` content as the `reproduction` field (lines 457-462), defaulting to `"N/A"` only when absent. The structure validator's empty-check (line 63) can now trigger if a packet has an empty Verification Methodology section. However, the check still validates the parser's extraction rather than the raw packet content — if the methodology section exists but is whitespace, the parser sets `reproduction` to `"N/A"` (line 460 falls through), so the check remains vacuous in that edge case.

### 2.11 `validators/evidence.py` — Evidence Validator (262 lines)

**Stated purpose:** Class-specific evidence validation rules.

**Actual behavior — verified:**
- Dispatches to 6 class-specific validators (A–F).
- Bug fix heuristic (`_is_bug_fix`) checks for keywords in intent and claim descriptions.

**Inconsistencies found:**
- ✅ FIXED: **RULE ID COLLISION: E007** — Resolved. Each evidence class now has its own unique rule IDs: E015 (Class B non-blob), E016 (Class B missing file ref), E017 (Class C negative framing), E018 (Class D manual DB). Rule IDs are now unambiguous.
- ✅ FIXED: **BUG FIX HEURISTIC FALSE POSITIVES:** `_is_bug_fix()` (lines 254-279) now uses word-boundary regex patterns (`\bfix(?:ed|es|ing)?\b`, `\bissue\s*#?\d+`, etc.) instead of substring matching. "prefix" no longer triggers "fix"; "tissue" no longer triggers "issue". Tested with 7 unit tests in `test_validators.py::TestBugFixHeuristic`.
- ❌ STILL PRESENT: **CLASS A VALIDATION MOSTLY EMPTY:** `_validate_execution()` (lines 73-110) still only checks sub-conditions when the artifact is a non-CI URL AND the description mentions "performance" or "ui/visual". For the common case (CI link or string artifact), it returns no findings. Class A validation is effectively a no-op for most claims. Rule IDs used are E012 and E013.

### 2.12 `validators/links.py` — Link Validator (138 lines)

**Stated purpose:** URL immutability checking per Addendum 2.2.

**Actual behavior — verified:**
- Validates intent link immutability (Class E). Plain text → info. Mutable URL → block.
- Validates claim artifact links. Mutable github_blob → block.

**Inconsistencies found:**
- ✅ FIXED: **`validate_link_format()` IS DEAD CODE:** Removed entirely. `links.py` is now 100 lines (was 138). Only `validate()` → `validate_packet_links()` remains.
- ❌ STILL PRESENT: **NO NETWORK VALIDATION:** Comments mention "Links should be accessible (optional, requires network)" (line 40) but no network checks exist. All validation is structural/heuristic.
- ✅ FIXED: **CONFIG NOT USED FOR IMMUTABILITY:** `LinkValidator.validate_packet_links()` now re-checks blob/tree links using `self.config.mutable_branches` and `self.config.min_sha_length` (lines 79-83). Config is fully wired through.

### 2.13 `validators/zero_touch.py` — Zero-Touch Validator (202 lines, was 174)

**Stated purpose:** Ensures reproduction instructions don't require local execution.

**Actual behavior — verified:**
- Matches reproduction text against prohibited patterns (git, npm, python, docker, etc.) and allowed patterns (N/A, CI Automation, URLs, etc.).
- Calculates friction score per claim and aggregate per packet.
- Produces BLOCK for prohibited patterns, WARN for high step count.
- 🆕 Strips fenced code blocks (```` ```...``` ````) before checking prohibited patterns (line 96). This prevents false positives from informational command examples in methodology sections.
- 🆕 Recognizes explicit zero-touch compliance phrases (e.g., "zero-touch mandate", "verifier inspects artifacts only") as early-exit (lines 82-91).

**Inconsistencies found:**
- ✅ FIXED: **ALWAYS PASSES IN PRACTICE:** The parser now extracts `## Verification Methodology` content as the `reproduction` field (parser.py lines 457-462). Real packets with methodology content like "**Zero-Touch Mandate:** Verifier inspects artifacts only" are correctly parsed and validated. The validator can now find violations when methodology sections contain prohibited patterns outside code blocks. Tested with 5 unit tests in `test_validators.py::TestZeroTouchCodeBlockStripping`.
- ✅ FIXED: **DEPRECATED IMPORT:** Now uses `from re import Pattern` (line 10) instead of `from typing import Pattern`.

### 2.14 `validators/anti_cheat.py` — Anti-Cheat Scanner (196 lines)

**Stated purpose:** Detects test manipulation in git diffs.

**Actual behavior — verified by test execution:**
- Scans diff for deleted assertions, added skip decorators, mock/bypass flags, removed test files.
- Cross-references findings against packet claims for Class F justification.

**Inconsistencies found:**
- ❌ STILL PRESENT: **LINE NUMBER TRACKING BUG:** At lines 133-137, line counting logic increments `current_line` for added lines and context lines. The `@@` hunk header resets it. This is approximately correct but imprecise for multi-hunk files where additions span many lines.
- ✅ FIXED: **REMOVED FILE DETECTION BUG:** The regex (lines 141-143) now correctly matches `diff --git a/X b/X` BEFORE `deleted file mode` — matching real unified diff order. Pattern: `r"diff --git a/([^\s]+) b/[^\s]+\n(?:old|new|deleted|index|similarity|rename|copy)[^\n]*\ndeleted file mode \d+"`. This can now detect deleted test files.
- ✅ FIXED: **DEPRECATED IMPORT:** Now uses `from re import Pattern` (line 10) instead of `from typing import Pattern`.

### 2.15 `cli/main.py` — CLI Application (366 lines, was 170)

**Stated purpose:** Typer CLI with `check`, `init`, and `generate` commands.

**Actual behavior — verified by execution:**
- `check`: reads packet from file/argument/stdin, runs pipeline, displays results with Rich tables.
- `init`: creates `.aiv.yml` config file.
- 🆕 `generate`: creates a pre-filled packet scaffold with classification, claim stubs, and evidence sections appropriate for the chosen risk tier. Includes git scope detection (`_detect_git_scope()` runs `git diff --cached --name-status`).
- 🆕 SVP CLI integrated via `app.add_typer(svp_app, name="svp")` at line 28.

**Inconsistencies found:**
- ✅ FIXED: **UNUSED IMPORTS:** CLI now only imports `ValidationStatus`, `ValidationFinding`, `ValidationPipeline`, `AIVConfig`, and `svp_app`. Individual validators and `Severity` are no longer imported.
- ⚠️ PARTIALLY FIXED: **`init` IS MINIMAL:** Docstring now correctly says "Creates: .aiv.yml configuration file" (line 125) — the false "Verification packet template" claim has been removed. However, users wanting a packet template must use `aiv generate` separately; `init` doesn't mention this.
- ❌ STILL PRESENT: **FROZEN MODEL MUTATION:** At line 64, `cfg.strict_mode = strict` still mutates the `AIVConfig` object. `AIVConfig` is a `BaseSettings` (not frozen), so this works but remains a code smell.
- 🆕 **SVP IMPORT PATH:** Line 21 imports `from svp.cli.main import svp_app`. This assumes `src/svp` is on the Python path (configured via `pyproject.toml` `pythonpath = ["src"]`). This import will fail in any environment where the package is installed via pip but the svp package isn't in the same wheel — currently `tool.hatch.build.targets.wheel.packages` includes both `src/aiv` and `src/svp` (pyproject.toml line 57), so this works, but it's fragile coupling between two packages.

---

## 3. Execution Trace

### 3.1 Scenario: `python -m aiv check .github/aiv-packets/VERIFICATION_PACKET_PRECOMMIT.md`

**Input:** Path to a real verification packet file.

**Step-by-step call chain:**

1. **`__main__.py`** → calls `app()` (Typer)
2. **`cli/main.py:check()`** → receives `body=".github/aiv-packets/VERIFICATION_PACKET_PRECOMMIT.md"`
3. **Config load:** `AIVConfig()` with defaults → `strict_mode=True`
4. **File read:** `Path(body).exists()` → True → reads file as UTF-8 string
5. **Pipeline creation:** `ValidationPipeline(cfg)` → initializes all 6 validators
6. **`pipeline.validate(body_text, diff=None)`** →

   **Stage 1 — Parse:**
   - `PacketParser.parse(markdown_text)` →
   - `_extract_sections()` → splits markdown into `ParsedSection` objects by heading level
   - `_parse_intent()` → finds `### Class E (Intent Alignment)`, extracts `**Link:**` field → plain text "AIV Protocol §2.0..." → `IntentSection(evidence_link="AIV Protocol §2.0...", verifier_check="...")`
   - `_parse_claims()` → finds `## Claim(s)`, extracts 5 numbered items → 5 `Claim` objects with default `evidence_class=REFERENTIAL`, `artifact="See Evidence section"`, `reproduction="N/A"`
   - `_enrich_claims_with_evidence()` →
     - Finds `### Class B`, `### Class A` subsections
     - Class E skipped (intent handled separately)
     - Class B has no `Claim N:` references → goes to `unlinked_evidence`
     - Class A has no `Claim N:` references → goes to `unlinked_evidence`
     - All 5 unenriched claims get `unlinked_evidence[0]` = Class B content
   - Returns `VerificationPacket(version="2.1", intent=..., claims=[5 claims], raw_markdown=...)`

   **Stage 2 — Structure:**
   - `StructureValidator.validate(packet)` → checks verifier_check length (OK), claim descriptions (all >15 chars), reproduction ("N/A" is non-empty) → **0 findings**

   **Stage 3 — Links:**
   - `LinkValidator.validate(packet)` → intent link is `str` → **1 INFO finding (E004)**
   - No claim artifacts are `ArtifactLink` → no further checks

   **Stage 4 — Evidence:**
   - `EvidenceValidator.validate(packet)` → all 5 claims have `evidence_class=REFERENTIAL` (Class B) → `_validate_referential()` → artifact is `str` containing "Created" keyword → **0 findings**
   - `_is_bug_fix()` → no "fix/bug/issue" keywords → no E010

   **Stage 5 — Zero-Touch:**
   - `ZeroTouchValidator.validate(packet)` → all 5 claims have `reproduction="N/A"` → matches `^N/?A$` → **0 findings**

   **Stage 6 — Anti-Cheat:**
   - `diff=None` → **skipped**

   **Final determination:**
   - `strict_mode=True`, errors=0, warnings=0, info=1 → `status=PASS`

7. **CLI output:** Rich panel showing "Validation Passed, Packet version: 2.1, Claims: 5"

**State mutations:** Only `PacketParser.errors` (reset at parse start). All models are frozen. Pipeline creates new `ValidationResult` without mutating inputs.

---

## 4. Critical Findings

### 4.1 Logical Flaws

| ID | Severity | Location | Description | Status |
|----|----------|----------|-------------|--------|
| L01 | **HIGH** | `anti_cheat.py:140-143` | Removed test file detection regex was inverted. | ✅ FIXED — regex now matches `diff --git` before `deleted file mode` |
| L02 | **HIGH** | `parser.py:480-489` | Unlinked evidence only applied first match. | ✅ FIXED — best-match logic prefers class-matching evidence |
| L03 | **MEDIUM** | `evidence.py:254-279` | Bug fix heuristic false positives on "prefix", "tissue". | ✅ FIXED — now uses word-boundary regex patterns, 7 tests |
| L04 | **MEDIUM** | `evidence.py` | Rule ID E007 used for 4 different rules. | ✅ FIXED — unique IDs: E015, E016, E017, E018 |
| L05 | **MEDIUM** | `zero_touch.py` + `parser.py:457-462` | Zero-touch validator structurally a no-op. | ✅ FIXED — parser extracts methodology content, code blocks stripped |
| L06 | **LOW** | `analyzers/diff.py` | Critical surface detection misattributed to last file. | ✅ FIXED — module deleted; re-implemented correctly in guard/runner.py |
| L07 | **LOW** | `models.py:321` | `datetime.utcnow()` deprecated. | ✅ FIXED — uses `datetime.now(timezone.utc)` |
| L08 | **LOW** | `models.py:95-96` | Mutable branch config never consulted. | ✅ FIXED — `ArtifactLink.from_url()` accepts config params; `LinkValidator` passes them |
| L09 | 🆕 **LOW** | `pipeline.py:98` | Broad `except Exception` catch masks non-parse errors. | ❌ STILL PRESENT |
| L10 | 🆕 **LOW** | `pipeline.py:212-214` | E014 rule ID overloaded for 3 different tier-check meanings. | 🆕 NEW |
| L11 | 🆕 **LOW** | `anti_cheat.py:133-137` | Line number tracking imprecise for multi-hunk diffs. | ❌ STILL PRESENT |
| L12 | 🆕 **LOW** | `parser.py:308-342` | Legacy intent parser (`_build_intent_from_legacy`) untested dead code path. | ❌ STILL PRESENT |

### 4.2 Dead Code

| ID | Module | Lines | Description | Status |
|----|--------|-------|-------------|--------|
| D01 | `guard/security.py` | 82 | **Entire module** — 5 functions, 0 callers | ✅ DELETED — replaced with full guard module |
| D02 | `analyzers/diff.py` | 166 | **Entire module** — `DiffAnalyzer` never used | ✅ DELETED — functionality in guard/runner.py |
| D03 | `validators/exceptions.py` | 220 | **Entire module** — 3 handler classes, 0 callers | ✅ DELETED — fast-track in guard/runner.py |
| D04 | `errors.py` | ~47 | 4 of 5 exceptions never raised | ❌ STILL PRESENT — guard uses urllib errors directly |
| D05 | `models.py:12,20-21` | 3 | Unused imports: `Annotated`, `field_validator`, `model_validator` | ✅ FIXED — removed |
| D06 | `cli/main.py:18-24` | 7 | Unused imports: individual validators, `Severity` | ✅ FIXED — removed |
| D07 | `parser.py:179-190` | 12 | `_find_sections()` method never called | ✅ FIXED — removed |
| D08 | `links.py:99-137` | 39 | `validate_link_format()` method never called | ✅ FIXED — removed |
| D09 | `parser.py:308-342` | 35 | `_build_intent_from_legacy()` never exercised | ❌ STILL PRESENT |
| D10 | `base.py:15-34` | 20 | `Validator` Protocol never checked | ✅ FIXED — removed |
| D11 | 🆕 `config.py:128-138` | 11 | `fast_track_patterns` field never used by pipeline | 🆕 NEW |
| D12 | 🆕 `analyzers/__init__.py` | 6 | Empty package — only contains docstring | 🆕 NEW (trivial) |

**Previous dead code: ~691 lines (30% of source)**  
**Current dead code: ~99 lines (~2% of source)** — reduced by **86%**

### 4.3 Dead/Phantom Dependencies

| Dependency | Previous Status | Current Status |
|------------|----------------|----------------|
| `mistune>=3.0,<4.0` | **DEAD** — listed but never imported | ✅ FIXED — **removed** from `pyproject.toml` |
| `pyperclip>=1.8,<2.0` | Questionable — optional extra, no code uses it | ❌ STILL PRESENT — optional `[clipboard]` extra, still no code imports it |

### 4.4 Structural/Architectural Weaknesses

1. ⚠️ PARTIALLY FIXED: **Two parallel enforcement systems:**
   - The Python guard module (`src/aiv/guard/`) now **uses `aiv-lib` internally** — `runner.py:215` calls `ValidationPipeline`. This means the Python guard and CLI share the same validation logic for markdown packets.
   - The JS workflow (`aiv-guard.yml`, 2243 lines) is **preserved unchanged** alongside the new `aiv-guard-python.yml` (45 lines). Two CI workflows now exist.
   - The Python guard adds canonical JSON validation on top of `aiv-lib`, using its own rule IDs (`CT-001`, `CLS-002`, `A-001`, etc.) distinct from `aiv-lib` rule IDs (`E001`–`E018`). This is intentional (canonical validation is a superset), but the two rule ID namespaces are still separate.

2. ❌ STILL PRESENT: **Spec/Implementation drift on Class F:**
   - The canonical spec (`SPECIFICATION.md`) defines Class F as "Provenance" (cryptographic integrity).
   - The Python implementation still calls Class F "Conservation" (non-regression) in `EvidenceClass.CONSERVATION`, docstrings, and the `generate` command.

3. ✅ FIXED: **Classification parsing:**
   - Parser now extracts `risk_tier` from `## Classification (required)` YAML block via `_parse_classification()`.
   - Pipeline enforces evidence class requirements per tier via `_check_tier_requirements()` with `_TIER_REQUIRED` and `_TIER_OPTIONAL` mappings.
   - R0 needs A+B; R1 needs A+B+E; R2 needs A+B+C+E; R3 needs all six. Missing required = BLOCK, missing optional = INFO.
   - Tested with 9 unit tests in `test_validators.py::TestRiskTierEnforcement`.

4. ✅ FIXED: **Test coverage for validators:**
   - `test_validators.py` (382 lines) — Tests for zero-touch code block stripping (5), bug-fix heuristic (7), conservation negative framing (4), risk-tier enforcement (9).
   - `test_parser.py` (251 lines) — Tests for classification parsing (7), evidence class collection (2), methodology extraction (2).
   - `test_guard.py` — 36 tests for the guard module.
   - `test_svp.py` — 43 tests for SVP models and validators.
   - Total: 163 tests (was 39).

5. ❌ STILL PRESENT: **Pre-commit hook is independent shell:**
   - The Husky pre-commit hook still enforces atomic commits.
   - It still does NOT validate packet content — only checks that a packet file exists alongside the functional file.
   - A commit with an empty or invalid packet will still pass the pre-commit hook.

### 4.5 Test Coverage Gaps

| Area | Previous | Current |
|------|----------|---------|
| Model construction/validation | ✅ 28 tests | ✅ ~40 tests (added RiskTier, config tests) |
| Full pipeline happy path | ✅ 8 tests | ✅ 8 tests |
| Real packet smoke tests | ✅ 3 tests | ✅ 3 tests |
| Individual validator unit tests | ❌ Zero | ✅ **25 tests** (zero-touch 5, bug-fix 7, conservation 4, risk-tier 9) |
| Parser (classification, methodology) | ❌ Minimal | ✅ **11 tests** (classification 7, evidence collection 2, methodology 2) |
| Guard module | ❌ N/A | ✅ **36 tests** |
| SVP module | ❌ N/A | ✅ **43 tests** |
| `DiffAnalyzer` | ❌ Dead code | ✅ N/A — deleted |
| `guard/security.py` | ❌ Dead code | ✅ N/A — deleted |
| `validators/exceptions.py` | ❌ Dead code | ✅ N/A — deleted |
| Parser edge cases (malformed markdown) | ❌ Minimal | ❌ Still minimal — only missing header tested |
| Strict mode behavior with each validator | ❌ Limited | ❌ Still limited |
| Multi-claim evidence enrichment variants | ❌ Not tested | ❌ Still not tested |
| `AIVConfig.from_file()` YAML loading | ❌ Not tested | ❌ Still not tested |
| Anti-cheat deleted file detection | ❌ Not tested | ❌ Still not tested (regex fixed but no test for it) |
| `aiv generate` command | ❌ N/A | ❌ No tests for generate command |

---

## 5. Recommendations

### 5.1 Critical Fixes (should be done now)

1. ✅ DONE: **Fix anti-cheat removed file regex** — regex corrected to match real diff order.
2. ✅ DONE: **Fix evidence enrichment** — best-match logic implemented.
3. ✅ DONE: **Parse Classification section** — risk_tier extracted, tier requirements enforced.
4. ✅ DONE: **Unique rule IDs** — E015, E016, E017, E018 assigned.

### 5.2 Dead Code Cleanup

5. ✅ DONE: **Remove `mistune` from dependencies.**
6. ✅ DONE: **Remove unused imports** from `models.py` and `cli/main.py`.
7. ✅ DONE: **Delete `guard/security.py`** — replaced with full guard module.
8. ✅ DONE: **Delete `analyzers/diff.py`** — critical surface detection in guard/runner.py.
9. ✅ DONE: **Delete `validators/exceptions.py`** — fast-track in guard/runner.py.
10. ❌ OPEN: **Remove unused error classes** from `errors.py` — 4 of 5 still never raised.

### 5.3 Architectural Improvements

11. ⚠️ PARTIAL: **Integrate enforcement systems** — Python guard uses `aiv-lib` internally, but JS workflow is preserved alongside new Python workflow. Two CI workflows coexist.
12. ✅ DONE: **Make zero-touch validation real** — parser extracts methodology content; code blocks stripped before checking.
13. ❌ OPEN: **Resolve spec/implementation naming** — Class F still "Conservation" vs spec's "Provenance".
14. ✅ DONE: **Use the config for immutability** — `MutableBranchConfig` wired through to `ArtifactLink.from_url()`.
15. ✅ DONE: **Add validator unit tests** — 25 validator tests, 11 parser tests, 36 guard tests, 43 SVP tests.

### 5.4 Minor Improvements

16. ✅ DONE: **Replace `datetime.utcnow()`** with `datetime.now(timezone.utc)`.
17. ✅ DONE: **Replace `from typing import Pattern`** with `from re import Pattern`.
18. ❌ OPEN: **Make `PacketParser` stateless** — still uses `self.errors` instance variable.
19. ❌ OPEN: **Narrow exception catch** in `pipeline.py:98` — still catches bare `Exception`.

### 5.5 🆕 New Recommendations

20. **Add tests for `aiv generate` command** — no tests exist for the generate command, git scope detection, or tier-based evidence section building.
21. **Add tests for anti-cheat deleted file detection** — regex was fixed (L01) but no test validates the fix.
22. **Unify fast-track definitions** — `AIVConfig.fast_track_patterns` (config.py:128) and `FAST_TRACK_EXT`/`FAST_TRACK_NAMES` (guard/runner.py:71-72) should share a single source of truth.
23. **Delete or test legacy intent parser** — `_build_intent_from_legacy()` (parser.py:308-342) is untested dead code. Either add tests or remove it.
24. **Consider merging `src/svp/` into `src/aiv/svp/`** — currently SVP is a separate top-level package imported across package boundaries (`from svp.cli.main import svp_app`). Moving it under `src/aiv/svp/` would make the dependency explicit and the wheel structure cleaner.
25. **Remove unused error classes or wire them in** — `GitHubAPIError` should be used by `guard/github_api.py` instead of catching raw `HTTPError`; `ConfigurationError` should be raised by `AIVConfig.from_file()` on parse failures.

---

## 6. Summary Scorecard

| Dimension | Previous Rating | Current Rating | Notes |
|-----------|----------------|----------------|-------|
| **Correctness** | 6/10 | **8/10** | All HIGH/MEDIUM bugs fixed (L01-L05). Remaining issues are LOW severity (broad catch, line tracking, naming). |
| **Completeness** | 4/10 | **8/10** | Dead code reduced from ~30% to ~2%. Classification/risk-tier enforcement implemented. Guard module, SVP, and generate command added. |
| **Test Coverage** | 5/10 | **8/10** | 163 tests pass (was 39). Validators, parser, guard, SVP all have dedicated tests. Gaps remain in edge cases and generate command. |
| **Architecture** | 7/10 | **8/10** | Pipeline still clean. Guard module shares aiv-lib. JS workflow preserved but Python alternative exists. SVP integrated via CLI. |
| **Maintainability** | 5/10 | **8/10** | Dead code nearly eliminated. Rule IDs unique. Config wired through. Duplicate mutable branch logic resolved. |
| **Security** | N/A | N/A | Dead security module deleted. Guard module handles URL/SHA validation. No local execution surface in Python package. |
| **Spec Fidelity** | 4/10 | **7/10** | Risk tiers enforced. Classification parsed. Fast-track implemented (guard). Class F naming still "Conservation" vs spec's "Provenance". |

**Previous bottom line:** The Python implementation was a functional proof-of-concept with ~30% dead code, structurally broken validators (zero-touch, anti-cheat), and no risk-tier enforcement.

**Current bottom line:** The implementation is now a **production-capable** validation suite. All HIGH and MEDIUM bugs are fixed. Dead code reduced from ~691 lines to ~99 lines. Risk-tier enforcement implemented and tested. Guard module replaces JS with Python. SVP Protocol Suite added. 163 tests pass. Remaining issues are LOW severity: Class F naming, stateful parser, broad exception catch, and missing edge-case tests.

---

## 7. Cross-Analysis: External Gap Assessment vs. This Audit

An independent gap analysis was performed comparing the canonical specifications (`AIV-SUITE-SPEC-V1.0-CANONICAL` and `SVP-SUITE-SPEC-V1.0-CANONICAL`) against the codebase. Below is a systematic comparison of that analysis against this audit's findings, with a verdict on each claim.

### 7.1 Claim: "The Entire SVP Protocol Suite (0% Implemented)"

**External claim:** No SVP models (`PredictionRecord`, `TraceRecord`, `OwnershipCommit`), no `svp predict`/`svp trace`/`svp probe` commands, no ELO rating system.

**Previous audit verdict: AGREE — confirmed by code search.**

**Re-Audit verdict: ✅ NOW IMPLEMENTED.**

The SVP Protocol Suite has been fully implemented in `src/svp/` (6 files):
- `src/svp/lib/models.py` — All Pydantic models: phases 0-4 (`SanityGate`, `Prediction`, `Trace`, `Probe`, `Ownership`), `SVPSession`, `VerifierRating`, validation result types.
- `src/svp/lib/validators/session.py` — Session validation rules S001-S013.
- `src/svp/cli/main.py` — CLI commands: `svp status`, `svp predict`, `svp trace`, `svp probe`, `svp validate`.
- Integrated into main `aiv` CLI via `app.add_typer(svp_app, name="svp")`.
- 43 unit tests in `tests/unit/test_svp.py` — all passing.

**What remains:** SVP is a first implementation per the spec. Advanced features like ELO rating persistence, mastery tracking database, and CI gate integration are not yet built — the models exist but there's no storage/API layer.

---

### 7.2 Claim: "The 'Smart' Generator (aiv generate) — Missing"

**External claim:** The `aiv-cli` has a `generate` command entry point but lacks automated scope inventory, CI integration, and intent linking.

**Previous audit verdict: DISAGREE on one detail, AGREE on substance.**

**Re-Audit verdict: ✅ NOW IMPLEMENTED.**

The `aiv generate` command now exists (cli/main.py lines 144-258, 366 total lines). It provides:
- **Tier-based scaffolding:** `aiv generate auth-fix --tier R2` creates a packet file with evidence sections appropriate for the risk tier.
- **Automated git scope detection:** `_detect_git_scope()` runs `git diff --cached --name-status` to populate the scope inventory with changed files.
- **Classification block:** Pre-fills `risk_tier`, `sod_mode`, `classified_at` timestamp.
- **SoD mode detection:** R0/R1 → S0, R2/R3 → S1.

**What remains:** The generator still lacks:
- CI run URL auto-population (Class A evidence)
- Issue tracker integration for Class E intent linking
- Automated commit SHA insertion
- No tests for the generate command

---

### 7.3 Claim: "Guard Architecture — Duplicated Logic (Python vs JS)"

**External claim:** The Python `src/aiv/lib` and the JavaScript in `aiv-guard.yml` are duplicate implementations. The fix is a Python-based GitHub Action (`action.yml` + `Dockerfile`).

**Previous audit verdict: STRONGLY AGREE — the single most important architectural issue.**

**Re-Audit verdict: ✅ SUBSTANTIALLY ADDRESSED.**

The Python guard module (`src/aiv/guard/`, 6 files, ~1,571 lines) now provides a full Python replacement:

| System | Language | Lines | Rule IDs | Shared Code |
|--------|----------|-------|----------|-------------|
| `src/aiv/lib/` | Python | ~2,100 | E001–E018 | Core pipeline |
| `src/aiv/guard/` | Python | ~1,571 | CT-*, CLS-*, A-*, B-*, E-*, ATT-*, G-* | **Uses aiv-lib pipeline** |
| `aiv-guard.yml` | JavaScript (inline) | 2,243 | Different set | None (preserved) |
| `aiv-guard-python.yml` | Python workflow | 45 | Uses guard module | **Uses Python guard** |

Key improvements:
- **GitHub API client built:** `guard/github_api.py` (196 lines) — fetches PR files, workflow runs, CI artifacts via `urllib` (no external deps).
- **CI artifact inspection:** `runner.py:296-367` verifies Class A CI run URLs, checks head_sha match, inspects aiv-evidence artifacts.
- **Packet Source resolution:** `runner.py:181-209` reads `Packet Source:` pointers from PR bodies.
- **Canonical JSON validation:** `canonical.py` (522 lines) validates the structured `aiv-canonical-json` block.
- **Python guard shares aiv-lib:** `runner.py:215` calls `ValidationPipeline` for markdown validation.

**What remains:**
- JS workflow is preserved unchanged (safe fallback during transition)
- Python guard doesn't yet post PR comments (would need GitHub API write operations)
- No `action.yml` or `Dockerfile` yet — runs as `python -m aiv.guard` within the workflow

---

### 7.4 Claim: "Advanced Evidence Classes D & F — Incomplete Tooling"

**External claim:** No tooling for Class D (Differential/State) diffs. No sigstore/GPG integration for Class F (Provenance). System accepts plain strings for `classified_by`.

**Previous audit verdict: PARTIALLY AGREE — naming conflict identified.**

**Re-Audit verdict: ⚠️ PARTIALLY ADDRESSED.**

Code verification update:
- **Class D validators still trivial.** `evidence.py:_validate_state()` (lines 169-220) still only checks for database CLI keywords. No actual state diff validation.
- **Class F (Conservation) validators improved.** `evidence.py:_validate_conservation()` (lines 223-260) now has **negative framing detection** — claims with "no tests modified" or "preserved" phrasing are recognized as valid without additional justification. Test modification claims without negative framing produce E011 warnings. Tested with 4 unit tests in `test_validators.py::TestConservationNegativeFraming`.
- ✅ FIXED: **`classified_by` and `risk_tier` are now parsed.** The parser extracts `risk_tier` from the Classification YAML block. The pipeline enforces evidence requirements per tier.

**Naming conflict still present:**

| Class | Canonical Spec | Python `EvidenceClass` | Status |
|-------|---------------|----------------------|--------|
| D | Differential | `STATE` | ❌ Still mismatched |
| F | Provenance | `CONSERVATION` | ❌ Still mismatched |

---

### 7.5 Claim: "Roadmap Priority — Guard Refactor, SVP Core, Generator"

**External claim:** Priority order should be (1) Refactor AIV Guard, (2) Implement SVP Core, (3) Enhance Generator.

**Previous audit verdict: PARTIALLY DISAGREE — missing validator defect fixes as P0.**

**Re-Audit verdict: ✅ ROADMAP EXECUTED.**

All five priority items from the previous audit's revised roadmap have been completed:

| Priority | Task | Status |
|----------|------|--------|
| **P0** | Fix validator defects (L01–L05) | ✅ All fixed — regex, enrichment, heuristic, rule IDs, zero-touch |
| **P1** | Classification parsing + risk-tier enforcement | ✅ Implemented — parser + pipeline + 9 tests |
| **P2** | Refactor AIV Guard to use Python package | ✅ Implemented — 6 files, ~1,571 lines, 36 tests |
| **P3** | Build `aiv generate` command | ✅ Implemented — tier-based scaffolding + git scope detection |
| **P4** | Implement SVP Core (predict/trace/probe) | ✅ Implemented — 6 files, 43 tests |

**Updated roadmap for next phase:**

| Priority | Task | Rationale |
|----------|------|-----------|
| **P0** | Resolve remaining LOW-severity issues | Clean up: narrow exception catch, delete legacy parser, unify fast-track, wire error classes |
| **P1** | Add missing test coverage | Generate command tests, anti-cheat deleted file test, parser edge cases, strict mode |
| **P2** | Decommission JS guard workflow | Once Python guard is validated in production, remove `aiv-guard.yml` |
| **P3** | Resolve Class D/F naming conflict | Align with canonical spec or document the divergence explicitly |
| **P4** | Enhance generator with CI/issue integration | Auto-populate Class A run URLs, Class E issue links |

---

### 7.6 Findings Unique to This Audit (Not in External Analysis)

The external analysis is a high-level gap assessment against the specification. This audit is a line-by-line code review. Several findings exist only in this audit:

| Finding | Category | Description | Status |
|---------|----------|-------------|--------|
| L01 | Bug | Anti-cheat removed file regex inverted | ✅ FIXED |
| L02 | Bug | Evidence enrichment applies only first unlinked section | ✅ FIXED |
| L04 | Design | Rule ID E007 used for 4 different rules | ✅ FIXED |
| L06 | Bug | `DiffAnalyzer` misattributes critical surface matches | ✅ FIXED (module deleted) |
| L08 | Design | `MutableBranchConfig` never consulted | ✅ FIXED |
| D01–D10 | Dead code | 691 lines across 10 locations (30% of source) | ✅ 86% eliminated |
| — | Dependency | `mistune` phantom dependency | ✅ FIXED (removed) |
| — | Test gap | Zero individual validator unit tests | ✅ FIXED (25+ tests) |
| — | Parser | `_find_sections()` dead code | ✅ FIXED (removed) |
| — | Parser | `_build_intent_from_legacy()` untested | ❌ STILL PRESENT |

---

### 7.7 Findings Unique to External Analysis (Not in This Audit)

| Finding | Category | Previous Assessment | Current Status |
|---------|----------|---------------------|----------------|
| SVP suite 0% implemented | Gap | Valid — unimplemented | ✅ NOW IMPLEMENTED (43 tests) |
| `aiv generate` command missing | Feature gap | Factually, no command existed | ✅ NOW IMPLEMENTED |
| CI integration for Class A auto-population | Feature gap | Valid — not built | ❌ STILL MISSING in generator |
| Issue tracker integration for Class E | Feature gap | Valid — not built | ❌ STILL MISSING |

---

### 7.8 Consolidated Assessment

**Previous assessment:** Both analyses converged on the diagnosis that the Python implementation was a structural proof-of-concept, not production-ready. The external analysis identified what was missing; this audit identified what was broken.

**Re-Audit assessment:** The codebase has undergone **significant remediation**:

- **All HIGH and MEDIUM bugs fixed** (L01–L05): anti-cheat regex, evidence enrichment, bug-fix heuristic, rule ID collisions, zero-touch no-op.
- **Dead code reduced by 86%:** from ~691 lines (30% of source) to ~99 lines (~2%).
- **Major features built:** Guard module (1,571 lines), SVP suite (6 files), generate command, classification parsing, risk-tier enforcement.
- **Test suite 4× larger:** 163 tests (was 39).
- **Guard architecture unified:** Python guard uses aiv-lib internally; JS workflow preserved as fallback.

**Remaining gaps are LOW severity:**
- Class D/F naming conflict with spec
- Stateful parser
- Broad exception catch
- Legacy intent parser untested
- No tests for generate command or anti-cheat deleted file detection
- `pyperclip` optional extra still unused
- 4 exception classes still never raised

**Updated Scorecard (incorporating both analyses):**

| Dimension | Previous Rating | Current Rating | Notes |
|-----------|----------------|----------------|-------|
| **Correctness** | 6/10 | **8/10** | All HIGH/MEDIUM bugs fixed. LOW-severity issues remain. |
| **Completeness** | 3/10 | **8/10** | SVP, generator, guard, classification — all implemented. Class D/F validators still hollow. |
| **Test Coverage** | 5/10 | **8/10** | 163 tests. Validators, parser, guard, SVP tested. Edge-case gaps remain. |
| **Architecture** | 7/10 | **8/10** | Guard shares aiv-lib. SVP integrated. JS fallback preserved. |
| **Maintainability** | 5/10 | **8/10** | Dead code eliminated. Rule IDs unique. Config wired. |
| **Spec Fidelity** | 3/10 | **7/10** | Risk tiers enforced. Classification parsed. Class D/F naming still wrong. |
| **Production Readiness** | 2/10 | **7/10** | Python guard can replace JS guard. Missing PR comments and `action.yml`. |

---

## 8. Re-Audit Delta Summary

### 8.1 Remediation Statistics

| Metric | Previous | Current | Change |
|--------|----------|---------|--------|
| Python source files | 22 | 32 | +10 |
| Python source lines | ~2,318 | ~6,500+ | +180% |
| Test files | 3 | 7 | +4 |
| Tests passing | 39 | 163 | +318% |
| Dead code lines | ~691 (30%) | ~99 (2%) | -86% |
| Logical flaws (HIGH/MEDIUM) | 5 | 0 | -100% |
| Logical flaws (LOW) | 3 | 7 | +4 (3 carried + 4 new) |
| Dead code findings | 10 | 4 | -60% |
| Recommendations completed | 0/19 | 14/19 | 74% |

### 8.2 Finding Resolution Summary

| Category | Total | ✅ Fixed | ⚠️ Partial | ❌ Still Present | 🆕 New |
|----------|-------|----------|------------|-----------------|--------|
| Logical Flaws (L01–L12) | 12 | 8 | 0 | 1 carried + 3 new | 4 |
| Dead Code (D01–D12) | 12 | 8 | 0 | 2 carried | 2 |
| Dependencies | 2 | 1 | 0 | 1 | 0 |
| Structural Weaknesses | 5 | 2 | 1 | 2 | 0 |
| Recommendations (§5) | 25 | 14 | 2 | 5 | 6 new |

### 8.3 New Modules Added Since Previous Audit

| Module | Files | Lines | Tests | Purpose |
|--------|-------|-------|-------|---------|
| `src/aiv/guard/` | 6 | ~1,571 | 36 | Python AIV Guard (replaces JS inline) |
| `src/svp/` | 6 | ~1,200 | 43 | SVP Protocol Suite (cognitive verification) |
| `aiv generate` command | 1 (cli/main.py) | ~200 | 0 | Packet scaffold generation |
| `test_parser.py` | 1 | 251 | 11 | Parser unit tests |
| `test_validators.py` | 1 | 382 | 25 | Validator unit tests |

### 8.4 Overall Assessment

The codebase has transitioned from a **proof-of-concept** (previous audit) to a **production-capable** validation suite. The average scorecard rating improved from **4.4/10** to **7.7/10**. All critical and medium-severity findings have been resolved. The remaining work is cleanup, edge-case testing, and the Class D/F naming alignment with the canonical specification.
