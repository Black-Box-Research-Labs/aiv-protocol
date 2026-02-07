# AIV Protocol — Codebase Audit Report

**Date:** 2026-02-06  
**Auditor:** Cascade (Senior Software Engineer role)  
**Scope:** Full Python implementation in `src/aiv/`, tests in `tests/`, CI workflows, pre-commit hook  
**Method:** Static analysis, code tracing, execution verification (39/39 tests, 6/6 real packet CLI checks)

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
│   │   └── main.py                   # Typer CLI app with `check` and `init` commands
│   ├── guard/
│   │   ├── __init__.py
│   │   └── security.py               # Security utilities (sanitization, URL validation, JSON limits)
│   └── lib/
│       ├── __init__.py
│       ├── config.py                 # Pydantic configuration models (AIVConfig, ZeroTouchConfig, etc.)
│       ├── errors.py                 # Exception hierarchy (AIVError, PacketParseError, etc.)
│       ├── models.py                 # Core Pydantic models (352 lines)
│       ├── parser.py                 # Markdown packet parser (453 lines)
│       ├── analyzers/
│       │   ├── __init__.py
│       │   └── diff.py               # Git diff analyzer (166 lines)
│       └── validators/
│           ├── __init__.py
│           ├── base.py               # ABC + Protocol for validators
│           ├── anti_cheat.py         # Test manipulation detection (196 lines)
│           ├── evidence.py           # Evidence class-specific validation (262 lines)
│           ├── exceptions.py         # Bootstrap, Flake Report, Fast-Track handlers (220 lines)
│           ├── links.py              # URL immutability checking (138 lines)
│           ├── pipeline.py           # Orchestrator — runs all validators (181 lines)
│           ├── structure.py          # Packet structural completeness (76 lines)
│           └── zero_touch.py         # Zero-Touch compliance checking (174 lines)
├── tests/
│   ├── conftest.py                   # Shared fixtures (286 lines)
│   ├── unit/
│   │   └── test_models.py            # Model unit tests (270 lines)
│   └── integration/
│       └── test_full_workflow.py      # Pipeline integration tests (149 lines)
├── .github/
│   ├── workflows/
│   │   ├── aiv-guard.yml             # CI PR validation (2243 lines, JavaScript inline)
│   │   └── verify-architecture.yml   # CI build/evidence generation (527 lines)
│   ├── aiv-packets/                  # 13 verification packet files
│   └── PULL_REQUEST_TEMPLATE.md
├── .husky/
│   └── pre-commit                    # Atomic commit enforcer (184 lines, shell)
├── docs/specs/                       # Canonical specification documents
├── pyproject.toml                    # Build config (hatchling), dependencies, tool settings
├── SPECIFICATION.md                  # Canonical AIV spec v1.0.0
└── README.md
```

**Total Python source:** ~2,318 lines across 22 files  
**Total test code:** ~705 lines across 3 files  
**CI workflows:** ~2,770 lines (mostly inline JavaScript in aiv-guard.yml)

### 1.2 Entry Points

1. **CLI:** `aiv check <packet>` / `aiv init <path>` — via `src/aiv/cli/main.py:app` (Typer)
2. **Module:** `python -m aiv` — via `src/aiv/__main__.py`
3. **Console script:** `aiv` — registered in `pyproject.toml` → `aiv.cli.main:app`
4. **CI:** `.github/workflows/aiv-guard.yml` — standalone JavaScript, does NOT use the Python package
5. **Pre-commit:** `.husky/pre-commit` — standalone shell, does NOT use the Python package

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

### 2.1 `models.py` — Core Data Models (352 lines)

**Stated purpose:** Immutable Pydantic models for the AIV domain.

**Actual behavior — verified:**
- `EvidenceClass` enum maps A–F correctly. `from_string()` handles letter, name, and prefix formats. Case-insensitive.
- `ArtifactLink.from_url()` classifies URLs into 4 types: `github_blob`, `github_actions`, `github_pr`, `external`. SHA detection works for 7+ hex chars.
- `Claim`, `IntentSection`, `VerificationPacket` are all frozen. `VerificationPacket.all_links` correctly filters for `ArtifactLink` instances.
- `ValidationFinding.rule_id` enforced by regex `^E\d{3}$`.
- `ValidationResult.validated_at` uses `datetime.utcnow`.

**Inconsistencies found:**
- **DEAD IMPORT: `Annotated`** — imported from `typing` at line 12 but never used anywhere in the file.
- **DEAD IMPORT: `field_validator`** — imported from Pydantic at line 20 but never used. No field validators are defined.
- **DEAD IMPORT: `model_validator`** — imported from Pydantic at line 21 but never used. No model validators are defined.
- **DEPRECATION: `datetime.utcnow()`** — used at line 292 (`validated_at` default). Deprecated since Python 3.12 in favor of `datetime.now(timezone.utc)`.
- **NAMING INCONSISTENCY:** `EvidenceClass.CONSERVATION` (value "F") is documented as "Conservation (non-regression)" in the docstring, but the spec calls Class F "Provenance" in the template and `SPECIFICATION.md`. The model's docstring says "F: Conservation (non-regression)" while the canonical spec says "F: Provenance — Content-addressed integrity." These are different concepts.

### 2.2 `parser.py` — Markdown Parser (453 lines)

**Stated purpose:** Convert markdown verification packets into structured `VerificationPacket` objects.

**Actual behavior — verified against 6 real packets:**
- Section extraction via heading detection works correctly.
- Intent parsing: tries `### Class E` first (level 3), falls back to legacy `## 0. Intent Alignment`. Extracts `**Link:**` and `**Requirements Verified:**` fields via regex.
- Claim parsing: extracts numbered list items from `## Claim(s)` section. Minimum description length enforced (10 chars).
- Evidence enrichment: maps `### Class X` sections to claims via `Claim N:` references. Unlinked evidence (no claim references) falls back to all unenriched claims.

