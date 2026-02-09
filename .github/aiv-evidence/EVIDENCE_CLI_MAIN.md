# AIV Evidence File (v1.0)

**File:** `src/aiv/cli/main.py`
**Commit:** `533081b`
**Previous:** `8d91744`
**Generated:** 2026-02-09T18:58:33Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "src/aiv/cli/main.py"
  classification_rationale: "LLM-readiness: CLI must be self-documenting for AI coding assistants"
  classified_by: "ImmortalDemonGod"
  classified_at: "2026-02-09T18:58:33Z"
```

## Claim(s)

1. aiv quickstart prints complete self-contained workflow reference for new users and LLMs
2. aiv commit rejects non-URL --intent values with clear error message
3. aiv close help text uses ASCII only (no em-dashes or section signs)
4. aiv init help text documents all created artifacts including evidence dir and pre-push hook
5. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/aiv-protocol/blob/533081b92880a9464f91d579f8b259995b9cdcc6/README.md](https://github.com/ImmortalDemonGod/aiv-protocol/blob/533081b92880a9464f91d579f8b259995b9cdcc6/README.md)
- **Requirements Verified:** README section 3: The Workflow describes the complete init-to-push workflow

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`533081b`](https://github.com/ImmortalDemonGod/aiv-protocol/tree/533081b92880a9464f91d579f8b259995b9cdcc6))

- [`src/aiv/cli/main.py#L113-L114`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/533081b92880a9464f91d579f8b259995b9cdcc6/src/aiv/cli/main.py#L113-L114)
- [`src/aiv/cli/main.py#L116-L118`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/533081b92880a9464f91d579f8b259995b9cdcc6/src/aiv/cli/main.py#L116-L118)
- [`src/aiv/cli/main.py#L239-L330`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/533081b92880a9464f91d579f8b259995b9cdcc6/src/aiv/cli/main.py#L239-L330)
- [`src/aiv/cli/main.py#L958`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/533081b92880a9464f91d579f8b259995b9cdcc6/src/aiv/cli/main.py#L958)
- [`src/aiv/cli/main.py#L978`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/533081b92880a9464f91d579f8b259995b9cdcc6/src/aiv/cli/main.py#L978)
- [`src/aiv/cli/main.py#L1456-L1466`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/533081b92880a9464f91d579f8b259995b9cdcc6/src/aiv/cli/main.py#L1456-L1466)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`init`** (L113-L114): FAIL -- WARNING: No tests import or call `init`
- **`quickstart`** (L116-L118): FAIL -- WARNING: No tests import or call `quickstart`
- **`close`** (L239-L330): FAIL -- WARNING: No tests import or call `close`
- **`commit_cmd`** (L958): FAIL -- WARNING: No tests import or call `commit_cmd`

**Coverage summary:** 0/4 symbols verified by tests.

### Code Quality (Linting & Types)

- **ruff:** All checks passed
- **mypy:** Success: no issues found in 1 source file

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | aiv quickstart prints complete self-contained workflow refer... | symbol | 0 tests call `quickstart` | FAIL UNVERIFIED |
| 2 | aiv commit rejects non-URL --intent values with clear error ... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 3 | aiv close help text uses ASCII only (no em-dashes or section... | symbol | 0 tests call `close` | FAIL UNVERIFIED |
| 4 | aiv init help text documents all created artifacts including... | symbol | 0 tests call `init` | FAIL UNVERIFIED |
| 5 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 0 verified, 3 unverified, 2 manual review.

**Acknowledged gaps (--force override):**

- Claim 1: UNVERIFIED -- 0 tests call `quickstart` (justification: Infrastructure change -- commit_cmd and quickstart lack direct unit tests)
- Claim 3: UNVERIFIED -- 0 tests call `close` (justification: Infrastructure change -- commit_cmd and quickstart lack direct unit tests)
- Claim 4: UNVERIFIED -- 0 tests call `init` (justification: Infrastructure change -- commit_cmd and quickstart lack direct unit tests)
---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff (scope inventory), AST symbol-to-test binding (0/4 symbols verified).
Ruff/mypy results are in Code Quality (not Class A) because they prove syntax/types, not behavior.

---

## Summary

Add quickstart command, validate intent URLs, fix Unicode in help text
