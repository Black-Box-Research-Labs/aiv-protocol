# Claim-Aware Evidence Routing — Design Plan

**Status:** V2 — Revised after critique of keyword-matching approach.

---

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

---

## Retro-Test: Would Each Proposed Approach Have Caught Our Bugs?

### Bug 1: `import pytest_xdist` (wrong module name, parallel never activated)

**Claim:** "Parallel test execution activates correctly via pytest-xdist"

| Approach | What it would do | Catches bug? |
|----------|------------------|--------------|
| **Current** | List 17 test names. No connection to claim. | NO |
| **Keyword matching** | Search tests for keywords ["xdist", "import", "activates"]. `import xdist as _` uses `_` — idiomatic but keyword-blind. Test named `test_parallel_execution_is_activated` uses synonyms. | UNRELIABLY — depends on naming luck |
| **AST analysis** | Parse `evidence_collector.py` AST. Identify that lines 254-259 are inside `collect_class_a`. Find all tests that import AND call `collect_class_a`. Check whether any test exercises the `import xdist` branch. | YES — deterministically finds tests covering the changed function |

### Bug 2: `git grep pyproject` matching 41 unrelated pre-commit hook tests

**Claim:** "pytest-xdist>=3.0 added to dev dependencies"

| Approach | What it would do | Catches bug? |
|----------|------------------|--------------|
| **Current** | `git grep pyproject tests/` → 41 matches in test_pre_commit_hook.py | NO — 41 false positives |
| **Keyword matching** | Search 41 tests for ["xdist", "dependencies", "dev"]. Would correctly report 0 keyword matches. | YES — but for the wrong reason (keyword absence ≠ proven irrelevance) |
| **AST analysis** | `pyproject.toml` is not a `.py` file. No Python symbol to trace. Report: "Non-Python target — no import graph available. 0 tests directly exercise this file." | YES — correctly identifies the gap with a structural explanation, not a heuristic |

### Bug 3: Class F restating Class C + Class A

| Approach | What it would do | Catches bug? |
|----------|------------------|--------------|
| **Current** | "No test files deleted. No assertions removed. Full test suite passes." | NO — pure redundancy |
| **Keyword/AST** | Neither keyword nor AST needed. Fix is independent: replace Class F content with `git log --follow` chain-of-custody data. | YES — architectural fix, not algorithmic |

---

## V1 Approach: Keyword Matching — REJECTED

The initial V1 plan proposed "NLP-lite" keyword extraction from claim strings.
This approach is rejected for three reasons identified in review:

### 1. False Negatives (Semantic Gaps)

Keywords miss synonyms. Claim says "activates"; test says "is_activated".
Claim says "detects"; test calls the function without using the word "detect".
Code uses idiomatic patterns (`import xdist as _`) that strip meaningful names.

The fundamental problem: **prose and code use different vocabularies for the same
concepts.** Keyword matching cannot bridge this gap without becoming an NLP system,
which is out of scope and unreliable.

### 2. False Positives (Noise)

The `pyproject` → 41 tests bug already proved this. Keywords match mentions, not
meaning. A test that contains the string `"pyproject.toml"` as a test fixture is
not a test that verifies `pyproject.toml` changes.

### 3. Gameable

Keyword matching creates perverse incentives: stuff claims with keywords the
machine recognizes. Or worse: the AI generates claims that happen to match test
names without actually verifying the claim substance. This is a **new form of
verification theater** — machine-optimized theater.

---

## V2 Approach: AST-Based Semantic Analysis

The fundamental insight: **don't derive structure from unstructured strings.
Start with structure.** Python's `ast` module gives us deterministic,
compiler-level code analysis with zero external dependencies.

### Key Design Decision: Auto-Extract Verification Targets

The AST critique proposed requiring `--claim-json` with explicit verification
targets. This is correct in principle but wrong on UX — it adds too much
friction to every commit.

**Better approach: auto-detect verification targets from the diff itself.**