**Inconsistencies found:**
- **DEAD METHOD: `_find_sections()`** — defined at line 179 but never called anywhere in the codebase. Only `_find_section()` (singular) is used.
- **STATEFUL PARSER:** `PacketParser.errors` is an instance variable reset in `parse()`. This means the parser is **not thread-safe** and repeated calls clobber previous errors. The pipeline reads `self.parser.errors` after `parse()`, so this works in practice, but if the parser were reused concurrently it would fail.
- **FIRST-ONLY UNLINKED EVIDENCE:** At line 424-426, when claims are unenriched and unlinked evidence exists, ALL unenriched claims get `unlinked_evidence[0]` — only the first unlinked evidence section. If a packet has both unlinked Class B and unlinked Class A sections, only the first one (in document order) is used. Claims don't differentiate between evidence types.
- **LEGACY PARSER UNTESTED:** `_build_intent_from_legacy()` (lines 256-290) handles `## 0. Intent Alignment` format, but no real packet uses this format and no test exercises it. Dead code path.
- **VERSION FALLBACK:** If the header lacks a version (e.g., `# AIV Verification Packet`), version defaults to `"2.1"` (line 100). This is an assumption, not a parsing result.

### 2.3 `config.py` — Configuration Models (152 lines)

**Stated purpose:** Pydantic-based configuration for all validators.

**Actual behavior — verified:**
- `AIVConfig` extends `pydantic_settings.BaseSettings` with `env_prefix="AIV_"`.
- `from_file()` loads YAML via PyYAML (lazy import).
- Sub-configs: `ZeroTouchConfig`, `AntiCheatConfig`, `MutableBranchConfig` with sensible defaults.

**Inconsistencies found:**
- **YAML IMPORT NOT GUARDED:** `from_file()` does `import yaml` inside the method. If PyYAML isn't installed, this raises `ModuleNotFoundError` at call time, not import time. But PyYAML IS listed as a required dependency, so this is a style issue rather than a bug.
- **`fast_track_patterns` UNUSED:** `AIVConfig.fast_track_patterns` (line 128) is defined but the `FastTrackHandler` in `exceptions.py` has its OWN default patterns and is never integrated into the pipeline. The config field is dead.
- **`MutableBranchConfig` DUPLICATED:** The mutable branch set is defined both in `MutableBranchConfig.mutable_branches` (line 94) AND hardcoded in `ArtifactLink.from_url()` at `models.py:139`. The validator `LinkValidator` accepts a `MutableBranchConfig` but **never passes it to `ArtifactLink.from_url()`** — the model uses its own hardcoded set. The config is effectively ignored.

### 2.4 `errors.py` — Exception Hierarchy (69 lines)

**Stated purpose:** Exception classes for distinct failure modes.

**Actual behavior — verified:**
- Clean hierarchy: `AIVError` → `PacketParseError`, `PacketValidationError`, `ConfigurationError`, `GitHubAPIError`, `EvidenceResolutionError`.
- Each exception has appropriate metadata fields (rule_id, status_code, url).

**Inconsistencies found:**
- **4 of 5 exceptions are NEVER RAISED:** Only `PacketParseError` is used (in `parser.py`). The other four — `PacketValidationError`, `ConfigurationError`, `GitHubAPIError`, `EvidenceResolutionError` — are defined but never imported or raised anywhere in the codebase. They are speculative infrastructure for future code.

### 2.5 `guard/security.py` — Security Utilities (82 lines)

**Stated purpose:** Security utilities for the GitHub Action.

**Actual behavior — verified:**
- 5 standalone functions: `sanitize_for_shell()`, `sanitize_for_markdown()`, `truncate_for_log()`, `validate_url_structure()`, `safe_json_loads()`.
- `validate_url_structure()` rejects localhost, private IPs, non-standard ports (allows only 80, 443, 8080).

**Inconsistencies found:**
- **ENTIRE MODULE IS DEAD CODE:** None of the 5 functions are imported or called anywhere in the codebase. The `guard/` package is never referenced outside its own files. This module appears to be scaffolding for a future GitHub Action that doesn't exist yet.
- **INCOMPLETE PRIVATE IP CHECK:** `validate_url_structure()` checks for `192.168.*` and `10.*` but misses `172.16.0.0/12` (172.16–172.31), `169.254.*` (link-local), and IPv6 loopback `::1`.
- **PORT ALLOWLIST QUESTIONABLE:** Blocking port 443 with non-HTTPS scheme would be unusual but permitted; allowing port 8080 is generous for a security utility.

### 2.6 `analyzers/diff.py` — Diff Analyzer (166 lines)

**Stated purpose:** Git diff analysis for scope inventory validation and critical surface detection.

**Actual behavior — verified by code reading:**
- `DiffAnalyzer.analyze()` parses unified diff format into file-level statistics.
- `detect_critical_surfaces()` pattern-matches file paths and added lines against security-sensitive patterns (auth, crypto, PII, etc.).

