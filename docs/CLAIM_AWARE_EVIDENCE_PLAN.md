# Claim-Aware Evidence Routing — Design Plan

**Status:** V4 — Phases 0–8 shipped. Phase 1 bug discovered and patched:
`resolve_changed_symbols` reported only 1 symbol per hunk (smallest/innermost),
starving the claim binder. Patched to report ALL overlapping symbols.

**History:**
- V1: Keyword matching proposed → **REJECTED** (false positives, false negatives, gameable)
- V2: AST-based semantic analysis designed → **IMPLEMENTED** (Phases 0–4)
- V3: Honest audit of shipped output → **3 remaining gaps identified**
- V4: Phases 5–8 shipped (`e53f2c6`). Phase 1 resolver bug found during
  enforcement gap analysis — single-symbol-per-hunk caused claim matrix theater

---

## 1. Original Problem Statement

The evidence collector ran the **same scan for every commit** regardless of what
was claimed. This produced three forms of verification theater:

1. **Class F = Class C + Class A restated.** "No test files deleted" is already in
   Class C. "Full test suite passes" is already in Class A. Class F contributed
   zero new information.

2. **Class A listed tests but didn't tie them to claims.** If you claim "xdist
   import activates correctly," the packet listed 17 tests but didn't say which
   one verifies *that specific claim*.

3. **Class C was claim-blind.** It ran the same 4 structural indicators on every
   commit. It never searched for anything specific to what was claimed.

---

## 2. What V2 Fixed (Phases 0–4, shipped `e58b81c..6e05404`)

### Phase 0: Distinct Class F ✅

**Before:** "No test files deleted. Full test suite passes."
**After:** `git log --follow` chain-of-custody per covering test file:

| File | Commits | Created By | Last Modified By | Assertions |
|------|---------|------------|------------------|------------|
| `test_evidence_collector.py` | 2 | ImmortalDemonGod (2985156) | ImmortalDemonGod (f81b6e6) | 100 |

**Verdict:** No longer theater. Provides information Class C and A don't.

### Phase 1–2: AST Symbol Resolver + Test Graph ✅

- `resolve_changed_symbols()` maps diff line ranges → enclosing Python functions/classes
- `build_test_graph()` parses all test files for imports + calls using `ast.NodeVisitor`
- Both use stdlib `ast` — zero external dependencies, deterministic

### Phase 3: Per-Symbol Class A ✅

**Before:** "551 passed, 0 failed" + flat list of 39 test names.
**After:** Per-symbol breakdown:

```
- `ClassAEvidence` (changed at L62):
  - 6 test(s) call `ClassAEvidence` directly
  - tests/unit/test_evidence_collector.py::test_renders_per_symbol_coverage
  - ...
- `ClassAEvidence.to_markdown` (changed at L67-L69):
  - WARNING: No tests import or call `to_markdown`
```

**Verdict:** The WARNING on `to_markdown` is genuinely anti-theater — the old
system would have said "39 tests covering changed file" and hidden this gap.

### Phase 4: Downstream Class C ✅

**Before:** "No test files deleted. No assertions removed."
**After:** Same structural scan PLUS:

```
Downstream impact analysis (AST):
- `find_downstream_callers` is called by:
  - `src/aiv/cli/main.py::commit_cmd`
```

**Verdict:** Downstream callers are new information about blast radius.

---

## 3. Retro-Test Results (Verified by Automated Tests)

### Bug 1: `import pytest_xdist` (wrong module name)

`test_retro_xdist_bug` in `test_evidence_collector.py` proves:
- AST finds tests import `ClassAEvidence` but 0 tests call `collect_class_a`
- System emits: `WARNING: No tests import or call collect_class_a`
- **CAUGHT** — deterministically, not by keyword luck

### Bug 2: `pyproject` false-positive (41 unrelated tests)

- `pyproject.toml` is not a `.py` file → AST analysis not available
- System reports 0 tests instead of 41 false positives
- **CAUGHT** — structural impossibility, not heuristic

### Bug 3: Class F redundancy

- Class F now shows git log chain-of-custody, not "tests pass"
- **FIXED** — architecturally distinct

---

## 4. Post-Implementation Theater Audit

**Methodology:** Compared the actual packet output from
`VERIFICATION_PACKET_EVIDENCE_COLLECTOR.md` (commit `e58b81c`, R3) and
`VERIFICATION_PACKET_MAIN.md` (commit `e405110`, R2) against a pre-AST packet
(`VERIFICATION_PACKET_AUDITOR.md`, commit `ed1639b`) using the definition:

> **Verification theater** = evidence that looks plausible but is not
> claim-specific. A verifier cannot determine if the claims are actually
> verified by reading the evidence.

### Scorecard

| Class | Pre-AST | Post-AST | Still Theater? |
|-------|---------|----------|----------------|
| **E** | "See linked spec" | SHA-pinned link + specific requirement text | **No** |
| **B** | Bare filename | SHA-pinned line-range permalinks | **No** |
| **A** | "499 passed" | Per-symbol AST coverage + WARNINGs for gaps | **Partially** |
| **C** | "tests pass, nothing deleted" | Structural scan + downstream callers | **Partially** |
| **D** | N/A | "See Class B" | **Yes** |
| **F** | "No test files deleted. Tests pass." | Git log chain-of-custody table | **No** |

### Three Remaining Forms of Theater

#### Theater Gap 1: "N passed, 0 failed" is still "CI green"

The global pytest summary line `551 passed, 0 failed in 29.19s` appears in every
packet regardless of what was changed. It proves nothing about any specific claim.
It would be **identical for a no-op commit.** This is the textbook definition of
verification theater — evidence that looks reassuring but carries zero
claim-specific information.

**Evidence from actual packet:**
```
- **pytest:** 551 passed, 0 failed in 29.19s
```

A verifier reading this learns nothing about whether `ClassAEvidence.to_markdown`
renders per-symbol coverage (Claim 1) or whether `find_downstream_callers` excludes
the committed file (Claim 3).

#### Theater Gap 2: No Claim→Evidence Binding

The packet lists 5 claims and lists per-symbol evidence, but **never says which
evidence verifies which claim.** The verifier must mentally match:

- Claim 1: "ClassAEvidence.to_markdown renders per-symbol AST coverage..."
- Evidence: "`ClassAEvidence.to_markdown` — WARNING: No tests import or call `to_markdown`"

These two facts together mean **Claim 1 is unverified** — but the packet still
passes validation. Worse: the evidence *correctly identifies the gap* but the
system doesn't *connect it to the claim it invalidates.*

This is the **structural root cause** of the other two gaps. Without claim→evidence
binding, the system cannot know that a WARNING makes a specific claim unverified,
which means it cannot enforce blocking behavior.

#### Theater Gap 3: WARNINGs Don't Block

The AST analysis correctly identifies:
- `commit_cmd` — WARNING: 0 tests call this function
- `to_markdown` — WARNING: 0 tests call this method

But the commit goes through anyway. The system **documents** the gap but doesn't
**act** on it. This is honest — which is better than the old system — but it means
a packet can pass validation while containing evidence that explicitly says its
claims are unverified.

**Evidence from actual packet (MAIN.md):**
```
- `commit_cmd` (changed at L753):
  - WARNING: No tests import or call `commit_cmd`
```

This commit claimed "aiv commit now runs resolve_changed_symbols + build_test_graph
+ find_covering_tests for Python files" and the evidence says 0 tests verify this.
The commit shipped anyway.

---

## 5. V1 Approach: Keyword Matching — REJECTED

The initial V1 plan proposed "NLP-lite" keyword extraction from claim strings.
Rejected for three reasons:

1. **False Negatives:** Keywords miss synonyms. Claim says "activates"; test says
   "is_activated". Code uses `import xdist as _` — idiomatic but keyword-blind.

2. **False Positives:** The `pyproject` → 41 tests bug proved keywords match
   mentions, not meaning.

3. **Gameable:** AI generates claims that match test names without verifying
   substance. Machine-optimized theater.

---

## 6. Design for Remaining Gaps (V3)

### Gap 1 Fix: Replace Global Metric with Per-Symbol Verdicts

**Problem:** `551 passed, 0 failed` is claim-blind.

**Design:** Remove the global summary line from Class A when per-symbol coverage
is available. Instead, each symbol gets a verdict:

```markdown
### Class A (Execution Evidence)

**Per-symbol test coverage (AST analysis):**

- **`ClassAEvidence`** (L62): ✅ 6 tests call directly
- **`ClassAEvidence.to_markdown`** (L67-L69): ❌ 0 tests call — UNVERIFIED
- **`DownstreamCaller`** (L73-L90): ✅ 1 test calls directly
- **`find_downstream_callers`** (L102-L110): ✅ 3 tests call directly

**Overall:** 4/6 symbols covered. 2 symbols lack direct test coverage.
**Linter/type checks:** ruff clean, mypy 1 error
```

The global "551 passed" provides no signal. The per-symbol verdicts do.
When AST coverage is not available (non-Python files), fall back to the global
metric with an honest annotation: "Global metric only — no per-symbol analysis
available for non-Python files."