The diff already tells us which functions/classes were modified:
- `git diff --cached -U0` gives us changed line ranges (Class B already has this)
- AST parsing of the changed file maps line ranges → function/class symbols

This means ZERO additional user input. The system can:
1. Parse the changed file's AST
2. Map each changed hunk (from Class B) to the enclosing function/class
3. Use those symbols as verification targets automatically

```
git diff --cached -U0
        │
        ▼
┌───────────────────────────┐
│  Changed Line Ranges       │  ← Already collected by Class B
│  L254-L259, L281-L329     │
└───────────┬───────────────┘
            │
            ▼
┌───────────────────────────┐
│  AST Symbol Resolver       │  ← NEW: Python ast module
│  Parses changed file       │
│  Maps line ranges to       │
│  enclosing functions:      │
│  L254-259 → collect_class_a│
│  L281-329 → collect_class_a│
└───────────┬───────────────┘
            │
            ▼
   Changed symbols:
   ["collect_class_a"]
            │
            ▼
┌───────────────────────────────────────────────────────┐
│  AST Import/Call Graph (test files)                    │
│                                                       │
│  For each test file in tests/:                        │
│    1. Parse AST                                       │
│    2. Extract imports: which symbols from which files  │
│    3. Extract calls: which functions call which symbols│
│                                                       │
│  Result: test_evidence_collector.py                   │
│    imports: collect_class_a, collect_class_b, ...     │
│    test_collect_parses_diff_hunks calls: collect_class_b │
│    test_to_markdown_includes_test_names uses: ClassAEvidence │
└───────────────────────────────────────────────────────┘
            │
            ▼
┌───────────────────────────────────────────────────────┐
│  Semantic Evidence Collectors                          │
│                                                       │
│  Class A: For each changed symbol, find tests that    │
│    IMPORT and CALL it. Report per-symbol coverage.    │
│    Cross-reference against claims.                    │
│                                                       │
│  Class C: Structural scan (existing) PLUS             │
│    downstream callers of changed symbols across       │
│    the entire src/ tree. Impact analysis.             │
│                                                       │
│  Class F: DISTINCT from C. git log --follow on        │
│    covering test files. Chain-of-custody history.     │
│    NOT "tests pass" or "no deletions."                │
└───────────────────────────────────────────────────────┘
```

### Architecture: Three New Components

#### 1. `ASTSymbolResolver` — Map diff hunks to symbols

```python
def resolve_symbols(file_path: str, line_ranges: list[tuple[int, int]]) -> list[str]:
    """Parse a Python file's AST and map line ranges to enclosing symbols.

    Example:
        resolve_symbols("evidence_collector.py", [(254, 259)])
        → ["collect_class_a"]
    """
```

Uses `ast.parse()` + `ast.walk()` to find `FunctionDef`/`ClassDef`/`AsyncFunctionDef`
nodes whose `lineno..end_lineno` range contains the changed lines.

#### 2. `ASTTestGraph` — Build import + call graph for test files

```python
@dataclass
class TestGraph:
    """Maps test files to the symbols they import and call."""
    imports: dict[str, set[str]]      # test_file → {imported_symbols}
    calls: dict[str, dict[str, set[str]]]  # test_file → {test_func → {called_symbols}}

def build_test_graph(test_dir: str = "tests/") -> TestGraph:
    """Parse all test files and build import + call relationships."""
```

Uses `ast.ImportFrom` visitor to build the import map, then `ast.Call` +
`ast.Name`/`ast.Attribute` visitor to build the call map within each `test_*`
function.

#### 3. Upgraded Collectors