**Inconsistencies found:**
- **ENTIRE MODULE IS DEAD CODE:** `DiffAnalyzer` is never imported or used anywhere in the codebase — not in the pipeline, not in the CLI, not in any test. The `AntiCheatScanner` does its own inline diff parsing.
- **INCORRECT CONTENT SCANNING:** `detect_critical_surfaces()` at line 158 always uses `analysis.files[-1].path` when matching diff content lines. It should track the current file during iteration, but instead attributes ALL content matches to the last file in the diff. This is a bug (documented in the comment as "simplified").

### 2.7 `validators/base.py` — Validator Interface (67 lines)

**Stated purpose:** Protocol + ABC defining the validator interface.

**Actual behavior — verified:**
- `Validator` is a `runtime_checkable Protocol`. `BaseValidator` is an ABC with `validate()` and `_make_finding()` helper.

**Inconsistencies found:**
- **PROTOCOL IS UNUSED:** The `Validator` protocol (line 16) is never checked with `isinstance()` anywhere. The pipeline directly calls concrete validators. The Protocol import of `runtime_checkable` is wasted.
- **DUAL ABSTRACTION:** Both `Protocol` AND `ABC` are defined for the same concept. Concrete validators inherit `BaseValidator` (ABC), making the Protocol redundant.

### 2.8 `validators/exceptions.py` — Exception Handlers (220 lines)

**Stated purpose:** Handlers for Bootstrap, Flake Report, and Fast-Track protocol exceptions.

**Actual behavior — verified by code reading:**
- `BootstrapExceptionHandler` — detects infrastructure PRs, validates bootstrap evidence.
- `FlakeReportHandler` — validates flake claims (requires 3 CI runs).
- `FastTrackHandler` — validates fast-track eligibility for trivial changes.

**Inconsistencies found:**
- **ENTIRE MODULE IS DEAD CODE:** None of the three handlers are imported or called anywhere — not in the pipeline, not in the CLI, not in any test. This is 220 lines of speculative infrastructure.
- **MISTYPED PARAMETER:** `FlakeReportHandler.validate_flake_claim()` takes `claim: object` (line 127) instead of `claim: Claim`. Uses `getattr(claim, "section_number", "?")` to defensively access the attribute. This is inconsistent with every other validator that types claims properly.

### 2.9 `validators/pipeline.py` — Validation Pipeline (181 lines)

**Stated purpose:** Orchestrates all validators in sequence.

**Actual behavior — verified by execution:**
- 7-stage pipeline: Parse → Structure → Links → Evidence → Zero-Touch → Anti-Cheat → Cross-Reference.
- Anti-cheat only runs if diff is provided. Cross-reference checks unjustified findings.
- Strict mode: warnings become failures.

**Inconsistencies found:**
- **EXCEPTION HANDLERS NOT INTEGRATED:** The pipeline doesn't use `BootstrapExceptionHandler`, `FlakeReportHandler`, or `FastTrackHandler` from `exceptions.py`. There's no fast-track bypass, no bootstrap detection, no flake report handling.
- **BROAD EXCEPTION CATCH:** Stage 1 parse (line 96) catches `Exception` instead of `PacketParseError`. This masks unexpected errors (e.g., Pydantic validation errors, regex errors) behind a generic E001 message.

### 2.10 `validators/structure.py` — Structure Validator (76 lines)

**Stated purpose:** Validates packet structural completeness.