**Changes:**
- `ClassAEvidence.to_markdown()`: suppress global metric when `symbol_coverage`
  is populated; emit per-symbol verdict summary
- Keep global metric only as fallback for non-Python or `--skip-checks`

### Gap 2 Fix: Claim→Evidence Binding

**Problem:** Claims and evidence live in separate sections with no cross-reference.

**Design:** After the per-symbol evidence, add a **Claim Verification Matrix**
that explicitly maps each claim to the evidence that supports or refutes it:

```markdown
## Claim Verification Matrix

| # | Claim | Changed Symbol(s) | Tests Calling Symbol | Verdict |
|---|-------|-------------------|---------------------|---------|
| 1 | ClassAEvidence.to_markdown renders per-symbol AST coverage... | `ClassAEvidence.to_markdown` | 0 | ❌ UNVERIFIED |
| 2 | ClassCEvidence.to_markdown renders downstream impact... | `ClassCEvidence.to_markdown` | 0 | ❌ UNVERIFIED |
| 3 | find_downstream_callers scans src/ AST... | `find_downstream_callers` | 3 | ✅ VERIFIED |
| 4 | DownstreamCaller dataclass groups callers... | `DownstreamCaller` | 1 | ✅ VERIFIED |
| 5 | No existing tests modified or deleted | — | Class C: clean | ✅ VERIFIED |
```

**How it works:**
1. For each claim, use NLP-free heuristic: find the changed symbol whose name
   appears in the claim text (substring match on symbol names, not keywords)
2. Look up the symbol in the per-symbol coverage results
3. If a symbol has ≥1 calling test → VERIFIED
4. If a symbol has 0 calling tests → UNVERIFIED
5. For structural claims ("no tests deleted") → cross-reference Class C
6. For non-Python files → mark as "NO AST AVAILABLE"

**Why this isn't keyword matching:** We're matching **symbol names** (which are
exact identifiers from the AST) against claim text, not extracting semantic
keywords. `find_downstream_callers` is a function name, not a keyword. If the
claim doesn't contain the symbol name, the binding is marked "MANUAL REVIEW."

**Changes:**
- New dataclass `ClaimVerification` with fields: claim_index, claim_text,
  matched_symbols, test_count, verdict
- New function `bind_claims_to_evidence(claims, symbol_coverage, class_c)`
- Emit matrix in packet between Evidence and Verification Methodology sections
- `commit_cmd` passes `--claim` strings to the binding function

### Gap 3 Fix: WARNING Enforcement at R3

**Problem:** WARNINGs are informational only. Commits pass with unverified claims.

**Design:** At R3, if the Claim Verification Matrix shows ANY claim as UNVERIFIED,
the commit is blocked with an actionable error:

```
ERROR: R3 commit has 2 unverified claims:
  Claim 1: "ClassAEvidence.to_markdown renders..." — 0 tests call `to_markdown`
  Claim 2: "ClassCEvidence.to_markdown renders..." — 0 tests call `to_markdown`

Options:
  1. Add tests that call the uncovered symbol(s)
  2. Reclassify to R2 if this is not a critical surface
  3. Use --force to override (recorded in packet as an acknowledged gap)
```

**Enforcement tiers:**

| Tier | Unverified Claim Behavior |
|------|--------------------------|
| R0 | No AST analysis (trivial commits) |
| R1 | Advisory: WARNINGs in packet, no block |
| R2 | Advisory: WARNINGs + Claim Verification Matrix |
| R3 | **Blocking:** UNVERIFIED claims fail validation |

**`--force` escape hatch:** At R3, the user can pass `--force` to override. The
packet records this as:

```markdown
**Acknowledged gaps (--force override):**
- Claim 1: UNVERIFIED — `to_markdown` has 0 test callers (user accepted risk)
```

This preserves the audit trail. The gap is documented, not hidden.

**Changes:**
- `commit_cmd`: after generating packet, if R3 and any claim is UNVERIFIED,
  block unless `--force` flag is set
- Add `--force` flag to `commit_cmd`
- Packet template includes "Acknowledged gaps" section when `--force` is used

### Gap 4: Class D Is Pure Theater

**Problem:** Class D says "See Class B scope inventory for line-range change details."
This is a pointer to existing evidence. It adds zero new information.

**Design:** Two options:

**Option A (recommended):** Remove Class D from the packet when no differential
analysis is available. An empty section is more honest than a pointer that
pretends to be evidence.

**Option B:** If Class D is required by the spec, populate it with actual
differential data — e.g., `git diff --stat` summary showing lines added/removed
per hunk, or a before/after comparison of changed function signatures.

---

