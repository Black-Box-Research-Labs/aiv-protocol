# Claim-Aware Evidence Routing — Design Plan

## Problem Statement

The evidence collector runs the **same scan for every commit** regardless of what
was claimed. This produces three forms of residual verification theater:

1. **Class F = Class C + Class A restated.** "No test files deleted" is already in
   Class C. "Full test suite passes" is already in Class A. Class F contributes
   zero new information.

2. **Class A lists tests but doesn't tie them to claims.** If you claim "xdist
   import activates correctly," the packet lists 17 tests but doesn't say which
   one verifies *that specific claim*. A verifier must read all 17 to figure it out.

3. **Class C is claim-blind.** It runs the same 4 structural indicators (assertion
   deletions, test file deletions, skip markers, test modifications) on every
   commit. It never searches for anything specific to what was claimed.

## Retro-Test: Would Claim-Aware Evidence Have Caught Our Bugs?

### Bug 1: `import pytest_xdist` (wrong module name, parallel never activated)

**Claim:** "Parallel test execution activates correctly via pytest-xdist"

- **Class A (current):** Listed 17 test names. None of them test that `-n auto`
  actually gets appended to the pytest command. The packet showed "530 passed in
  36.40s" — if evidence were claim-aware, it would have flagged: *"No test in the
  covering set asserts that the `-n auto` flag is passed to pytest."* A verifier
  reading the claim + the test list could not confirm the claim without reading
  the source code.

- **Class A (claim-aware):** Would search the 17 tests for assertions referencing
  `xdist`, `-n`, `auto`, or `pytest_cmd`. Finding none, it would emit:
  **"WARNING: No test in covering set references claim keywords [xdist, -n, auto].
  Claim 1 may be unverified by existing tests."** This would have surfaced the gap
  *before* commit.

- **Verdict: YES, claim-aware routing would have caught this.** The claim said
  "activates correctly" but no test tested activation.

### Bug 2: `git grep pyproject` matching 41 unrelated pre-commit hook tests

**Claim:** "pytest-xdist>=3.0 added to dev dependencies"

- **Class A (current):** Listed 41 tests from `test_pre_commit_hook.py`. These
  tests mention "pyproject" because they test `_is_functional("pyproject.toml")`.
  None of them verify that a dependency was added to the dev extras.

- **Class A (claim-aware):** Would search the 41 tests for assertions referencing
  `xdist`, `dependencies`, or `dev`. Finding none, it would emit:
  **"WARNING: 41 tests reference the file but 0 reference claim keywords
  [xdist, dependencies, dev]. Relevance is likely false-positive."**

- **Verdict: YES, claim-aware routing would have caught this.** The claim said
  "pytest-xdist added to dev" but no test verified that.

### Bug 3: Class F restating Class C + Class A

- **Class F (current):** "No test files deleted. No assertions removed. Full test
  suite passes." — this is Class C + Class A in one sentence.

- **Class F (claim-aware):** Would instead produce chain-of-custody evidence:
  *"test_evidence_collector.py: created 45min ago in commit e6ae981, 18 tests,
  0 deletions since creation. git log --oneline -- tests/unit/test_evidence_collector.py
  shows 1 commit touching this file."* This is information Class C doesn't have
  (file history, not just diff scan).

- **Verdict: PARTIALLY.** Class F redundancy isn't a "bug" per se, but making it
  distinct would have provided genuinely new information about test file provenance.

## Design: Claim-Aware Evidence Routing

### Architecture

```
Claims (from --claim flags)
    │
    ▼
┌─────────────────────────┐
│  Claim Keyword Extractor │  ← NLP-lite: extract verbs, nouns, identifiers
│  "xdist", "import",     │    from each claim string
│  "activates", "parallel" │
└─────────┬───────────────┘
          │
          ▼
┌─────────────────────────────────────────────────┐
│              Evidence Collectors                  │
│                                                   │
│  Class A: For each claim, search covering tests  │
│           for claim keywords. Report per-claim   │
│           coverage: "Claim 1: 3/17 tests match"  │
│           Emit WARNING if 0 tests match a claim. │
│                                                   │
│  Class C: For each claim, identify what the      │
│           claim CHANGES and search for downstream │
│           dependencies of the old behavior.       │
│           Also: existing structural scan.         │
│                                                   │
│  Class F: DISTINCT from C. Run git log on test   │
│           files to show chain-of-custody:         │
│           creation date, commit count, last       │
│           modifier, deletion history.             │
│           NOT "no tests deleted" (that's Class C) │
└─────────────────────────────────────────────────┘
```