**Actual behavior — verified:**
- Checks `verifier_check` minimum length (10 chars).
- Checks claim description minimum length (15 chars — stricter than parser's 10 char check).
- Checks reproduction field exists and isn't whitespace.

**Inconsistencies found:**
- **DUAL LENGTH THRESHOLDS:** The parser skips claims with description < 10 chars (line 314), but the structure validator warns on claims with description < 15 chars (line 50). A 12-char description passes the parser but gets a warning from the structure validator. This dual threshold is confusing.
- **REPRODUCTION CHECK IS VACUOUS:** The parser sets `reproduction="N/A"` for all claims (line 406). The structure validator checks if reproduction is empty or whitespace (line 63). Since the parser always sets `"N/A"`, this check can never fail. It validates the parser's output, not the packet's content.

### 2.11 `validators/evidence.py` — Evidence Validator (262 lines)

**Stated purpose:** Class-specific evidence validation rules.

**Actual behavior — verified:**
- Dispatches to 6 class-specific validators (A–F).
- Bug fix heuristic (`_is_bug_fix`) checks for keywords in intent and claim descriptions.

**Inconsistencies found:**
- **RULE ID COLLISION: E007** — Used for FOUR different things:
  - Class B: non-blob link (line 123)
  - Class B: missing file reference keywords (line 136)
  - Class C: missing negative framing (line 160)
  - Class D: manual database queries (line 182)
  - This makes E007 findings ambiguous — you can't tell which rule triggered from the ID alone.
- **BUG FIX HEURISTIC FALSE POSITIVES:** `_is_bug_fix()` triggers on the word "fix" appearing anywhere in any claim description. A claim like "SSO authentication fix" or even "prefix handling" would trigger. The word "issue" triggers on claims mentioning "GitHub issue link." These broad matches can incorrectly require Class F evidence.
- **CLASS A VALIDATION MOSTLY EMPTY:** `_validate_execution()` only checks sub-conditions when the artifact is a non-CI URL AND the description mentions "performance" or "ui/visual". For the common case (CI link or string artifact), it returns no findings. Class A validation is effectively a no-op for most claims.

### 2.12 `validators/links.py` — Link Validator (138 lines)

**Stated purpose:** URL immutability checking per Addendum 2.2.

**Actual behavior — verified:**
- Validates intent link immutability (Class E). Plain text → info. Mutable URL → block.
- Validates claim artifact links. Mutable github_blob → block.

**Inconsistencies found:**
- **`validate_link_format()` IS DEAD CODE:** Defined at line 99 but never called anywhere. The pipeline calls `validate()` → `validate_packet_links()`, which never delegates to `validate_link_format()`.
- **NO NETWORK VALIDATION:** Comments mention "Links should be accessible (optional, requires network)" but no network checks exist. All validation is structural/heuristic.
- **CONFIG NOT USED FOR IMMUTABILITY:** `LinkValidator` accepts a `MutableBranchConfig` but never passes it to `ArtifactLink.from_url()`. The config's `mutable_branches` set and `min_sha_length` are ignored entirely. The model uses hardcoded values.

### 2.13 `validators/zero_touch.py` — Zero-Touch Validator (174 lines)

**Stated purpose:** Ensures reproduction instructions don't require local execution.

**Actual behavior — verified:**
- Matches reproduction text against prohibited patterns (git, npm, python, docker, etc.) and allowed patterns (N/A, CI Automation, URLs, etc.).
- Calculates friction score per claim and aggregate per packet.
- Produces BLOCK for prohibited patterns, WARN for high step count.

**Inconsistencies found:**
- **ALWAYS PASSES IN PRACTICE:** The parser hardcodes `reproduction="N/A"` for all claims (line 406). `"N/A"` matches the allowed pattern `^N/?A$`, causing immediate early return with score=0. The zero-touch validator can NEVER find violations on parser-produced packets. It would only trigger if someone manually constructed a `Claim` with a different reproduction value.
- **DEPRECATED IMPORT:** `from typing import Pattern` (line 11) — `typing.Pattern` is deprecated since Python 3.9 in favor of `re.Pattern`.

### 2.14 `validators/anti_cheat.py` — Anti-Cheat Scanner (196 lines)

**Stated purpose:** Detects test manipulation in git diffs.

**Actual behavior — verified by test execution:**
- Scans diff for deleted assertions, added skip decorators, mock/bypass flags, removed test files.
- Cross-references findings against packet claims for Class F justification.

**Inconsistencies found:**
- **LINE NUMBER TRACKING BUG:** At lines 134-137, line counting logic increments `current_line` for added lines and context lines, but the counter is reset at each `@@` hunk header. For multi-hunk files, the first hunk's final count carries into hunk header parsing, but the `@@` match resets it to the new hunk's start. This is correct for finding approximate line numbers, but the counter is imprecise for additions that span many lines within a hunk.
- **REMOVED FILE DETECTION BUG:** At line 140-142, the regex `r"deleted file mode \d+\n.*?diff --git a/([^\s]+)"` looks for "deleted file mode" followed by a `diff --git` line. But in actual git diff output, the `diff --git` line comes BEFORE the `deleted file mode` line, not after. The regex will never match. This means deleted test files are **never detected**.
- **DEPRECATED IMPORT:** Same `from typing import Pattern` deprecation as zero_touch.py.

### 2.15 `cli/main.py` — CLI Application (170 lines)

**Stated purpose:** Typer CLI with `check` and `init` commands.

**Actual behavior — verified by execution:**
- `check`: reads packet from file/argument/stdin, runs pipeline, displays results with Rich tables.
- `init`: creates `.aiv.yml` config file.

**Inconsistencies found:**
- **UNUSED IMPORTS:** Line 18-24 imports `PacketParser`, `StructureValidator`, `EvidenceValidator`, `LinkValidator`, `ZeroTouchValidator`, `AntiCheatScanner` directly, but only `ValidationPipeline` is used. The individual validators are never referenced in the CLI.
- **UNUSED IMPORT:** `Severity` imported at line 18 but never referenced.
- **`init` IS MINIMAL:** Only creates `.aiv.yml`. The docstring says "Creates: .aiv.yml configuration file, Verification packet template" but no template is actually created.
- **FROZEN MODEL MUTATION:** At line 68, `cfg.strict_mode = strict` mutates the `AIVConfig` object. But `AIVConfig` doesn't set `frozen=True` (it's a `BaseSettings`, not a regular `BaseModel`), so this works. However, it's a code smell — the config is modified after construction.

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

| ID | Severity | Location | Description |
|----|----------|----------|-------------|
| L01 | **HIGH** | `anti_cheat.py:140-142` | Removed test file detection regex is inverted — `diff --git` comes BEFORE `deleted file mode` in real diffs, so the pattern never matches. Deleted test files are invisible to the scanner. |
| L02 | **HIGH** | `parser.py:424-426` | All unenriched claims get `unlinked_evidence[0]` regardless of evidence class. A packet with both Class B and Class A unlinked sections only applies the first one. Claims that should be Class A get Class B instead. |
| L03 | **MEDIUM** | `evidence.py:247-261` | Bug fix heuristic triggers on common words ("fix", "issue", "patch"). A claim mentioning "prefix handling" or linking to "GitHub issue #42" falsely triggers Class F requirement. |
| L04 | **MEDIUM** | `evidence.py:123,136,160,182` | Rule ID E007 used for 4 different rules across 3 evidence classes. Findings are ambiguous. |
| L05 | **MEDIUM** | `zero_touch.py:45-47` + `parser.py:406` | Zero-touch validator is structurally incapable of finding violations because the parser hardcodes `reproduction="N/A"` for all claims. The validator validates the parser's output, not the packet's actual content. |
| L06 | **LOW** | `analyzers/diff.py:158` | `detect_critical_surfaces()` attributes all content-line matches to `analysis.files[-1]` instead of tracking current file during iteration. |
| L07 | **LOW** | `models.py:292` | `datetime.utcnow()` deprecated since Python 3.12. |
| L08 | **LOW** | `models.py:139` vs `config.py:94` | Mutable branch set is hardcoded in model AND defined in config, but config is never consulted. |