## 7. Risks and Trade-offs

### AST Complexity (Addressed)

AST analysis is more complex than grep. But Python's `ast` module is stdlib
(zero dependencies), well-documented, and deterministic. 39 tests verify the
implementation. The call graph is best-effort and conservative (undercounts
rather than overcounts).

### Language Specificity (Accepted)

The AST analyzer only works for Python. Non-Python files get an honest report:
"AST analysis not available for non-Python targets." No false confidence.

### Call Graph Accuracy (Accepted)

Python's dynamic dispatch means false negatives (e.g., `getattr(obj, name)()`).
This is conservative: undercounting surfaces gaps rather than hiding them.

### Claim→Symbol Binding Accuracy (New Risk)

The proposed claim binding uses substring matching of symbol names in claim text.
This has failure modes:

- **Claim doesn't mention the symbol name:** "Improved test rendering" doesn't
  contain `to_markdown`. Binding falls back to "MANUAL REVIEW."
- **Symbol name is common:** `run` matches many claims. Mitigated by matching
  fully-qualified names first (`ClassC.to_markdown` before `to_markdown`).

This is strictly better than no binding. The "MANUAL REVIEW" fallback is honest
about what the system can't determine automatically.

### R3 Blocking (New Risk)

Blocking commits at R3 could slow development if the AST analysis has false
negatives (misses a test that actually covers the symbol). Mitigated by:
- `--force` escape hatch with audit trail
- Conservative AST analysis already surfaces false negatives as WARNINGs

---

## 8. Implementation Plan

### Completed Phases

| Phase | Description | Status | Commit |
|-------|-------------|--------|--------|
| 0 | Distinct Class F (git log chain-of-custody) | ✅ Shipped | `e58b81c` |
| 1 | AST Symbol Resolver (`resolve_changed_symbols`) | ⚠️ Bug found | `e58b81c` |
| 2 | AST Test Graph (`build_test_graph`) | ✅ Shipped | `e58b81c` |
| 3 | Per-Symbol Class A (`find_covering_tests`) | ✅ Shipped | `6e05404` |
| 4 | Downstream Class C (`find_downstream_callers`) | ✅ Shipped | `6e05404` |
| 5 | Remove global metric from Class A | ✅ Shipped | `e53f2c6` |
| 6 | Claim Verification Matrix | ✅ Shipped | `e53f2c6` |
| 7 | R3 blocking + `--force` | ✅ Shipped | `e53f2c6` |
| 8 | Class D cleanup (`git diff --stat`) | ✅ Shipped | `e53f2c6` |
| 9 | Phase 1 resolver bug — multi-symbol hunks | ✅ Patched | pending |

### Phase 1 Bug: Single-Symbol-Per-Hunk (V4 Discovery)

**Problem:** `resolve_changed_symbols()` picked only the **smallest** (innermost)
symbol per diff hunk. When a hunk spanned multiple functions (common for large
additions), only one symbol was reported. This starved `bind_claims_to_evidence()`
of symbols to match against, causing most claims to fall through to "unresolved /
MANUAL REVIEW."

**Impact:** The Claim Verification Matrix (Phase 6) existed but was theater —
it produced a table of MANUAL REVIEW entries for claims that SHOULD have been
verifiable. Example: claim "audit_commits() detects HOOK_BYPASS" contains the
symbol `audit_commits`, but the resolver only reported `_is_functional_path`
(smallest function in the same hunk). The binder couldn't match and gave up.

**Root cause:** The resolver used a "best match" pattern (smallest overlapping
symbol) inherited from IDE go-to-definition behavior. But evidence collection
needs ALL changed symbols, not just the innermost one.

**Patch:** Changed `resolve_changed_symbols()` to collect ALL symbols whose
range overlaps with each hunk, instead of only the smallest. One `for` loop
replacement. 2 new tests verify multi-symbol hunks.

---

## 9. Success Criteria (Updated)

The original 4 criteria are met. New criteria for V3:

1. **No global metric as primary evidence.** Class A must show per-symbol verdicts
   when AST is available. "N passed, 0 failed" must not be the first thing a
   verifier reads.

2. **Every claim bound to evidence.** The Claim Verification Matrix must map each
   claim to specific test coverage or explicitly mark it UNVERIFIED/MANUAL REVIEW.

3. **R3 commits with unverified claims are blocked.** Unless `--force` is used,
   in which case the gap is recorded in the packet.

4. **No pointer-only evidence classes.** Class D must contain real data or be omitted.

5. **Retro-test: all 3 original bugs still caught.** The 39 existing tests must
   continue to pass, including `test_retro_xdist_bug`.

---

