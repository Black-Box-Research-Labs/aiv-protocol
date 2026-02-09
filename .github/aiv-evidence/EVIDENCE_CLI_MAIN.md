# AIV Evidence File (v1.0)

**File:** `src/aiv/cli/main.py`
**Commit:** `7eed8f4`
**Previous:** `7eed8f4`
**Generated:** 2026-02-09T09:12:11Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "src/aiv/cli/main.py"
  classification_rationale: "Quality improvements to close and generate commands"
  classified_by: "ImmortalDemonGod"
  classified_at: "2026-02-09T09:12:11Z"
```

## Claim(s)

1. aiv close extracts real claims from Layer 1 evidence files instead of generic boilerplate
2. aiv close extracts Class B file references from evidence files to fix E016 warnings
3. aiv close detects actual evidence classes (A-F) present in each evidence file
4. aiv generate scopes ruff to staged Python files when available, falls back to full src/tests/
5. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/aiv-protocol/blob/7eed8f4f8c8e17b011b4483639a81462676fdba6/src/aiv/cli/main.py](https://github.com/ImmortalDemonGod/aiv-protocol/blob/7eed8f4f8c8e17b011b4483639a81462676fdba6/src/aiv/cli/main.py)
- **Requirements Verified:** Layer 2 packets must contain meaningful claims from evidence, not boilerplate

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`7eed8f4`](https://github.com/ImmortalDemonGod/aiv-protocol/tree/7eed8f4f8c8e17b011b4483639a81462676fdba6))

- [`src/aiv/cli/main.py#L656-L667`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/7eed8f4f8c8e17b011b4483639a81462676fdba6/src/aiv/cli/main.py#L656-L667)
- [`src/aiv/cli/main.py#L670`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/7eed8f4f8c8e17b011b4483639a81462676fdba6/src/aiv/cli/main.py#L670)
- [`src/aiv/cli/main.py#L941-L943`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/7eed8f4f8c8e17b011b4483639a81462676fdba6/src/aiv/cli/main.py#L941-L943)
- [`src/aiv/cli/main.py#L945-L948`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/7eed8f4f8c8e17b011b4483639a81462676fdba6/src/aiv/cli/main.py#L945-L948)
- [`src/aiv/cli/main.py#L951-L987`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/7eed8f4f8c8e17b011b4483639a81462676fdba6/src/aiv/cli/main.py#L951-L987)
- [`src/aiv/cli/main.py#L999-L1008`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/7eed8f4f8c8e17b011b4483639a81462676fdba6/src/aiv/cli/main.py#L999-L1008)
- [`src/aiv/cli/main.py#L1014-L1022`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/7eed8f4f8c8e17b011b4483639a81462676fdba6/src/aiv/cli/main.py#L1014-L1022)
- [`src/aiv/cli/main.py#L1081-L1084`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/7eed8f4f8c8e17b011b4483639a81462676fdba6/src/aiv/cli/main.py#L1081-L1084)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`_run_local_checks`** (L656-L667): FAIL — WARNING: No tests import or call `_run_local_checks`
- **`close`** (L670): FAIL — WARNING: No tests import or call `close`

**Coverage summary:** 0/2 symbols verified by tests.
- **ruff:** All checks passed
- **mypy:** Success: no issues found in 1 source file

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | aiv close extracts real claims from Layer 1 evidence files i... | symbol | 0 tests call `close` | FAIL UNVERIFIED |
| 2 | aiv close extracts Class B file references from evidence fil... | symbol | 0 tests call `close` | FAIL UNVERIFIED |
| 3 | aiv close detects actual evidence classes (A-F) present in e... | symbol | 0 tests call `close` | FAIL UNVERIFIED |
| 4 | aiv generate scopes ruff to staged Python files when availab... | tooling | Class A: ruff: clean | PASS VERIFIED |
| 5 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 1 verified, 3 unverified, 1 manual review.

---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff, pytest (677 passed, 10 failed), ruff (clean), mypy (Success: no issues found in 1 source file), AST symbol-to-test binding (2 symbols).

---

## Summary

aiv close now produces rich packets with real claims and file refs; aiv generate scopes ruff properly