### 4.2 Dead Code

| ID | Module | Lines | Description |
|----|--------|-------|-------------|
| D01 | `guard/security.py` | 82 | **Entire module** — 5 functions, 0 callers anywhere in codebase |
| D02 | `analyzers/diff.py` | 166 | **Entire module** — `DiffAnalyzer` never imported or used |
| D03 | `validators/exceptions.py` | 220 | **Entire module** — 3 handler classes, 0 callers anywhere |
| D04 | `errors.py` | ~47 | 4 of 5 exception classes never raised (`PacketValidationError`, `ConfigurationError`, `GitHubAPIError`, `EvidenceResolutionError`) |
| D05 | `models.py:12,20-21` | 3 | Unused imports: `Annotated`, `field_validator`, `model_validator` |
| D06 | `cli/main.py:18-24` | 7 | Unused imports: `PacketParser`, `StructureValidator`, `EvidenceValidator`, `LinkValidator`, `ZeroTouchValidator`, `AntiCheatScanner`, `Severity` |
| D07 | `parser.py:179-190` | 12 | `_find_sections()` method never called |
| D08 | `links.py:99-137` | 39 | `validate_link_format()` method never called |
| D09 | `parser.py:256-290` | 35 | `_build_intent_from_legacy()` never exercised — no real packet or test uses legacy format |
| D10 | `base.py:15-34` | 20 | `Validator` Protocol never checked or used |

**Total dead code: ~691 lines** (~30% of the Python source)

### 4.3 Dead/Phantom Dependencies

| Dependency | Status | Explanation |
|------------|--------|-------------|
| `mistune>=3.0,<4.0` | **DEAD** | Listed in `pyproject.toml` but never imported anywhere. Parser uses regex. |
| `pyperclip>=1.8,<2.0` | Questionable | Optional `[clipboard]` extra, but no code imports or uses it. |

### 4.4 Structural/Architectural Weaknesses

1. **Two parallel enforcement systems with zero integration:**
   - The Python package (`src/aiv/`) validates packets locally via CLI.
   - The CI workflow (`aiv-guard.yml`, 2243 lines of inline JavaScript) validates packets on PRs.
   - These are **completely independent implementations** — they don't share code, models, rules, or even rule IDs. A packet that passes `aiv check` may fail CI or vice versa.

2. **Spec/Implementation drift:**
   - The canonical spec (`SPECIFICATION.md`) defines Class F as "Provenance" (cryptographic integrity).
   - The Python implementation calls Class F "Conservation" (non-regression).
   - These are fundamentally different concepts. The naming mismatch suggests the implementation was written against a different version of the spec.

3. **No Classification parsing:**
   - Real packets include a `## Classification (required)` YAML block with `risk_tier`, `sod_mode`, `critical_surfaces`, etc.
   - The parser completely ignores this section. Risk tier is never extracted or used.
   - This means evidence requirements by tier (R0 needs A+B, R1 needs A+B+E, etc.) are **never enforced**.

4. **No test coverage for validators individually:**
   - Unit tests only cover models (`test_models.py`).
   - Individual validators (`structure`, `evidence`, `links`, `zero_touch`, `anti_cheat`) have **zero unit tests**.
   - The integration tests exercise the pipeline, but don't isolate validator behavior.

5. **Pre-commit hook is independent shell:**
   - The Husky pre-commit hook (184 lines of shell) enforces atomic commits.
   - It does NOT validate packet content — only checks that a packet file exists alongside the functional file.
   - A commit with an empty or invalid packet will pass the pre-commit hook.

### 4.5 Test Coverage Gaps

| Area | Status |
|------|--------|
| Model construction/validation | ✅ Covered (28 tests) |
| Full pipeline happy path | ✅ Covered (8 tests) |
| Real packet smoke tests | ✅ Covered (3 tests) |
| Individual validator unit tests | ❌ **Zero coverage** |
| `DiffAnalyzer` | ❌ Zero coverage (dead code) |
| `guard/security.py` | ❌ Zero coverage (dead code) |
| `validators/exceptions.py` | ❌ Zero coverage (dead code) |
| Parser edge cases (malformed markdown) | ❌ Minimal — only tests missing header |
| Strict mode behavior with each validator | ❌ Tested only via `invalid_mutable_link` |
| Multi-claim evidence enrichment variants | ❌ Not tested |
| `AIVConfig.from_file()` YAML loading | ❌ Not tested |

---

## 5. Recommendations

### 5.1 Critical Fixes (should be done now)

1. **Fix anti-cheat removed file regex** (`anti_cheat.py:140`): Reverse the pattern to match `diff --git` before `deleted file mode`, or parse files first and check status separately using the existing `DiffFile` model.