**Class A (Semantic):**
```markdown
### Class A (Execution Evidence)

- **pytest:** 530 passed, 0 failed in 19.21s

**Per-symbol test coverage:**

- **`collect_class_a`** (changed at L254-259, L281-329):
  - Imported by: `tests/unit/test_evidence_collector.py`
  - Called by 4 tests:
    - `test_to_markdown_includes_test_names` (calls ClassAEvidence)
    - `test_to_markdown_warns_no_tests` (calls ClassAEvidence)
    - `test_to_markdown_ruff_errors` (calls ClassAEvidence)
    - `test_to_markdown_clean` (calls ClassAEvidence)
  - NOTE: 4 tests exercise the dataclass, but 0 tests call `collect_class_a`
    directly. The function's subprocess logic is untested.

**Claim cross-reference:**

- Claim 1: "xdist import activates correctly"
  → Changed symbol: `collect_class_a` → 0 tests call this function directly
  → WARNING: Claim references behavior inside `collect_class_a` but no test
    invokes the function. Verification gap.
```

**Class C (Semantic):**
```markdown
### Class C (Negative Evidence)

**Structural scan:** 0 assertion deletions, 0 skip markers, 0 test file deletions.

**Downstream impact analysis:**
- `collect_class_a` is called by:
  - `src/aiv/cli/main.py::commit_cmd` (line 853)
  - No other callers in src/ or tests/
- `_run` (internal helper, also modified) is called by:
  - `collect_class_a` (3 call sites)
  - `collect_class_c` (0 — uses `_run_git` instead)
  - `collect_class_f` (0 — uses `_run_git` instead)
- Downstream impact is contained to `commit_cmd` via `collect_class_a`.
```

**Class F (Provenance — distinct from C):**
```markdown
### Class F (Provenance Evidence)

**Test file chain-of-custody:**

| File | Created | Commits | Last Modified By | Assertions |
|------|---------|---------|------------------|------------|
| `tests/unit/test_evidence_collector.py` | 2h ago (e6ae981) | 2 | cascade | 42 |

**git log --oneline -5 -- tests/unit/test_evidence_collector.py:**
```
c144769 fix(lib): correct xdist import check
e6ae981 test(lib): 18 tests for evidence collector module
```

No test files renamed or deleted in the last 10 commits.
```

---

## Retro-Test: Does V2 Catch the Bugs?

### Bug 1: `import pytest_xdist` (wrong module name)

1. AST Symbol Resolver: changed lines 254-259 → enclosing symbol: `collect_class_a`
2. AST Test Graph: scan all test files for imports of `collect_class_a`
   → `test_evidence_collector.py` imports `ClassAEvidence` (the dataclass)
   → but 0 test functions actually CALL `collect_class_a` (they construct
     `ClassAEvidence` directly with mock data)
3. Class A output: "0 tests call `collect_class_a` directly. The function's
   subprocess logic (including xdist detection) is untested."
4. Claim cross-reference: Claim says "activates correctly" but the function
   is never invoked in tests.

**VERDICT: YES — V2 catches this deterministically.** Not by keyword luck but by
proving no test calls the function that contains the bug.

### Bug 2: `pyproject` false-positive (41 unrelated tests)

1. AST Symbol Resolver: `pyproject.toml` is not a `.py` file → no AST available
2. AST Test Graph: no Python symbol to search for → 0 imports, 0 calls
3. Class A output: "Non-Python target. AST analysis not available. 0 tests
   directly exercise this configuration file."
4. No false positives possible — AST analysis is structurally impossible for
   non-Python files, so the system correctly reports the gap.

**VERDICT: YES — V2 eliminates false positives entirely for non-Python files.**

### Bug 3: Class F redundancy

