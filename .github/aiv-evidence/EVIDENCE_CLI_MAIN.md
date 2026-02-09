# AIV Evidence File (v1.0)

**File:** `src/aiv/cli/main.py`
**Commit:** `8147dfd`
**Previous:** `89d8b8e`
**Generated:** 2026-02-09T08:14:35Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "src/aiv/cli/main.py"
  classification_rationale: "Enforcement logic changes affecting evidence quality -- standard R1"
  classified_by: "ImmortalDemonGod"
  classified_at: "2026-02-09T08:14:35Z"
```

## Claim(s)

1. aiv commit --skip-checks exits with error for R1+ tiers
2. Methodology section reflects actual tools run, not static boilerplate
3. Class E intent URLs auto-pinned from /blob/main/ to /blob/HEAD_SHA/
4. Loop variable e renamed to err to fix mypy deleted-variable error
5. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/aiv-protocol/blob/8147dfdd95040f86d6b75ccb76a66d1bb91a4003/SPECIFICATION.md](https://github.com/ImmortalDemonGod/aiv-protocol/blob/8147dfdd95040f86d6b75ccb76a66d1bb91a4003/SPECIFICATION.md)
- **Requirements Verified:** Section 1.1 defines verification theater; these gates prevent it structurally

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`8147dfd`](https://github.com/ImmortalDemonGod/aiv-protocol/tree/8147dfdd95040f86d6b75ccb76a66d1bb91a4003))

- [`src/aiv/cli/main.py#L195`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/8147dfdd95040f86d6b75ccb76a66d1bb91a4003/src/aiv/cli/main.py#L195)
- [`src/aiv/cli/main.py#L226`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/8147dfdd95040f86d6b75ccb76a66d1bb91a4003/src/aiv/cli/main.py#L226)
- [`src/aiv/cli/main.py#L1044-L1045`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/8147dfdd95040f86d6b75ccb76a66d1bb91a4003/src/aiv/cli/main.py#L1044-L1045)
- [`src/aiv/cli/main.py#L1197-L1201`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/8147dfdd95040f86d6b75ccb76a66d1bb91a4003/src/aiv/cli/main.py#L1197-L1201)
- [`src/aiv/cli/main.py#L1267-L1276`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/8147dfdd95040f86d6b75ccb76a66d1bb91a4003/src/aiv/cli/main.py#L1267-L1276)
- [`src/aiv/cli/main.py#L1346-L1355`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/8147dfdd95040f86d6b75ccb76a66d1bb91a4003/src/aiv/cli/main.py#L1346-L1355)
- [`src/aiv/cli/main.py#L1358`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/8147dfdd95040f86d6b75ccb76a66d1bb91a4003/src/aiv/cli/main.py#L1358)
- [`src/aiv/cli/main.py#L1516-L1538`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/8147dfdd95040f86d6b75ccb76a66d1bb91a4003/src/aiv/cli/main.py#L1516-L1538)
- [`src/aiv/cli/main.py#L1589`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/8147dfdd95040f86d6b75ccb76a66d1bb91a4003/src/aiv/cli/main.py#L1589)
- [`src/aiv/cli/main.py#L1614-L1615`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/8147dfdd95040f86d6b75ccb76a66d1bb91a4003/src/aiv/cli/main.py#L1614-L1615)

### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`init`** (L195): FAIL — WARNING: No tests import or call `init`
- **`close`** (L226): FAIL — WARNING: No tests import or call `close`
- **`commit_cmd`** (L1044-L1045): FAIL — WARNING: No tests import or call `commit_cmd`

**Coverage summary:** 0/3 symbols verified by tests.
- **ruff:** All checks passed
- **mypy:** Success: no issues found in 1 source file

## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | aiv commit --skip-checks exits with error for R1+ tiers | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 2 | Methodology section reflects actual tools run, not static bo... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 3 | Class E intent URLs auto-pinned from /blob/main/ to /blob/HE... | unresolved | No automatic binding available | REVIEW MANUAL REVIEW |
| 4 | Loop variable e renamed to err to fix mypy deleted-variable ... | tooling | Class A: mypy: clean | PASS VERIFIED |
| 5 | No existing tests were modified or deleted during this chang... | structural | Class C not collected | REVIEW MANUAL REVIEW |

**Verdict summary:** 1 verified, 0 unverified, 4 manual review.

---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff, pytest (645 passed, 7 failed), ruff (clean), mypy (Success: no issues found in 1 source file), AST symbol-to-test binding (3 symbols).

---

## Summary

Systemic anti-theater gates in aiv commit: real evidence or no evidence