2. **Fix evidence enrichment** (`parser.py:424-426`): Instead of always applying `unlinked_evidence[0]`, match unlinked evidence by type — claims that don't have evidence should get the most relevant unlinked evidence based on their content or position, or at minimum all unlinked evidence should be available.

3. **Parse Classification section**: Extract `risk_tier` from the YAML block and enforce evidence class requirements per tier. This is the core value proposition of the protocol.

4. **Unique rule IDs**: E007 is used for 4 different rules. Assign distinct IDs (e.g., E015-E018) so findings are unambiguous.

### 5.2 Dead Code Cleanup

5. **Remove `mistune` from dependencies** — it's installed but never used.
6. **Remove unused imports** from `models.py` (`Annotated`, `field_validator`, `model_validator`) and `cli/main.py` (individual validators, `Severity`).
7. **Delete or integrate `guard/security.py`** — either wire it into the pipeline or remove it.
8. **Delete or integrate `analyzers/diff.py`** — either replace inline diff parsing in `AntiCheatScanner` with `DiffAnalyzer`, or remove the module.
9. **Delete or integrate `validators/exceptions.py`** — either wire Bootstrap/FlakeReport/FastTrack into the pipeline, or remove them.
10. **Remove unused error classes** from `errors.py` or mark them as future placeholders.

### 5.3 Architectural Improvements

11. **Integrate the two enforcement systems**: Either rewrite `aiv-guard.yml` to call the Python package, or generate a shared rule definition that both systems consume. Currently you maintain two completely independent validators.

12. **Make zero-touch validation real**: The parser should extract reproduction instructions from the evidence sections (e.g., `### Class A` content that contains commands) rather than hardcoding `reproduction="N/A"`.

13. **Resolve spec/implementation naming**: Decide whether Class F is "Provenance" (spec) or "Conservation" (implementation) and align everywhere.

14. **Use the config for immutability**: Pass `MutableBranchConfig` through to `ArtifactLink.from_url()` so the mutable branch set is configurable rather than hardcoded.

15. **Add validator unit tests**: Each validator should have its own test file with isolated test cases. The current suite tests the pipeline as a whole, which makes it hard to diagnose individual validator failures.

### 5.4 Minor Improvements

16. **Replace `datetime.utcnow()`** with `datetime.now(timezone.utc)`.
17. **Replace `from typing import Pattern`** with `from re import Pattern` (deprecated since 3.9).
18. **Make `PacketParser` stateless**: Return errors alongside the parsed packet instead of storing them as instance state. This enables thread safety and cleaner API.
19. **Narrow exception catch** in `pipeline.py:96`: Catch `PacketParseError` specifically instead of bare `Exception`.

---

## 6. Summary Scorecard

| Dimension | Rating | Notes |
|-----------|--------|-------|
| **Correctness** | 6/10 | Core happy path works. Multiple bugs in edge cases (anti-cheat regex, evidence enrichment, bug-fix heuristic). |
| **Completeness** | 4/10 | ~30% dead code. Classification/risk-tier enforcement missing. Exception handlers unintegrated. |
| **Test Coverage** | 5/10 | 39 tests pass. But 0 validator unit tests, 0 coverage on 3 entire modules. |
| **Architecture** | 7/10 | Clean pipeline pattern, frozen models, good separation. Undermined by two parallel systems and dead scaffolding. |
| **Maintainability** | 5/10 | Good code style. But dead code, duplicate logic (mutable branches), and ambiguous rule IDs hurt. |
| **Security** | N/A | Security module exists but is dead code. No actual security surface in the Python package. |
| **Spec Fidelity** | 4/10 | Class F naming wrong. Risk tiers not enforced. Classification not parsed. Fast-track not implemented. |

**Bottom line:** The Python implementation is a functional proof-of-concept that validates packet structure and link immutability. Its core pipeline architecture is sound. However, ~30% of the code is dead scaffolding, several validators are structurally unable to find the violations they're designed to detect (zero-touch, anti-cheat file deletion), and the most important protocol feature — risk-tier-based evidence requirements — is not implemented at all.

---

## 7. Cross-Analysis: External Gap Assessment vs. This Audit

An independent gap analysis was performed comparing the canonical specifications (`AIV-SUITE-SPEC-V1.0-CANONICAL` and `SVP-SUITE-SPEC-V1.0-CANONICAL`) against the codebase. Below is a systematic comparison of that analysis against this audit's findings, with a verdict on each claim.

### 7.1 Claim: "The Entire SVP Protocol Suite (0% Implemented)"

**External claim:** No SVP models (`PredictionRecord`, `TraceRecord`, `OwnershipCommit`), no `svp predict`/`svp trace`/`svp probe` commands, no ELO rating system.

**Audit verdict: AGREE — confirmed by code search.**

Grep for `svp`, `prediction`, `trace.*record`, `ownership.*commit`, `mental.*trace` across `src/` returns zero matches. The SVP suite exists only in `docs/specs/SVP-SUITE-SPEC-V1.0-CANONICAL-2025-12-20.md`. No Python models, no CLI commands, no data structures. This is a pure specification with zero implementation.