## 10. Resolved Questions

- **Should the Claim Verification Matrix be a new packet section or part of
  Class A?** → **DECIDED: Own section.** It lives between Evidence and
  Verification Methodology. It cross-references multiple classes (A, C, F) so
  it doesn't belong inside any single class.

- **Should `--force` at R3 require a justification string?** → **DECIDED: Yes.**
  `--force "to_markdown is tested indirectly via integration tests"`. The
  justification is recorded in the packet. Without a justification string,
  `--force` is rejected — no silent escape hatches.

- **Should the test graph be cached?** → **DECIDED: Not yet.** Our test suite
  is <50 files. Re-parsing on every commit is <1s. Revisit at >500 test files.

---

## 11. Non-Code Claims — Best-Effort Binding

> **⚠️ REVIEW NOTE:** This section describes a best-effort heuristic for claims
> that don't reference Python symbols. The approach works for the common patterns
> we've seen, but edge cases may need manual review. Flag any concerns.

**Problem:** Not all claims reference code symbols. Examples:
- "No existing tests were modified or deleted" (structural, verified by Class C)
- "All ruff and mypy checks pass" (tooling, verified by Class A linter output)
- "Documentation updated to reflect new API" (non-Python file)

The Claim Verification Matrix must handle these without forcing everything
through the AST symbol pathway.

**Design: Claim Classification Heuristics**

Before attempting symbol binding, classify each claim into one of four types:

| Type | Detection Heuristic | Evidence Source | Example |
|------|--------------------|-----------------|---------|
| **Symbol** | Claim text contains a changed symbol name | AST per-symbol coverage | "find_downstream_callers scans src/" |
| **Structural** | Claim matches structural patterns: "no tests deleted", "no assertions removed", "no modifications" | Class C structural scan | "No existing tests were modified or deleted" |
| **Tooling** | Claim matches tooling patterns: "ruff", "mypy", "lint", "type check" | Class A linter/mypy output | "All ruff checks pass" |
| **Unresolved** | None of the above match | Mark as MANUAL REVIEW | "Improved developer experience" |

**Classification rules (applied in order):**

1. **Symbol match (highest priority):** If any changed symbol name is a
   substring of the claim text (case-insensitive, longest match first to avoid
   `run` matching before `commit_cmd`), classify as Symbol. Bind to that
   symbol's coverage data.

2. **Structural match:** If the claim text matches any of these patterns
   (case-insensitive regex):
   - `no.*(test|assertion|file).*(delet|modif|remov|chang)`
   - `no.*(regression|breaking)`
   - `existing.*(test|suite).*(pass|green|intact)`

   → Classify as Structural. Verdict is VERIFIED if Class C structural scan
   shows all-clean, UNVERIFIED if any indicator fires.

3. **Tooling match:** If the claim text contains any of:
   `ruff`, `mypy`, `lint`, `type.?check`, `format`

   → Classify as Tooling. Verdict is VERIFIED if the corresponding tool
   reported clean in Class A, UNVERIFIED if errors were found.

4. **Unresolved (fallback):** No match. Verdict is MANUAL REVIEW. The matrix
   renders this honestly:

   ```
   | 6 | Improved developer experience | — | MANUAL REVIEW | ⚠️ |
   ```

   This is not theater — it explicitly flags that the system cannot
   automatically verify this claim. A human must decide.

**Example Claim Verification Matrix with mixed claim types:**

```markdown
## Claim Verification Matrix

| # | Claim | Type | Evidence | Verdict |
|---|-------|------|----------|---------|
| 1 | find_downstream_callers scans src/ AST... | Symbol | 3 tests call `find_downstream_callers` | ✅ VERIFIED |
| 2 | No existing tests modified or deleted | Structural | Class C: 0 deletions, 0 modifications | ✅ VERIFIED |
| 3 | All ruff checks pass | Tooling | Class A: ruff clean | ✅ VERIFIED |
| 4 | ClassAEvidence.to_markdown renders... | Symbol | 0 tests call `to_markdown` | ❌ UNVERIFIED |
| 5 | Improved developer experience | Unresolved | — | ⚠️ MANUAL REVIEW |
```

**Verdict summary:** 3/5 verified, 1 unverified, 1 manual review.
At R3, claim 4 would block. Claim 5 (MANUAL REVIEW) does NOT block — the
system is honest that it can't verify, but doesn't assume the worst.

> **⚠️ REVIEW NOTE:** The structural and tooling patterns above are based on
> the claim texts we've seen across 43 packets. If you encounter a claim type
> that doesn't fit these four categories, we should add a new classification
> rule rather than stretching the existing ones.