### Implementation Plan

#### Phase 1: Claim Keyword Extraction

Add a function `extract_claim_keywords(claims: list[str]) -> dict[int, list[str]]`
that extracts meaningful identifiers from each claim:

```python
# Input:
claims = [
    "Parallel test execution activates correctly: import xdist detects pytest-xdist",
    "Class A test relevance uses Python import-path matching instead of bare stem grep",
]

# Output:
{
    1: ["parallel", "xdist", "import", "pytest-xdist", "activates"],
    2: ["import-path", "matching", "stem", "grep", "relevance"],
}
```

Strategy: split on whitespace/punctuation, filter stopwords, keep identifiers
(snake_case, camelCase, dotted.paths, hyphenated-words), keep known code tokens.

#### Phase 2: Claim-Aware Class A

Modify `collect_class_a` to accept claims and produce per-claim coverage:

```markdown
### Class A (Execution Evidence)

- **pytest:** 530 passed, 0 failed in 19.21s

**Per-claim test coverage:**

- **Claim 1** (xdist import activates): 0/17 tests reference claim keywords
  [xdist, import, activates, parallel]
  ⚠️ WARNING: No covering test verifies this claim.

- **Claim 2** (import-path matching): 4/17 tests reference claim keywords
  [import, path, matching, grep]
  - `test_collect_parses_diff_hunks`
  - `test_collect_single_line_hunk`
  - `test_collect_new_file_fallback`
  - `test_to_markdown_includes_sha_pinned_links`
```

This transforms Class A from "here are 17 tests" to "here's which tests verify
which claims, and here's where the gaps are."

#### Phase 3: Claim-Aware Class C

Modify `collect_class_c` to accept claims and the changed file, then:

1. Run existing structural scan (assertion deletions, skip markers, etc.)
2. For each claim that describes a behavior change, search for existing code
   that depends on the old behavior:
   - Extract the function/class being modified from the diff
   - Search for callers/importers of that function
   - Report: "Function `_run_git` is imported by 4 files; none depend on the
     old return value format"

This is the hardest phase — requires AST-level understanding. Start with
grep-based caller search as a pragmatic first step.

#### Phase 4: Distinct Class F

Replace the current Class F (which restates C + A) with chain-of-custody evidence:

```markdown
### Class F (Provenance Evidence)

**Test file chain-of-custody:**

| File | Created | Commits | Last Modified | Lines | Assertions |
|------|---------|---------|---------------|-------|------------|
| `tests/unit/test_evidence_collector.py` | 2h ago (e6ae981) | 1 | 2h ago | 267 | 42 |

- No test files in `tests/` were deleted in the last 10 commits.
- `git log --oneline -5 -- tests/`: (actual output pasted here)
```

This is information that Class C (diff scan) and Class A (test results) don't
provide: the *history* of the test files, not just their current state.

## Implementation Order

1. **Phase 1: Keyword extraction** — pure function, easy to test
2. **Phase 4: Distinct Class F** — independent of claims, fixes redundancy now
3. **Phase 2: Claim-aware Class A** — highest impact, catches both retro bugs
4. **Phase 3: Claim-aware Class C** — hardest, start with grep-based caller search

## Success Criteria

After implementation, re-run the two retro-test scenarios:

1. `import pytest_xdist` bug: Class A must emit WARNING that no test verifies
   the "activates correctly" claim.
2. `pyproject` false-positive: Class A must report 0 claim-relevant tests instead
   of 41 irrelevant ones.
3. Class F must not restate anything already in Class C or Class A.

## Open Questions

- Should claim-aware warnings be blocking (prevent commit) or advisory?
  **Recommendation:** Advisory for R0/R1, blocking for R2/R3. A claim without
  test coverage at R2+ is a verification gap that should be surfaced.

- How deep should Class C caller analysis go? Full AST parsing, or grep-based?
  **Recommendation:** Start with `git grep <function_name>` for callers. AST
  parsing is Phase 2 if grep proves insufficient.