**Impact assessment: AGREE.** The external analysis correctly identifies that without SVP, a verifier can rubber-stamp PRs by providing the correct packet format. The AIV system validates evidence *structure*, not human *comprehension*. This is by design — the spec itself acknowledges Class G (Cognitive Evidence) is optional because "you can't prove thinking occurred" — but it does mean the "cognitive debt" problem stated in the user story remains unsolved by the current codebase.

**What this audit adds:** The SVP spec describes Pydantic models in its specification document, but these are aspirational code snippets, not runnable code. No `src/svp/` directory exists.

---

### 7.2 Claim: "The 'Smart' Generator (aiv generate) — Missing"

**External claim:** The `aiv-cli` has a `generate` command entry point but lacks automated scope inventory, CI integration, and intent linking.

**Audit verdict: DISAGREE on one detail, AGREE on substance.**

The external analysis claims "`aiv-cli` has a `generate` command entry point." **This is factually incorrect.** Grep for `generate` in `src/aiv/cli/` returns zero matches. The CLI (`cli/main.py`) defines exactly two commands: `check` and `init`. There is no `generate` command, not even a stub.

However, the substantive point is correct: there is no automated packet generation tooling. Developers must manually:
- Copy-paste commit SHAs for Class B links
- Find and link CI run URLs for Class A evidence
- Write scope inventories by hand
- Look up spec/issue references for Class E

**What this audit adds:** The `init` command (line 118-146 of `cli/main.py`) only creates a `.aiv.yml` config file. Its docstring *claims* it also creates a "Verification packet template," but the implementation does not do this. This is a documented-but-unimplemented feature within the existing CLI.

---

### 7.3 Claim: "Guard Architecture — Duplicated Logic (Python vs JS)"

**External claim:** The Python `src/aiv/lib` and the JavaScript in `aiv-guard.yml` are duplicate implementations. The fix is a Python-based GitHub Action (`action.yml` + `Dockerfile`).

**Audit verdict: STRONGLY AGREE — this is the single most important architectural issue.**

This audit independently identified this as finding §4.4.1: "Two parallel enforcement systems with zero integration." The numbers confirm the scale:

| System | Language | Lines | Rule IDs | Shared Code |
|--------|----------|-------|----------|-------------|
| `src/aiv/lib/` | Python | ~2,318 | E001–E014 | None |
| `aiv-guard.yml` | JavaScript (inline) | 2,243 | Different set | None |

No `action.yml` or `Dockerfile` exists in the repo (confirmed by search). The only way to run the Python validator in CI today would be to add a workflow step that installs the package and runs `aiv check`.

**Where this audit goes further:** The external analysis frames this as "maintenance risk" (logic drift). This audit adds a more specific finding: **the two systems don't even use the same rule IDs.** A packet that produces `E004` in the Python validator may trigger a completely different check (or no check) in the JS guard. This isn't just drift risk — the two systems are architecturally decoupled from inception.

**Where I add nuance:** The external analysis's proposed fix ("delete the 2000-line JS script and replace with `pip install aiv-protocol && aiv check`") is correct in direction but understates the work. The JS guard does things the Python package cannot:
- Fetches PR body from GitHub API (Python has no GitHub API client — finding §D04 in errors.py, `GitHubAPIError` defined but never used)
- Inspects CI artifacts (Python has no artifact fetching)
- Posts PR comments with validation results
- Reads `Packet Source:` pointers from PR bodies to locate packet files

A full replacement requires building a GitHub API client and artifact inspector into the Python package first.

---

### 7.4 Claim: "Advanced Evidence Classes D & F — Incomplete Tooling"

**External claim:** No tooling for Class D (Differential/State) diffs. No sigstore/GPG integration for Class F (Provenance). System accepts plain strings for `classified_by`.

**Audit verdict: PARTIALLY AGREE — but the external analysis has the naming wrong too.**

Code verification:
- **Class D validators exist** but are trivial. `evidence.py:_validate_state()` (lines 169-196) only checks if the reproduction field contains database CLI keywords (`sqlite3`, `psql`, etc.). It doesn't validate actual state diffs, before/after comparisons, or schema changes. So: **structurally present, functionally hollow.**
- **Class F validators exist** but are also trivial. `evidence.py:_validate_conservation()` (lines 221-245) only checks if test-related claims have a justification field. No cryptographic integrity checks, no sigstore, no GPG, no hash verification. So: **same — structurally present, functionally hollow.**
- **`classified_by` is never parsed.** Grep for `classified_by`, `risk_tier`, `sod_mode` in `src/` returns zero matches. The Classification YAML block is completely ignored by the parser.

**Critical nuance the external analysis misses:** The external analysis says "Class D (Differential)" and "Class F (Provenance)." But this audit found a **naming conflict** (finding §2.1): the Python codebase calls Class D "STATE" (not Differential) and Class F "CONSERVATION" (not Provenance). The canonical spec (`SPECIFICATION.md`) calls them "Differential" and "Provenance" respectively. The implementation spec (`AIV-SUITE-SPEC`) may use different terminology. This naming confusion is itself a finding — the codebase, the canonical spec, and the implementation spec don't agree on what D and F mean.

| Class | Canonical Spec | Python `EvidenceClass` | Implementation Spec |
|-------|---------------|----------------------|-------------------|
| D | Differential | `STATE` | Varies |
| F | Provenance | `CONSERVATION` | Varies |

---

### 7.5 Claim: "Roadmap Priority — Guard Refactor, SVP Core, Generator"

**External claim:** Priority order should be (1) Refactor AIV Guard, (2) Implement SVP Core, (3) Enhance Generator.

