# Source File ↔ Verification Packet Mapping

> **What is this?** Every commit in this repo pairs a functional file with a verification packet.
> This document is the **evidence index** — it answers questions the individual packets cannot:
>
> - **"Show me all evidence for file X"** → [Source Files → Packets](#source-files--verification-packets)
> - **"What files does packet Y cover?"** → [Packets → Source Files](#verification-packets--source-files)
> - **"Which files have no evidence?"** → [Unmapped Source Files](#unmapped-source-files)
>
> **Regenerate:** `python scripts/map_packets.py`

Auto-generated from git commit history.

## Summary

- **Mapped source files (live):** 56
- **Mapped packets (live):** 62
- **Unmapped source files:** 11
- **Unmapped packets (packet-only commits):** 3
- **Ghost packets (deleted from disk):** 27
- **Deleted source files:** 11

## Source Files → Verification Packets

### `./`

| Source File | Packet(s) | Commit(s) |
|---|---|---|
| `.gitignore` | GITIGNORE | `83c5a1c` |
| `pyproject.toml` | AIV_AUDIT_FIXES, MISTUNE_REMOVAL, PYPROJECT | `2c3d2eb`, `42c7869`, `74761ae` |

### `.github/`

| Source File | Packet(s) | Commit(s) |
|---|---|---|
| `PULL_REQUEST_TEMPLATE.md` | PR_TEMPLATE | `acf0766` |

### `.github\workflows/`

| Source File | Packet(s) | Commit(s) |
|---|---|---|
| `aiv-guard-python.yml` | CI_LINT_FORMAT, GUARD_REFACTOR | `3535166`, `779b9d2` |
| `aiv-guard.yml` | AIV_GUARD, CRITIQUE_FIXES | `60ea728`, `9955e75` |
| `ci.yml` | CI_LINT_FORMAT, EVIDENCE_PIPELINE | `9bfac7d`, `efc32ee` |
| `verify-architecture.yml` | EVIDENCE_PIPELINE, VERIFY_ARCH | `03c4bd0`, `0acdfe1` |

### `.husky/`

| Source File | Packet(s) | Commit(s) |
|---|---|---|
| `pre-commit` | CRITIQUE_FIXES, PRECOMMIT, PRECOMMIT_HOOK_FIX, SNAPSHOT_WINDOWS_FIX | `0b00c63`, `5ced0b3`, `b25af40`, `c4128a1` |

### `scripts/`

| Source File | Packet(s) | Commit(s) |
|---|---|---|
| `map_packets.py` | FILE_PACKET_MAP | `f3202e4` |

### `src\aiv/`

| Source File | Packet(s) | Commit(s) |
|---|---|---|
| `__init__.py` | AIV_INIT, CI_LINT_FORMAT | `2fa0f15`, `575c11e` |
| `__main__.py` | MAIN_ENTRY | `57482d9` |
| `py.typed` | PY_TYPED | `6be32ea` |

### `src\aiv\cli/`

| Source File | Packet(s) | Commit(s) |
|---|---|---|
| `__init__.py` | CLI_INIT | `9292c8e` |
| `main.py` | AIV_AUDIT_FIXES, AUDIT_CLI_COMMAND, CI_LINT_FORMAT, CLI_CLEANUP, CLI_MAIN, CRITIQUE_FIXES, FALSIFIABILITY_GUIDED_GEN, GENERATE_CMD, GENERATOR_CLASS_E_FIX, SVP_IMPL | `3665936`, `3842564`, `464c063`, `4784c47`, `8b8f941`, `9214766`, `adae01d`, `bc3982e`, `d56b589`, `fea5aed` |

### `src\aiv\guard/`

| Source File | Packet(s) | Commit(s) |
|---|---|---|
| `__init__.py` | CI_LINT_FORMAT, GUARD_INIT, GUARD_REFACTOR | `2b0aa56`, `779b9d2`, `f39fff5` |
| `__main__.py` | GUARD_REFACTOR | `779b9d2` |
| `canonical.py` | CI_LINT_FORMAT, FALSIFIABILITY_CT013, GUARD_REFACTOR | `50d9cad`, `779b9d2`, `90557ff` |
| `github_api.py` | AIV_AUDIT_FIXES, CI_LINT_FORMAT, GUARD_REFACTOR | `24c0e6b`, `779b9d2`, `dbf4185` |
| `manifest.py` | CI_LINT_FORMAT, EVIDENCE_PIPELINE, GUARD_REFACTOR | `66a874a`, `779b9d2`, `a1cfb9f`, `bb3fe91` |
| `models.py` | CI_LINT_FORMAT, GUARD_REFACTOR | `09283a0`, `779b9d2` |
| `runner.py` | AIV_AUDIT_FIXES, CI_LINT_FORMAT, GUARD_REFACTOR | `11cfb83`, `750afcb`, `779b9d2` |

### `src\aiv\lib/`

| Source File | Packet(s) | Commit(s) |
|---|---|---|
| `__init__.py` | LIB_INIT | `e7c55f9` |
| `auditor.py` | AUDITOR_FALSE_POSITIVE_FIX, CI_LINT_FORMAT, PACKET_AUDITOR | `39d1685`, `6d708e6`, `7633861` |
| `config.py` | AIV_AUDIT_FIXES, CI_LINT_FORMAT, CONFIG | `1454ac9`, `3f1db42`, `5cfb386` |
| `errors.py` | AIV_AUDIT_FIXES, CI_LINT_FORMAT, ERRORS | `16c0ced`, `34ee79c`, `56af5e7` |
| `models.py` | AIV_AUDIT_FIXES, CI_LINT_FORMAT, CLASSIFICATION, MODELS, MODELS_CLEANUP, MUTABLE_CONFIG, ZEROTOUCH_FIX | `1b22fc5`, `4f2f07d`, `547b126`, `63dfe83`, `711d192`, `e1d94f1` |
| `parser.py` | AIV_AUDIT_FIXES, CI_LINT_FORMAT, CLASSIFICATION, CLI_CLEANUP, EVIDENCE_RULES, PARSER, PARSER_CLEANUP, PARSER_CODEBLOCK_FIX, PARSER_ENRICHMENT, PARSER_SUBSTANCE_FIX, PARSER_SUBSTANCE_REFINE, ZEROTOUCH_FIX | `2158886`, `2ad8101`, `304d47e`, `36071ce`, `4f41529`, `5f0f951`, `711d192`, `8a50936`, `8aee121`, `dfe6438` |

### `src\aiv\lib\validators/`

| Source File | Packet(s) | Commit(s) |
|---|---|---|
| `__init__.py` | VALIDATORS_INIT | `3d299a7` |
| `anti_cheat.py` | AIV_AUDIT_FIXES, ANTICHEAT_DELETED_FILE_REGEX, ANTICHEAT_FIX, ANTI_CHEAT, CI_LINT_FORMAT | `14d5fef`, `3b48465`, `6e0daaf`, `b3feb5b`, `fa7f0ac` |
| `base.py` | BASE_CLEANUP, VALIDATOR_BASE | `08ecfe4`, `e6b12e7` |
| `evidence.py` | AIV_AUDIT_FIXES, CI_LINT_FORMAT, CLI_CLEANUP, CRITIQUE_FIXES, EVIDENCE_COHERENCE_E020, EVIDENCE_RULES, EVIDENCE_VALIDATOR, PARSER_ENRICHMENT, ZEROTOUCH_FIX | `0d6b1ea`, `67f7580`, `7e6c6bb`, `7fb04c2`, `8a50936`, `8f70926`, `a4617d2`, `c26371a` |
| `links.py` | CI_LINT_FORMAT, LINKS_CLEANUP, LINKS_VALIDATOR, LINK_VALIDATOR, MUTABLE_CONFIG, TEST_SUITE | `12b2287`, `1b22fc5`, `3eedd50`, `6f26fb1`, `7b42e0b`, `af67c1a` |
| `pipeline.py` | AIV_AUDIT_FIXES, CI_LINT_FORMAT, CLASSIFICATION, PIPELINE, ZEROTOUCH_FIX | `3dd5d1a`, `711d192`, `7fb5f3c`, `bf71977` |
| `structure.py` | CI_LINT_FORMAT, STRUCTURE_VALIDATOR | `4ff34a3`, `a5ba911` |
| `zero_touch.py` | CI_LINT_FORMAT, CLI_CLEANUP, EVIDENCE_RULES, PARSER_ENRICHMENT, ZEROTOUCH_DEPRECATION, ZEROTOUCH_FIX, ZERO_TOUCH | `4cc63e2`, `7f1ec1c`, `8a50936`, `ee3f9cb` |

### `src\aiv\svp/`

| Source File | Packet(s) | Commit(s) |
|---|---|---|
| `__init__.py` | AIV_AUDIT_FIXES, SVP_IMPL | `3842564`, `c9990cb` |

### `src\aiv\svp\cli/`

| Source File | Packet(s) | Commit(s) |
|---|---|---|
| `__init__.py` | AIV_AUDIT_FIXES, SVP_IMPL | `3842564`, `4ecc333` |
| `main.py` | AIV_AUDIT_FIXES, CI_LINT_FORMAT, SVP_AI_FIRST_PASS, SVP_CLI_FIXES, SVP_E2E_TESTS, SVP_IMPL, SVP_RATING_CLI | `3842564`, `5400cb7`, `73d4505`, `9299186`, `92c520f`, `a3652b6`, `e523989` |

### `src\aiv\svp\lib/`

| Source File | Packet(s) | Commit(s) |
|---|---|---|
| `__init__.py` | AIV_AUDIT_FIXES, SVP_IMPL | `3842564`, `611365e` |
| `models.py` | AIV_AUDIT_FIXES, CI_LINT_FORMAT, FALSIFIABILITY_SVP_S014, SVP_AI_FIRST_PASS, SVP_AI_SESSION_MODELS, SVP_IMPL, SVP_RATING_CLI | `3842564`, `5400cb7`, `8246c99`, `9af7633`, `a1fab9f`, `cee0ec9`, `d8b6225` |
| `rating.py` | CI_LINT_FORMAT, SVP_RATING_ENGINE | `a7fe749`, `a9432ae`, `df15358` |

### `src\aiv\svp\lib\validators/`

| Source File | Packet(s) | Commit(s) |
|---|---|---|
| `__init__.py` | AIV_AUDIT_FIXES, SVP_IMPL | `1dd9764`, `3842564` |
| `session.py` | AIV_AUDIT_FIXES, CI_LINT_FORMAT, FALSIFIABILITY_SVP_S014, SVP_AI_VALIDATOR_RULES, SVP_IMPL | `3842564`, `50303e7`, `53b9612`, `b50125e`, `d8b6225` |

### `tests/`

| Source File | Packet(s) | Commit(s) |
|---|---|---|
| `conftest.py` | AIV_AUDIT_FIXES, CI_LINT_FORMAT, CONFTEST, CONFTEST_E2E_FIXTURES | `0260232`, `6dda8e7`, `8903f10`, `d33a9e5` |

### `tests\integration/`

| Source File | Packet(s) | Commit(s) |
|---|---|---|
| `__init__.py` | TEST_INTEGRATION_INIT | `270136e` |
| `test_e2e_compliance.py` | CI_LINT_FORMAT, CRITIQUE_FIXES, CRITIQUE_TEST_GAPS, E2E_COMPLIANCE_TESTS, E2E_TEST_FIXES, FALSIFIABILITY_CT013 | `245e786`, `5998e73`, `90557ff`, `dca3d1f`, `dd4daf0`, `ffd62ca` |
| `test_full_workflow.py` | CI_LINT_FORMAT, TEST_WORKFLOW | `12147f1`, `c222774` |
| `test_svp_full_workflow.py` | CI_LINT_FORMAT, SVP_CLI_FIXES, SVP_E2E_TESTS | `9299186`, `a3652b6`, `a7724ea` |

### `tests\unit/`

| Source File | Packet(s) | Commit(s) |
|---|---|---|
| `__init__.py` | TEST_UNIT_INIT | `7e4ae3f` |
| `test_auditor.py` | AUDITOR_TESTS, AUDITOR_TEST_REFINEMENT, CI_LINT_FORMAT | `0a6f437`, `22f7c10`, `ac0085e` |
| `test_coverage.py` | AIV_AUDIT_FIXES, CI_LINT_FORMAT, TEST_COVERAGE_R0_UPDATE | `2ea606e`, `90e23b6`, `b5291cb` |
| `test_guard.py` | AIV_AUDIT_FIXES, CI_LINT_FORMAT, GUARD_REFACTOR | `779b9d2`, `8ab3eca`, `ca8c8af` |
| `test_models.py` | AIV_AUDIT_FIXES, CI_LINT_FORMAT, TEST_MODELS, TEST_SUITE | `2092704`, `563f054`, `90830ab`, `af67c1a` |
| `test_parser.py` | AIV_AUDIT_FIXES, CI_LINT_FORMAT, PARSER_REGRESSION_TESTS, TEST_SUITE | `0d857d8`, `6ca1787`, `af67c1a`, `c37ba5d` |
| `test_svp.py` | AIV_AUDIT_FIXES, CI_LINT_FORMAT, FALSIFIABILITY_SVP_S014, SVP_AI_SESSION_TESTS, SVP_IMPL, SVP_RATING_TESTS | `1b9766a`, `1f697d5`, `3842564`, `49f1310`, `674d3e4`, `afb1e15`, `d8b6225` |
| `test_validators.py` | AIV_AUDIT_FIXES, CI_LINT_FORMAT, TEST_SUITE | `af67c1a`, `b1a3fdf`, `e4ae2d6` |

## Verification Packets → Source Files

| Packet | Source File(s) | Commit(s) |
|---|---|---|
| AIV_AUDIT_FIXES | `pyproject.toml`, `src/aiv/cli/main.py`, `src/aiv/guard/github_api.py`, `src/aiv/guard/runner.py`, `src/aiv/lib/analyzers/__init__.py`, `src/aiv/lib/config.py`, `src/aiv/lib/errors.py`, `src/aiv/lib/models.py`, `src/aiv/lib/parser.py`, `src/aiv/lib/validators/anti_cheat.py`, `src/aiv/lib/validators/evidence.py`, `src/aiv/lib/validators/pipeline.py`, `src/aiv/svp/__init__.py`, `src/aiv/svp/cli/__init__.py`, `src/aiv/svp/cli/main.py`, `src/aiv/svp/lib/__init__.py`, `src/aiv/svp/lib/models.py`, `src/aiv/svp/lib/validators/__init__.py`, `src/aiv/svp/lib/validators/session.py`, `src/svp/__init__.py`, `src/svp/cli/__init__.py`, `src/svp/cli/main.py`, `src/svp/lib/__init__.py`, `src/svp/lib/models.py`, `src/svp/lib/validators/__init__.py`, `src/svp/lib/validators/session.py`, `tests/conftest.py`, `tests/unit/test_coverage.py`, `tests/unit/test_guard.py`, `tests/unit/test_models.py`, `tests/unit/test_parser.py`, `tests/unit/test_svp.py`, `tests/unit/test_validators.py` | `1454ac9`, `14d5fef`, `191f034`, `1b9766a`, `1dd9764`, `2092704`, `2ad8101`, `2ea606e`, `34ee79c`, `41d9b88`, `4784c47`, `4e87dcb`, `4ecc333`, `513351a`, `592b54a`, `611365e`, `694a960`, `6dda8e7`, `74761ae`, `750afcb`, `8ab3eca`, `92c520f`, `9a94125`, `a1fab9f`, `b1a3fdf`, `b50125e`, `bf71977`, `c26371a`, `c37ba5d`, `c9990cb`, `dbf4185`, `e1d94f1`, `e1ebeb7` |
| AIV_GUARD | `.github/workflows/aiv-guard.yml` | `60ea728` |
| ANTICHEAT_DELETED_FILE_REGEX | `src/aiv/lib/validators/anti_cheat.py` | `3b48465` |
| ANTICHEAT_FIX | `src/aiv/lib/validators/anti_cheat.py` | `6e0daaf` |
| AUDITOR_FALSE_POSITIVE_FIX | `src/aiv/lib/auditor.py` | `7633861` |
| AUDITOR_TESTS | `tests/unit/test_auditor.py` | `0a6f437` |
| AUDITOR_TEST_REFINEMENT | `tests/unit/test_auditor.py` | `ac0085e` |
| AUDIT_CLI_COMMAND | `src/aiv/cli/main.py` | `bc3982e` |
| BASE_CLEANUP | `src/aiv/lib/validators/base.py` | `08ecfe4` |
| CI_LINT_FORMAT | `.github/workflows/aiv-guard-python.yml`, `.github/workflows/ci.yml`, `src/aiv/__init__.py`, `src/aiv/cli/main.py`, `src/aiv/guard/__init__.py`, `src/aiv/guard/canonical.py`, `src/aiv/guard/github_api.py`, `src/aiv/guard/manifest.py`, `src/aiv/guard/models.py`, `src/aiv/guard/runner.py`, `src/aiv/lib/auditor.py`, `src/aiv/lib/config.py`, `src/aiv/lib/errors.py`, `src/aiv/lib/models.py`, `src/aiv/lib/parser.py`, `src/aiv/lib/validators/anti_cheat.py`, `src/aiv/lib/validators/evidence.py`, `src/aiv/lib/validators/links.py`, `src/aiv/lib/validators/pipeline.py`, `src/aiv/lib/validators/structure.py`, `src/aiv/lib/validators/zero_touch.py`, `src/aiv/svp/cli/main.py`, `src/aiv/svp/lib/models.py`, `src/aiv/svp/lib/rating.py`, `src/aiv/svp/lib/validators/session.py`, `tests/conftest.py`, `tests/integration/test_e2e_compliance.py`, `tests/integration/test_full_workflow.py`, `tests/integration/test_svp_full_workflow.py`, `tests/unit/test_auditor.py`, `tests/unit/test_coverage.py`, `tests/unit/test_guard.py`, `tests/unit/test_models.py`, `tests/unit/test_parser.py`, `tests/unit/test_svp.py`, `tests/unit/test_validators.py` | `09283a0`, `0d857d8`, `11cfb83`, `1f697d5`, `22f7c10`, `245e786`, `24c0e6b`, `2b0aa56`, `2fa0f15`, `3535166`, `3dd5d1a`, `3f1db42`, `4ff34a3`, `50d9cad`, `53b9612`, `563f054`, `56af5e7`, `5f0f951`, `63dfe83`, `6d708e6`, `7b42e0b`, `90e23b6`, `9af7633`, `a4617d2`, `a7724ea`, `a7fe749`, `b3feb5b`, `bb3fe91`, `c222774`, `ca8c8af`, `d33a9e5`, `e4ae2d6`, `e523989`, `ee3f9cb`, `efc32ee`, `fea5aed` |
| CLASSIFICATION | `src/aiv/lib/models.py`, `src/aiv/lib/parser.py`, `src/aiv/lib/validators/pipeline.py` | `711d192` |
| CLI_CLEANUP | `src/aiv/cli/main.py`, `src/aiv/lib/parser.py`, `src/aiv/lib/validators/evidence.py`, `src/aiv/lib/validators/zero_touch.py` | `8a50936`, `9214766` |
| CONFTEST_E2E_FIXTURES | `tests/conftest.py` | `0260232` |
| CRITIQUE_FIXES | `.github/workflows/aiv-guard.yml`, `.husky/pre-commit`, `src/aiv/cli/main.py`, `src/aiv/lib/validators/evidence.py`, `tests/integration/test_e2e_compliance.py` | `5ced0b3`, `7e6c6bb`, `9955e75`, `adae01d`, `ffd62ca` |
| CRITIQUE_TEST_GAPS | `tests/integration/test_e2e_compliance.py` | `dd4daf0` |
| DEAD_MODULE_REMOVAL | `src/aiv/guard/security.py`, `src/aiv/lib/analyzers/diff.py`, `src/aiv/lib/validators/exceptions.py` | `e06ee44` |
| E2E_COMPLIANCE_TESTS | `tests/integration/test_e2e_compliance.py` | `dca3d1f` |
| E2E_TEST_FIXES | `tests/integration/test_e2e_compliance.py` | `5998e73` |
| EVIDENCE_COHERENCE_E020 | `src/aiv/lib/validators/evidence.py` | `0d6b1ea` |
| EVIDENCE_PIPELINE | `.github/workflows/ci.yml`, `.github/workflows/verify-architecture.yml`, `src/aiv/guard/manifest.py` | `0acdfe1`, `66a874a`, `9bfac7d`, `a1cfb9f` |
| EVIDENCE_RULES | `src/aiv/lib/parser.py`, `src/aiv/lib/validators/evidence.py`, `src/aiv/lib/validators/zero_touch.py` | `8a50936`, `8f70926` |
| EVIDENCE_VALIDATOR | `src/aiv/lib/validators/evidence.py` | `67f7580`, `7fb04c2` |
| FALSIFIABILITY_CT013 | `src/aiv/guard/canonical.py`, `tests/integration/test_e2e_compliance.py` | `90557ff` |
| FALSIFIABILITY_GUIDED_GEN | `src/aiv/cli/main.py` | `464c063` |
| FALSIFIABILITY_SVP_S014 | `src/aiv/svp/lib/models.py`, `src/aiv/svp/lib/validators/session.py`, `tests/unit/test_svp.py` | `d8b6225` |
| FILE_PACKET_MAP | `scripts/map_packets.py` | `f3202e4` |
| GENERATE_CMD | `src/aiv/cli/main.py` | `d56b589` |
| GENERATOR_CLASS_E_FIX | `src/aiv/cli/main.py` | `8b8f941` |
| GITIGNORE | `.gitignore` | `83c5a1c` |
| GUARD_REFACTOR | `.github/workflows/aiv-guard-python.yml`, `src/aiv/guard/__init__.py`, `src/aiv/guard/__main__.py`, `src/aiv/guard/canonical.py`, `src/aiv/guard/github_api.py`, `src/aiv/guard/manifest.py`, `src/aiv/guard/models.py`, `src/aiv/guard/runner.py`, `tests/unit/test_guard.py` | `779b9d2` |
| LINKS_CLEANUP | `src/aiv/lib/validators/links.py` | `3eedd50` |
| LINK_VALIDATOR | `src/aiv/lib/validators/links.py` | `6f26fb1` |
| MAIN_ENTRY | `src/aiv/__main__.py` | `57482d9` |
| MISTUNE_REMOVAL | `pyproject.toml` | `42c7869` |
| MODELS_CLEANUP | `src/aiv/lib/models.py` | `4f2f07d` |
| MUTABLE_CONFIG | `src/aiv/lib/models.py`, `src/aiv/lib/validators/links.py` | `1b22fc5` |
| PACKET_AUDITOR | `src/aiv/lib/auditor.py` | `39d1685` |
| PARSER_CLEANUP | `src/aiv/lib/parser.py` | `dfe6438` |
| PARSER_CODEBLOCK_FIX | `src/aiv/lib/parser.py` | `304d47e` |
| PARSER_ENRICHMENT | `src/aiv/lib/parser.py`, `src/aiv/lib/validators/evidence.py`, `src/aiv/lib/validators/zero_touch.py` | `2158886`, `8a50936` |
| PARSER_REGRESSION_TESTS | `tests/unit/test_parser.py` | `6ca1787` |
| PARSER_SUBSTANCE_FIX | `src/aiv/lib/parser.py` | `36071ce` |
| PARSER_SUBSTANCE_REFINE | `src/aiv/lib/parser.py` | `4f41529` |
| PRECOMMIT | `.husky/pre-commit` | `c4128a1` |
| PRECOMMIT_HOOK_FIX | `.husky/pre-commit` | `b25af40` |
| PR_TEMPLATE | `.github/PULL_REQUEST_TEMPLATE.md` | `acf0766` |
| SNAPSHOT_WINDOWS_FIX | `.husky/pre-commit` | `0b00c63` |
| SVP_AI_FIRST_PASS | `src/aiv/svp/cli/main.py`, `src/aiv/svp/lib/models.py` | `5400cb7` |
| SVP_AI_SESSION_MODELS | `src/aiv/svp/lib/models.py` | `cee0ec9` |
| SVP_AI_SESSION_TESTS | `tests/unit/test_svp.py` | `afb1e15` |
| SVP_AI_VALIDATOR_RULES | `src/aiv/svp/lib/validators/session.py` | `50303e7` |
| SVP_CLI_FIXES | `src/aiv/svp/cli/main.py`, `tests/integration/test_svp_full_workflow.py` | `a3652b6` |
| SVP_E2E_TESTS | `src/aiv/svp/cli/main.py`, `tests/integration/test_svp_full_workflow.py` | `9299186` |
| SVP_IMPL | `src/aiv/cli/main.py`, `src/aiv/svp/__init__.py`, `src/aiv/svp/cli/__init__.py`, `src/aiv/svp/cli/main.py`, `src/aiv/svp/lib/__init__.py`, `src/aiv/svp/lib/models.py`, `src/aiv/svp/lib/validators/__init__.py`, `src/aiv/svp/lib/validators/session.py`, `tests/unit/test_svp.py` | `3842564` |
| SVP_RATING_CLI | `src/aiv/svp/cli/main.py`, `src/aiv/svp/lib/models.py` | `73d4505`, `8246c99` |
| SVP_RATING_ENGINE | `src/aiv/svp/lib/rating.py` | `a9432ae`, `df15358` |
| SVP_RATING_TESTS | `tests/unit/test_svp.py` | `49f1310`, `674d3e4` |
| TEST_COVERAGE_R0_UPDATE | `tests/unit/test_coverage.py` | `b5291cb` |
| TEST_SUITE | `src/aiv/lib/validators/links.py`, `tests/unit/test_models.py`, `tests/unit/test_parser.py`, `tests/unit/test_validators.py` | `af67c1a` |
| VERIFY_ARCH | `.github/workflows/verify-architecture.yml` | `03c4bd0` |
| ZEROTOUCH_DEPRECATION | `src/aiv/lib/validators/zero_touch.py` | `7f1ec1c` |
| ZEROTOUCH_FIX | `src/aiv/lib/models.py`, `src/aiv/lib/parser.py`, `src/aiv/lib/validators/evidence.py`, `src/aiv/lib/validators/pipeline.py`, `src/aiv/lib/validators/zero_touch.py` | `711d192`, `8a50936` |

## Unmapped Source Files

These files were committed without an accompanying verification packet.

- `AUDIT_REPORT.md`
- `CHANGELOG.md`
- `FILE_PACKET_MAP.json`
- `FILE_PACKET_MAP.md`
- `LICENSE`
- `README.md`
- `SPECIFICATION.md`
- `docs/AIV_SVP_PROTOCOL_USER_STORY.md`
- `docs/specs/AIV-SUITE-SPEC-V1.0-CANONICAL_2025-12-19.md`
- `docs/specs/E2E_COMPLIANCE_TEST_SUITE_SPEC.md`
- `docs/specs/SVP-SUITE-SPEC-V1.0-CANONICAL-2025-12-20.md`

## Unmapped Packets (Packet-Only Commits)

These packets were committed alone (e.g., SHA backfill, classification fix).

- AIV_IMPLEMENTATION
- GITKEEP
- TEMPLATE

## Ghost Packets (Deleted from Disk)

These packets appeared in git history but have been deleted 
(typically consolidated into a larger packet like AIV_IMPLEMENTATION).

| Ghost Packet | Originally Covered | Superseded By |
|---|---|---|
| AIV_INIT | `src/aiv/__init__.py` | AIV_IMPLEMENTATION |
| ANALYZERS_INIT | `src/aiv/lib/analyzers/__init__.py` | AIV_IMPLEMENTATION |
| ANTI_CHEAT | `src/aiv/lib/validators/anti_cheat.py` | AIV_IMPLEMENTATION |
| CLI_INIT | `src/aiv/cli/__init__.py` | AIV_IMPLEMENTATION |
| CLI_MAIN | `src/aiv/cli/main.py` | AIV_IMPLEMENTATION |
| CONFIG | `src/aiv/lib/config.py` | AIV_IMPLEMENTATION |
| CONFTEST | `tests/conftest.py` | AIV_IMPLEMENTATION |
| DIFF_ANALYZER | `src/aiv/lib/analyzers/diff.py` | AIV_IMPLEMENTATION |
| ERRORS | `src/aiv/lib/errors.py` | AIV_IMPLEMENTATION |
| EXCEPTIONS | `src/aiv/lib/validators/exceptions.py` | AIV_IMPLEMENTATION |
| GUARD_INIT | `src/aiv/guard/__init__.py` | AIV_IMPLEMENTATION |
| LIB_INIT | `src/aiv/lib/__init__.py` | AIV_IMPLEMENTATION |
| LINKS_VALIDATOR | `src/aiv/lib/validators/links.py` | AIV_IMPLEMENTATION |
| MODELS | `src/aiv/lib/models.py` | AIV_IMPLEMENTATION |
| PARSER | `src/aiv/lib/parser.py` | AIV_IMPLEMENTATION |
| PIPELINE | `src/aiv/lib/validators/pipeline.py` | AIV_IMPLEMENTATION |
| PYPROJECT | `pyproject.toml` | AIV_IMPLEMENTATION |
| PY_TYPED | `src/aiv/py.typed` | AIV_IMPLEMENTATION |
| SECURITY | `src/aiv/guard/security.py` | AIV_IMPLEMENTATION |
| STRUCTURE_VALIDATOR | `src/aiv/lib/validators/structure.py` | AIV_IMPLEMENTATION |
| TEST_INTEGRATION_INIT | `tests/integration/__init__.py` | AIV_IMPLEMENTATION |
| TEST_MODELS | `tests/unit/test_models.py` | AIV_IMPLEMENTATION |
| TEST_UNIT_INIT | `tests/unit/__init__.py` | AIV_IMPLEMENTATION |
| TEST_WORKFLOW | `tests/integration/test_full_workflow.py` | AIV_IMPLEMENTATION |
| VALIDATORS_INIT | `src/aiv/lib/validators/__init__.py` | AIV_IMPLEMENTATION |
| VALIDATOR_BASE | `src/aiv/lib/validators/base.py` | AIV_IMPLEMENTATION |
| ZERO_TOUCH | `src/aiv/lib/validators/zero_touch.py` | AIV_IMPLEMENTATION |

## Deleted Source Files

These files appeared in git history but no longer exist on disk 
(typically relocated or removed during refactoring).

- `src/aiv/guard/security.py` (was: DEAD_MODULE_REMOVAL, SECURITY)
- `src/aiv/lib/analyzers/__init__.py` (was: AIV_AUDIT_FIXES, ANALYZERS_INIT)
- `src/aiv/lib/analyzers/diff.py` (was: DEAD_MODULE_REMOVAL, DIFF_ANALYZER)
- `src/aiv/lib/validators/exceptions.py` (was: DEAD_MODULE_REMOVAL, EXCEPTIONS)
- `src/svp/__init__.py` (was: AIV_AUDIT_FIXES)
- `src/svp/cli/__init__.py` (was: AIV_AUDIT_FIXES)
- `src/svp/cli/main.py` (was: AIV_AUDIT_FIXES)
- `src/svp/lib/__init__.py` (was: AIV_AUDIT_FIXES)
- `src/svp/lib/models.py` (was: AIV_AUDIT_FIXES)
- `src/svp/lib/validators/__init__.py` (was: AIV_AUDIT_FIXES)
- `src/svp/lib/validators/session.py` (was: AIV_AUDIT_FIXES)