Class F no longer says "no tests deleted" (that's Class C) or "tests pass"
(that's Class A). It shows `git log --follow` history of covering test files.

**VERDICT: YES — V2 makes Class F structurally distinct.**

---

## Risks and Trade-offs

### Complexity

AST analysis is significantly more complex than grep. But Python's `ast` module
is stdlib (zero dependencies), well-documented, and deterministic. The call graph
doesn't need to be perfect — it's a best-effort analysis that's strictly better
than both grep and keyword matching.

### Language Specificity

The AST analyzer only works for Python. Non-Python files (`pyproject.toml`,
`.yml`, `.md`) cannot be analyzed. The system should honestly report "AST analysis
not available for non-Python targets" rather than faking relevance.

Future extension: TypeScript support via `ts-morph` (separate concern).

### Call Graph Accuracy

Python's dynamic dispatch means static call graph analysis will have false
negatives (e.g., `getattr(obj, method_name)()`). This is acceptable because:
- False negatives in the call graph mean we UNDERCOUNT covering tests
- Undercounting is conservative (surfaces gaps rather than hiding them)
- Better to miss a test than to falsely claim coverage

### Performance

Parsing ~50 Python files takes <1 second. For large repos (>500 files), we can
cache the AST graph and invalidate on file change. Not needed now.

---

## Implementation Plan

### Phase 0: Distinct Class F (no AST needed)

Replace current Class F (restates C + A) with `git log --follow` chain-of-custody.
Independent of all other phases. Fixes redundancy immediately.

**Changes:**
- `evidence_collector.py`: rewrite `collect_class_f()` to run `git log --follow`
  and `git log --oneline` on test files, count assertions via AST or grep
- No new dependencies, no new models

### Phase 1: AST Symbol Resolver

New function: given a file path and line ranges, return the enclosing symbols.
Pure function, easy to test, no side effects.

**Changes:**
- `evidence_collector.py`: add `resolve_changed_symbols(file_path, hunks)`
- Uses `ast.parse()` + walk for `FunctionDef`/`ClassDef` nodes
- Tests: mock file content, verify line-to-symbol mapping

### Phase 2: AST Test Graph

New function: parse all test files, build import map and call graph.

**Changes:**
- `evidence_collector.py`: add `build_test_graph(test_dir)`
- Import visitor: `ast.ImportFrom` → map symbol to source module
- Call visitor: `ast.Call` + `ast.Name`/`ast.Attribute` → map test func to called symbols
- Tests: mock test files, verify graph construction

### Phase 3: Semantic Class A

Wire the symbol resolver + test graph into `collect_class_a`.
Per-symbol coverage report. Claim cross-reference.

**Changes:**
- `collect_class_a` gains `claims` parameter
- For each changed symbol: find importing test files, find calling test functions
- Cross-reference claims against changed symbols
- Emit WARNING for claims with 0 covering tests

### Phase 4: Semantic Class C

Add downstream caller analysis to `collect_class_c`.

**Changes:**
- `collect_class_c` gains `changed_symbols` parameter
- For each changed symbol: find all callers across `src/` (not just tests)
- Report downstream impact scope
- Existing structural scan (assertion deletions, skip markers) unchanged

---

## Success Criteria

After full implementation, re-run the three retro-test scenarios:

1. **xdist bug:** Class A must report "0 tests call `collect_class_a` directly"
   and emit a WARNING that the claim is unverified by tests.
2. **pyproject false-positive:** Class A must report "Non-Python target, 0 tests"
   instead of 41 false matches.
3. **Class F redundancy:** Class F must contain ONLY `git log` chain-of-custody
   data. No overlap with Class C (diff scan) or Class A (test results).
4. **No false confidence:** The system must never report a test as "covering"
   a claim unless the test demonstrably imports and calls the claimed symbol.

---

## Open Questions

- **Should uncovered claims block commit at R2+?**
  Recommendation: Advisory WARNING for R0-R2. Blocking ERROR for R3.
  Rationale: R3 commits touch critical surfaces — unverified claims at R3
  are verification gaps that should not pass silently.

- **How to handle method-level resolution?**
  `ast.FunctionDef` inside `ast.ClassDef` produces `ClassName.method_name`.
  The call graph must handle `self.method()` calls by resolving the class.
  Start simple: treat methods as `ClassName.method_name` and match on method
  name only if class resolution fails.

- **Should the test graph be cached?**
  Not for now. Our test suite is <50 files. Re-parsing on every commit is <1s.
  Add caching if performance becomes an issue (>500 test files).