**Audit verdict: PARTIALLY DISAGREE — missing the most critical item.**

The external roadmap skips the finding this audit rates highest: **the Python validator itself has structural defects that must be fixed before it can replace the JS guard.** Specifically:

1. **Zero-touch validator is structurally a no-op** (finding L05) — parser hardcodes `reproduction="N/A"`, so the validator always passes. If you replace the JS guard with `aiv check`, zero-touch enforcement disappears.
2. **Anti-cheat deleted file detection is broken** (finding L01) — regex is inverted, deleted test files are invisible.
3. **Risk-tier enforcement doesn't exist** (finding §4.4.3) — Classification YAML is ignored. The most important protocol feature (R0 needs A+B, R1 needs A+B+E, etc.) is not implemented.
4. **Bug-fix heuristic produces false positives** (finding L03) — requiring Class F evidence for any claim containing "fix" or "issue."

**Revised roadmap (this audit's recommendation):**

| Priority | Task | Rationale |
|----------|------|-----------|
| **P0** | Fix validator defects (L01–L05) | Can't replace JS guard with broken Python validator |
| **P1** | Implement Classification parsing + risk-tier enforcement | This is the protocol's core value proposition |
| **P2** | Refactor AIV Guard to use Python package | Eliminates the dual-system maintenance burden |
| **P3** | Build `aiv generate` command | Reduces developer friction |
| **P4** | Implement SVP Core (predict/trace/probe) | Solves cognitive debt problem |

The key disagreement: the external analysis assumes the Python validator is ready to replace the JS guard. This audit demonstrates it is not — multiple validators are structurally unable to find violations, and the most important feature (risk-tier enforcement) is missing entirely. Fix the tool first, then promote it to CI.

---

### 7.6 Findings Unique to This Audit (Not in External Analysis)

The external analysis is a high-level gap assessment against the specification. This audit is a line-by-line code review. Several findings exist only in this audit:

| Finding | Category | Description |
|---------|----------|-------------|
| L01 | Bug | Anti-cheat removed file regex inverted — never matches real diffs |
| L02 | Bug | Evidence enrichment applies only first unlinked section to all claims |
| L04 | Design | Rule ID E007 used for 4 different rules — findings are ambiguous |
| L06 | Bug | `DiffAnalyzer.detect_critical_surfaces()` attributes all matches to last file |
| L08 | Design | `MutableBranchConfig` defined in config but never consulted by `ArtifactLink.from_url()` |
| D01–D10 | Dead code | 691 lines of dead code across 10 locations (30% of source) |
| — | Dependency | `mistune` is a phantom dependency — installed but never imported |
| — | Test gap | Zero unit tests for any individual validator |
| — | Parser | `_find_sections()` and `_build_intent_from_legacy()` are dead code paths |

---

### 7.7 Findings Unique to External Analysis (Not in This Audit)

| Finding | Category | This Audit's Assessment |
|---------|----------|------------------------|
| SVP suite 0% implemented | Gap | **Valid.** This audit focused on `src/aiv/` and did not scope SVP as a gap since the repo is named `aiv-protocol`, not `svp-protocol`. But the specs exist and are unimplemented. |
| `aiv generate` command exists as stub | Factual claim | **Incorrect.** No `generate` command exists — not even a stub. CLI has only `check` and `init`. |
| CI integration for Class A auto-population | Feature gap | **Valid and important.** Not flagged by this audit because it's a missing-feature rather than a code-defect. |
| Issue tracker integration for Class E | Feature gap | **Valid.** Same category — feature that doesn't exist, rather than broken code. |

---

### 7.8 Consolidated Assessment

Both analyses converge on the same core diagnosis: **the Python implementation is a structural proof-of-concept, not a production-ready validator.** The two analyses complement each other:

- **External analysis** identifies *what's missing* relative to the spec (SVP, generator, guard refactor, advanced evidence classes).
- **This audit** identifies *what's broken* in what exists (dead code, inverted regexes, no-op validators, naming conflicts, missing risk-tier enforcement).

Together, they paint a complete picture: the codebase has a sound architectural skeleton (pipeline, frozen models, validator interface) but needs both **depth** (fix what exists) and **breadth** (build what's missing) before it can serve as the single source of truth for AIV protocol enforcement.

**Updated Scorecard (incorporating both analyses):**

| Dimension | Rating | Notes |
|-----------|--------|-------|
| **Correctness** | 6/10 | Core happy path works. Edge-case bugs in anti-cheat, evidence enrichment, bug-fix heuristic. |
| **Completeness** | 3/10 | ~30% dead code. No SVP. No generator. No risk-tier enforcement. No Classification parsing. Class D/F validators are hollow. |
| **Test Coverage** | 5/10 | 39 tests pass. But 0 validator unit tests, 0 coverage on 3 entire modules, no edge-case coverage. |
| **Architecture** | 7/10 | Clean pipeline, frozen models, good separation. Undermined by dual JS/Python systems and dead scaffolding. |
| **Maintainability** | 5/10 | Good code style. Dead code, duplicate logic, ambiguous rule IDs, naming drift from spec. |
| **Spec Fidelity** | 3/10 | Class D/F naming wrong. Risk tiers not enforced. Classification not parsed. SVP 0%. Fast-track unintegrated. No generator. |
| **Production Readiness** | 2/10 | Cannot replace JS guard due to validator defects and missing GitHub API/artifact integration. |
