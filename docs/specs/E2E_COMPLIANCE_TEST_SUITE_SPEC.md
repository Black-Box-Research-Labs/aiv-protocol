# E2E Compliance Test Suite — Specification

**Version:** 1.0.0  
**Date:** 2026-02-06  
**Status:** DRAFT  
**File:** `tests/integration/test_e2e_compliance.py`

---

## 1. Purpose

The existing test suite (188 tests) validates **components in isolation with synthetic data**. This spec defines an E2E compliance suite that validates **the system works end-to-end against this actual repository**.

**The question it answers:** *"If we shipped this today, would AIV catch the problems it claims to catch?"*

**Trigger:** Manual E2E testing revealed two real failures:
1. Our own verification packet (`VERIFICATION_PACKET_AIV_AUDIT_FIXES.md`) fails `aiv check` with E010 (missing Class F for bug-fix claims).
2. R3 tier enforcement is bypassable — `### Class D` headers with only "TODO" text count as present evidence in `_collect_evidence_classes` (parser.py:248-259).

---

## 2. Prerequisite Code Changes

These code changes MUST be implemented before the test suite can pass. The tests are written to assert the *correct* behavior, not the current buggy behavior.

### 2.1 Substance Patch — `_collect_evidence_classes`

**File:** `src/aiv/lib/parser.py`, method `_collect_evidence_classes` (line 248)

**Current behavior:** Counts any `### Class X` heading as evidence present, regardless of content.

**Required behavior:** Only count a section as present if its content is *substantive* — i.e., not exclusively placeholder text.

**Proposed logic:**

```python
_PLACEHOLDER_RE = re.compile(
    r"^[\s\-*]*"                       # optional leading bullets/whitespace
    r"(TODO|TBD|PENDING|N/?A|NONE|FIXME|XXX)"  # placeholder keyword
    r"[:\s.]",                         # followed by separator
    re.IGNORECASE | re.MULTILINE,
)

def _is_substantive(self, content: list[str]) -> bool:
    """Return True if section content is more than just placeholders."""
    joined = "\n".join(content).strip()
    if not joined:
        return False
    # Strip all placeholder lines; if nothing remains, it's not substantive
    non_placeholder = self._PLACEHOLDER_RE.sub("", joined).strip()
    # Must have at least some real alphanumeric content beyond punctuation
    alpha_content = re.sub(r'[^a-zA-Z0-9]', "", non_placeholder)
    # MIN_SUBSTANCE_ALPHA: conservative threshold to avoid false rejects
    # on short but legitimate evidence (e.g., "- No regressions found.")
    return len(alpha_content) >= 10
```

**Integration point:** In `_collect_evidence_classes`, wrap the `found.add(...)` call:

```python
if match:
    try:
        ev_class = EvidenceClass.from_string(match.group(1))
        if self._is_substantive(s.content):
            found.add(ev_class)
    except ValueError:
        pass
```

**Impact:** R3 packets with six empty/TODO section headers will now correctly fail E019 tier enforcement.

### 2.2 Verification Packet Fix

**File:** `.github/aiv-packets/VERIFICATION_PACKET_AIV_AUDIT_FIXES.md`

**Problem:** Missing `### Class F (Provenance Evidence)` section. The packet describes bug fixes ("resolved", "fix"), triggering the E010 bug-fix heuristic in `evidence.py:254-279`, which requires Class F evidence.

**Fix:** Add a `### Class F (Provenance)` section with substantive content documenting that no existing tests were weakened.

---

## 3. Test Layers

Six layers, organized by the user story's sufficiency claims from `AIV_SVP_PROTOCOL_USER_STORY.md` §3.

---

### Layer 1: Self-Compliance — "Does this repo follow its own protocol?"

**Class:** `TestSelfCompliance`

These tests run `aiv check` against every real packet in `.github/aiv-packets/` and verify they actually **PASS** (not just parse). The existing `TestRealPacketSmoke` in `test_full_workflow.py` only checks "doesn't crash" — that's smoke, not compliance.

#### L1-01: `test_every_real_packet_passes_lenient`

- **Parametrize** over every `VERIFICATION_PACKET_*.md` in `.github/aiv-packets/` (excluding `TEMPLATE`).
- Each packet is a separate test case, named by filename.
- **Assert:** `result.status == ValidationStatus.PASS` (zero blocking errors).
- **Pipeline mode:** Lenient (`strict_mode=False`).
- **WHY:** Proves we eat our own dog food. If our own packets fail our own validator, the system is broken or we're not following our own protocol.

#### L1-02: `test_every_real_packet_parses_classification`

- For every real packet whose raw text contains `## Classification`:
  - Parse with `PacketParser`
  - **Assert:** `packet.risk_tier is not None`
  - **Assert:** `packet.risk_tier` is a valid `RiskTier` enum value
- **WHY:** Classification is required by spec §6.1. If the parser can't extract it from our own packets, the parser is wrong.

#### L1-03: `test_cli_subprocess_check_passes`

- Run `sys.executable -m aiv check <packet_path> --no-strict` as a **subprocess** (`subprocess.run`).
- Use `sys.executable` (not bare `python`) to ensure the test runner's environment is used, avoiding global install conflicts.
- Use the `VERIFICATION_PACKET_AIV_IMPLEMENTATION.md` packet (known good).
- **Assert:** `returncode == 0`
- **Assert:** stdout contains `"Validation Passed"` or `"[OK] Result"`
- **WHY:** Tests the actual user experience, not just the Python API. Import errors, Typer wiring bugs, Rich formatting issues, and `pyproject.toml` entry point problems only surface in subprocess tests.

#### L1-04: `test_cli_subprocess_check_rejects_garbage`

- Run `sys.executable -m aiv check "This is not a verification packet at all"` as subprocess.
- **Assert:** `returncode != 0`
- **Assert:** stderr/stdout contains `"Failed to parse"` or `"Error"`
- **WHY:** Confirms the CLI actually rejects bad input, not just silently passes.

---

### Layer 2: Evidence Substance — "Does the system validate substance, not just structure?"

**Class:** `TestEvidenceSubstance`

Core user story claim: "Evidence Exists" (§3 Sufficiency Assessment, 95% confidence). A `### Class D` header with "TODO" text is not evidence — it's a heading.

#### L2-01: `test_todo_only_evidence_section_not_counted`

- Build a packet with `### Class D (Differential Evidence)` section containing only `- TODO: Before/after diff of critical behavior.`
- Parse with `PacketParser`.
- **Assert:** `EvidenceClass.DIFFERENTIAL not in packet.evidence_classes_present`
- **WHY:** This is the actual bug found in manual E2E testing. Depends on Prerequisite §2.1.

#### L2-02: `test_r3_with_empty_sections_fails`

- Build an R3 packet where `### Class D` and `### Class F` have only placeholder text (TODO/TBD/N/A).
- Classes A, B, C, E have real content.
- Run through `ValidationPipeline`.
- **Assert:** `result.status == ValidationStatus.FAIL`
- **Assert:** E019 BLOCK findings exist for Class D and Class F.
- **WHY:** R3 is the highest risk tier. If it can be trivially bypassed with empty headers, tier enforcement is theater. Depends on Prerequisite §2.1.

#### L2-03: `test_r3_with_substantive_sections_passes`

- Build the same R3 packet as L2-02, but with *real content* in D and F sections.
- **Assert:** `result.status == ValidationStatus.PASS` (no E019 findings).
- **WHY:** Ensures the substance check doesn't over-reject. The positive case must work.

#### L2-04: `test_r0_scaffold_passes_without_optional`

- Generate an R0 packet via `_build_evidence_sections("R0", ...)`.
- Wrap it in a full packet with real A and B content.
- Run through `ValidationPipeline`.
- **Assert:** `result.status == ValidationStatus.PASS`
- **Assert:** No E019 BLOCK findings.
- **WHY:** R0 should be easy. Confirms we don't over-enforce on trivial changes.

#### L2-05: `test_r2_missing_required_class_fails`

- Build an R2 packet with real A, B, E content but **no Class C** section.
- **Assert:** `result.status == ValidationStatus.FAIL`
- **Assert:** E019 BLOCK for missing Class C (Negative).
- **WHY:** R2 requires C per `pipeline.py:180`. Proves enforcement works with real content, not just header detection.

#### L2-06: `test_bugfix_claims_require_class_f`

- Build a packet whose claims contain "fix", "resolved", or "bug" but has **no `### Class F` section**.
- **Assert:** `result.status == ValidationStatus.FAIL`
- **Assert:** E010 BLOCK present.
- **WHY:** This is the exact failure mode found on our audit packet. `evidence.py:254-279` heuristic must fire.

#### L2-07: `test_bugfix_claims_with_class_f_passes`

- Same claims as L2-06 but **with** a `### Class F (Provenance)` section containing real content and a claim with `evidence_class == EvidenceClass.PROVENANCE`.
- **Assert:** `result.status == ValidationStatus.PASS` (no E010).
- **WHY:** Confirms the fix path works — adding Class F resolves E010.

---

### Layer 3: Security Properties — "Can the system be bypassed?"

**Class:** `TestSecurityProperties`

Tests adversarial inputs. The user story claims "test manipulation detected" and "evidence is immutable" with 85-95% confidence.

#### L3-01: `test_mutable_github_link_blocked`

- Packet with Class E link pointing to `/blob/main/` (mutable branch).
- **Assert:** `result.status == ValidationStatus.FAIL`
- **Assert:** E004 finding present (mutable link detection in `links.py`).
- **WHY:** Immutability is a core AIV guarantee. Mutable links = fake evidence that can be changed after approval. Uses existing `invalid_mutable_link` fixture.

#### L3-02: `test_sha_pinned_link_passes`

- Packet with Class E link pointing to `/blob/abc123def456789.../` (40-char SHA).
- **Assert:** No E004 findings.
- **WHY:** Confirms the positive case. SHA-pinned links are valid immutable evidence.

#### L3-03: `test_deleted_assertion_in_diff_blocked`

- Use `valid_minimal_packet` + diff that removes `assert` statements from a test file.
- **Assert:** `result.status == ValidationStatus.FAIL`
- **Assert:** E011 BLOCK for `deleted_assertion`.
- **WHY:** Anti-cheat is a headline feature. `anti_cheat.py:92-103` must catch this.

#### L3-04: `test_added_skip_decorator_blocked`

- Diff adding `@pytest.mark.skip(reason="...")` to a test file.
- **Assert:** E011 BLOCK for `skipped_test`.
- **WHY:** `anti_cheat.py:106-117` must catch this pattern.

#### L3-05: `test_deleted_test_file_blocked`

- Diff that deletes an entire test file (`deleted file mode 100644`).
- **Assert:** E011 BLOCK for `removed_test_file`.
- **WHY:** `anti_cheat.py:141-156` — the most aggressive manipulation pattern.

#### L3-06: `test_clean_diff_passes`

- Diff that only adds new code in a non-test file.
- **Assert:** `result.status == ValidationStatus.PASS`
- **Assert:** No E011 findings.
- **WHY:** Anti-cheat must not false-positive on clean diffs. Uses existing `diff_clean` fixture.

#### L3-07: `test_class_f_justification_overrides_anticheat` *(from critique: Justification Loop)*

- Diff with a deleted assertion (would normally trigger E011).
- Packet includes a `### Class F (Provenance)` claim with evidence_class F **and** justification text > 20 chars explaining why the assertion was removed.
- Run through full pipeline with diff.
- **Assert:** `result.status == ValidationStatus.PASS` (no E011 BLOCK).
- **WHY:** Per `anti_cheat.py:171-199`, `check_justification` should find the Class F claim and mark the finding as justified. Without this test, legitimate test refactors would be permanently blocked. This is the "positive override" case.
- **Code path:** `pipeline.py:138-157` → `anti_cheat.check_justification()` → Class F claim with `justification` field.

#### L3-08: `test_strict_mode_promotes_warnings_to_failures`

- Build a packet that produces WARN findings but no BLOCK in lenient mode (e.g., a packet missing `## Classification`, which generates E014 WARN).
- Validate in lenient mode → **Assert PASS**.
- Validate in strict mode → **Assert FAIL**.
- **WHY:** Strict mode (`pipeline.py:160-161`) is the enforcement mechanism for high-assurance environments.

#### L3-09: `test_multi_hunk_multi_file_diff` *(from critique: Multi-Hunk Diffing)*

- Diff with modifications in **three separate hunks** across **two different test files**.
- Hunk 1: Deleted assertion in `tests/test_auth.py` at line 10.
- Hunk 2: Added skip decorator in `tests/test_auth.py` at line 50.
- Hunk 3: Deleted assertion in `tests/test_payment.py` at line 25.
- **Assert:** Exactly 3 anti-cheat findings.
- **Assert:** File paths correctly track across hunks (not "unknown" or stale).
- **Assert:** Line numbers are plausible (not 0 or negative).
- **WHY:** Ensures the `AntiCheatScanner` doesn't "forget" the current filename or line offset between hunks. The diff parser at `anti_cheat.py:68-139` uses mutable `current_file` and `current_line` — multi-hunk diffs stress this state machine.

---

### Layer 4: Round-Trip — "Does generate → check work for all tiers?"

**Class:** `TestGenerateCheckRoundTrip`

Tests the full developer workflow: generate a packet scaffold, then validate it.

#### L4-01: `test_generate_then_check_passes` *(parametrized: R0, R1, R2, R3)*

- Run `sys.executable -m aiv generate test-{tier} --tier {tier} --output {tmpdir}` as subprocess.
- Then run `sys.executable -m aiv check {tmpdir}/VERIFICATION_PACKET_TEST_{TIER}.md --no-strict` as subprocess.
- **Assert:** Both exit codes == 0.
- **WHY:** This is the actual developer experience. If `generate` produces packets that fail `check`, the tool is broken.

#### L4-02: `test_generate_r3_includes_all_six_sections`

- Generate R3 packet via `_build_evidence_sections("R3", "  - TODO: list modified files")`.
- **Assert:** Output contains all six `### Class X` headers (A, B, C, D, E, F).
- **WHY:** R3 requires all six per `pipeline.py:181`. The generator must scaffold them.

#### L4-03: `test_generate_r0_omits_non_required_sections`

- Generate R0 packet via `_build_evidence_sections("R0", ...)`.
- **Assert:** Output does NOT contain `### Class C`, `### Class D`, `### Class E`, `### Class F`.
- **Assert:** Output DOES contain `### Class A` and `### Class B`.
- **WHY:** Generator shouldn't add unnecessary sections that confuse users. R0 only requires A and B per `pipeline.py:178`.

#### L4-04: `test_generate_uses_temp_git_repo` *(from critique: Git Dependency)*

- Create a temporary directory, run `git init`, create a file, `git add` it.
- Run `aiv generate test-ci --tier R1 --output {tmpdir}` from that working directory.
- **Assert:** The scope inventory in the generated packet references the added file (not "TODO: list modified files").
- **WHY:** `_detect_git_scope()` in `cli/main.py:262-296` calls `git diff --cached --name-status`. In CI environments without a `.git` folder or with shallow clones, this fails silently and falls back to "TODO". This test ensures the git integration actually works when git state exists.
- **Fixture:** A `tmp_git_repo` fixture that initializes a temporary git repo with staged files.

---

### Layer 5: Canonical Compliance — "Is the machine-readable layer consistent?"

**Class:** `TestCanonicalCompliance`

*(From critique: The missing layer for `src/aiv/guard/` canonical JSON validation.)*

The `GuardRunner` (`runner.py`) validates an `aiv-canonical-json` block embedded in packets. This layer ensures the canonical JSON validator (`canonical.py`) correctly enforces structural and semantic rules.

#### L5-01: `test_canonical_required_fields_enforced`

- Build a canonical JSON packet missing `identification.head_sha`.
- Call `validate_canonical(packet, ctx, result, changed_paths)`.
- **Assert:** `result` contains CT-001 BLOCK finding.
- **WHY:** `canonical.py:56-93` lists 16 required fields. Every missing field must produce a BLOCK.

#### L5-02: `test_canonical_risk_tier_mismatch_detected` *(from critique: Stale Packet Problem)*

- Build a canonical JSON packet where `classification.risk_tier` is `"R1"`.
- Build a markdown packet whose `## Classification` YAML says `risk_tier: R2`.
- Run both through `GuardRunner` (or the appropriate validation path).
- **Assert:** The system detects the discrepancy.
- **WHY:** A developer might update the markdown and forget the JSON block (or vice versa). The `GuardRunner._validate_markdown` (line 213) and `validate_canonical` (line 161) run independently — we need to verify they don't silently disagree.
- **NOTE:** If the current code does NOT detect this mismatch, this test documents the gap as a failing test, to be fixed.

#### L5-03: `test_canonical_immutability_enforced`

- Build a canonical JSON packet with an evidence artifact reference containing `/blob/main/` (mutable).
- Call `validate_canonical(...)`.
- **Assert:** CT-004 BLOCK finding.
- **WHY:** `canonical.py:244-256` enforces immutability on all artifact references. This is the JSON-layer equivalent of L3-01.

#### L5-04: `test_canonical_scope_inventory_mismatch`

- Build a canonical JSON packet with scope inventory listing files `["src/a.py", "src/b.py"]`.
- Provide `changed_paths = ["src/a.py", "src/c.py"]` (b.py missing from diff, c.py extra).
- **Assert:** B-003 BLOCK finding for scope inventory mismatch.
- **WHY:** `canonical.py:396-420` validates scope against PR diff. A stale scope inventory means the packet doesn't describe what actually changed.

#### L5-05: `test_canonical_sod_enforced_for_r2_plus`

- Build R2 canonical JSON packet where `attestations[0].verifier_id == identification.created_by`.
- **Assert:** CLS-003 BLOCK (SoD violation).
- **WHY:** `canonical.py:319-323` — Separation of Duties is a spec requirement for R2+.

#### L5-06: `test_canonical_evidence_class_requirements_per_tier`

- Build an R3 canonical JSON packet missing Class D evidence_item.
- **Assert:** CT-002 BLOCK.
- Build an R0 canonical JSON packet with only Class A and B evidence_items.
- **Assert:** No CT-002 BLOCK.
- **WHY:** `canonical.py:232-237` enforces per-tier requirements via `REQUIRED_CLASSES`.

#### L5-07: `test_canonical_class_b_line_anchors_for_r2_plus`

- Build an R2 canonical JSON packet with a Class B artifact reference that is a SHA-pinned GitHub blob URL but **without** a `#L<N>` line anchor.
- **Assert:** B-002 BLOCK.
- **WHY:** `canonical.py:258-269` — R2+ requires line-level precision in code references.

#### L5-08: `test_canonical_conditional_decision_validation`

- Build an attestation with `decision: "CONDITIONAL"` and a WARN finding, but missing `conditions` array.
- **Assert:** CT-009 BLOCK.
- Add proper `conditions` with `remediation_plan`, `responsible_party`, `remediation_deadline`.
- **Assert:** No CT-009.
- **WHY:** `canonical.py:348-393` — CONDITIONAL decisions require structured remediation plans.

---

### Layer 6: Zero-Touch Compliance — "Does the friction detector work?"

**Class:** `TestZeroTouchCompliance`

*(From critique: Code blocks vs raw commands, friction scoring.)*

#### L6-01: `test_code_block_commands_not_flagged`

- Build a packet where the reproduction/methodology section contains bash commands **inside fenced code blocks** (` ```bash ... ``` `), with explicit "context only" framing.
- **Assert:** Friction score == 0.
- **Assert:** No E008 BLOCK findings.
- **WHY:** `zero_touch.py:51,96` strips code blocks before checking prohibited patterns. Methodology sections include commands as informational context. A false-positive here blocks legitimate packets.

#### L6-02: `test_raw_commands_outside_code_blocks_flagged`

- Build a packet where the reproduction instructions contain `git clone repo && npm install && npm test` **outside** any code block.
- **Assert:** E008 BLOCK present.
- **Assert:** `friction_score.is_zero_touch_compliant == False`
- **WHY:** Raw execution commands outside code blocks violate Zero-Touch. Confirms the stripping logic correctly distinguishes context from instructions.

#### L6-03: `test_zero_touch_phrase_overrides`

- Build a packet whose reproduction says: `"**Zero-Touch Mandate:** Verifier inspects artifacts only."`
- **Assert:** Friction score == 0, no E008.
- **WHY:** `zero_touch.py:82-91` has early-exit for compliance phrases. This is the standard methodology text generated by `aiv generate`.

#### L6-04: `test_high_friction_aggregate_warning`

- Build a packet with multiple claims, each having step-heavy reproduction (> 20 total friction).
- **Assert:** E008 WARN at packet level with "Total packet friction score" message.
- **WHY:** `zero_touch.py:159-165` — aggregate friction warns when total exceeds threshold.

---

## 4. Fixture Design

### 4.1 Shared Fixtures (add to `conftest.py`)

```python
@pytest.fixture
def tmp_git_repo(tmp_path):
    """Initialize a temporary git repo with a staged file for generate tests."""
    import subprocess
    subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=tmp_path, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, capture_output=True)
    test_file = tmp_path / "src" / "feature.py"
    test_file.parent.mkdir(parents=True)
    test_file.write_text("def hello(): pass\n")
    subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True)
    return tmp_path
```

```python
@pytest.fixture
def guard_context():
    """Minimal GuardContext for canonical validation tests."""
    from aiv.guard.models import GuardContext
    return GuardContext(
        pr_number=42,
        head_sha="a" * 40,
        base_sha="b" * 40,
        owner="test-org",
        repo="test-repo",
        pr_body="",
    )
```

```python
@pytest.fixture
def minimal_canonical_packet(guard_context):
    """Factory fixture for building canonical JSON packets."""
    def _make(
        risk_tier="R1",
        sod_mode="S0",
        evidence_classes=("A", "B", "E"),
        extra_overrides=None,
    ):
        ctx = guard_context
        packet = {
            "aiv_version": "1.0.0",
            "packet_schema_version": "1.0.0",
            "identification": {
                "head_sha": ctx.head_sha,
                "pr_id": ctx.pr_number,
                "pr_url": f"https://github.com/{ctx.full_repo}/pull/{ctx.pr_number}",
                "base_sha": ctx.base_sha,
                "created_at": "2026-02-06T00:00:00Z",
                "created_by": "implementer",
            },
            "classification": {
                "risk_tier": risk_tier,
                "sod_mode": sod_mode,
                "blast_radius": "component",
                "classification_rationale": "Test packet",
                "classified_by": "cascade",
                "classified_at": "2026-02-06T00:00:00Z",
            },
            "claims": [
                {"id": "C-001", "description": "Test claim", "evidence_refs": ["E-001"]},
            ],
            "evidence_items": [
                {
                    "id": "E-001",
                    "class": cls,
                    "claim_refs": ["C-001"],
                    "artifacts": [{"type": "scope_inventory" if cls == "B" else "ci_run", "reference": "inline-json:[\"src/a.py\"]" if cls == "B" else f"https://github.com/test-org/test-repo/actions/runs/12345"}],
                    **({"validation_method": "pytest --collect-only | json"} if cls == "C" else {}),
                }
                for cls in evidence_classes
            ],
            "attestations": [{
                "id": "ATT-001",
                "verifier_id": "verifier",
                "verifier_identity_type": "github_username",
                "signature_method": "unsigned",
                "timestamp": "2026-02-06T00:00:00Z",
                "evidence_classes_validated": list(evidence_classes),
                "validation_rules_checked": ["CT-001"],
                "findings": [],
                "decision": "COMPLIANT",
            }],
            "known_limitations": ["Test only"],
        }
        if extra_overrides:
            _deep_merge(packet, extra_overrides)
        return packet
    return _make
```

### 4.2 Diff Fixtures (add to `conftest.py`)

```python
@pytest.fixture
def diff_multi_hunk_multi_file():
    """Diff with 3 anti-cheat violations across 2 files and 3 hunks."""
    return """\
diff --git a/tests/test_auth.py b/tests/test_auth.py
index abc123..def456 100644
--- a/tests/test_auth.py
+++ b/tests/test_auth.py
@@ -10,7 +10,6 @@ class TestAuth:
     def test_login(self):
         user = login("test@example.com", "pw")
-        assert user.is_authenticated
         assert user.email == "test@example.com"
@@ -50,6 +49,7 @@ class TestAuth:
     def test_refresh_token(self):
+        pytest.skip("Flaky")
         token = refresh("old-token")
         assert token is not None
diff --git a/tests/test_payment.py b/tests/test_payment.py
index aaa111..bbb222 100644
--- a/tests/test_payment.py
+++ b/tests/test_payment.py
@@ -25,7 +25,6 @@ class TestPayment:
     def test_charge(self):
         result = charge(100)
-        assert result.success
         assert result.amount == 100
"""


@pytest.fixture
def diff_deleted_test_file():
    """Diff that deletes an entire test file."""
    return """\
diff --git a/tests/test_old_feature.py b/tests/test_old_feature.py
deleted file mode 100644
index abc123..0000000
--- a/tests/test_old_feature.py
+++ /dev/null
@@ -1,20 +0,0 @@
-import pytest
-from app.old_feature import do_thing
-
-def test_do_thing():
-    assert do_thing() == 42
"""
```

### 4.3 Packet Builder Helpers (in test file)

```python
def _build_packet(
    claims_text: str = "1. Implemented feature X.",
    evidence_sections: str = "",
    classification_yaml: str | None = None,
    methodology: str = "**Zero-Touch Mandate:** Verifier inspects artifacts only.",
) -> str:
    """Build a complete packet from parts."""
    cls_block = ""
    if classification_yaml:
        cls_block = f"\n## Classification (required)\n\n```yaml\n{classification_yaml}\n```\n"

    return f"""\
# AIV Verification Packet (v2.1)

**Commit:** `abc1234`
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)
{cls_block}
## Claim(s)

{claims_text}

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [Spec](https://github.com/owner/repo/blob/abc123def456789012345678901234567890/docs/spec.md)
- **Requirements Verified:**
  1. Requirement met

### Class B (Referential Evidence)

**Scope Inventory (required)**

- Modified:
  - `src/feature.py`

### Class A (Execution Evidence)

- [CI Run](https://github.com/owner/repo/actions/runs/12345) — all tests pass

{evidence_sections}

---

## Verification Methodology

{methodology}

---

## Summary

Change summary.
"""
```

---

## 5. CI Considerations

### 5.1 Git Availability

Tests in Layer 4 (Round-Trip) that call `aiv generate` depend on `git` being available. The `tmp_git_repo` fixture initializes a fresh repo so tests work in:
- Local development (has `.git`)
- CI containers (may not have project `.git`, but `git` binary is available)
- Shallow clones (no full history)

If `git` is not available, L4-04 should `pytest.skip("git not available")`.

### 5.2 Subprocess Timeout

All subprocess calls should use `timeout=30` to prevent CI hangs.

### 5.3 Test Markers

```python
# In test_e2e_compliance.py or pyproject.toml
pytestmark = pytest.mark.integration
```

This allows running only E2E tests: `pytest -m integration` or excluding them: `pytest -m "not integration"`.

---

## 6. Traceability Matrix

Maps each test to the user story claim, the code path exercised, and the rule ID asserted.

| Test ID | User Story Claim | Code Path | Rule ID | Severity |
|---------|-----------------|-----------|---------|----------|
| L1-01 | Evidence Exists | `pipeline.validate()` | (all) | BLOCK |
| L1-02 | Evidence Exists | `parser._parse_classification()` | - | - |
| L1-03 | Evidence Exists | `cli.main.check()` via subprocess | - | - |
| L1-04 | Evidence Exists | `cli.main.check()` via subprocess | E001 | BLOCK |
| L2-01 | Evidence Exists | `parser._collect_evidence_classes()` | - | - |
| L2-02 | Evidence Exists | `pipeline._check_tier_requirements()` | E019 | BLOCK |
| L2-03 | Evidence Exists | `pipeline._check_tier_requirements()` | E019 | - |
| L2-04 | Evidence Exists | `pipeline._check_tier_requirements()` | - | - |
| L2-05 | Evidence Exists | `pipeline._check_tier_requirements()` | E019 | BLOCK |
| L2-06 | Evidence Exists | `evidence._is_bug_fix()` | E010 | BLOCK |
| L2-07 | Evidence Exists | `evidence._is_bug_fix()` | E010 | - |
| L3-01 | Immutability | `links.validate()` | E004 | BLOCK |
| L3-02 | Immutability | `links.validate()` | E004 | - |
| L3-03 | Anti-Cheat | `anti_cheat.scan_diff()` | E011 | BLOCK |
| L3-04 | Anti-Cheat | `anti_cheat.scan_diff()` | E011 | BLOCK |
| L3-05 | Anti-Cheat | `anti_cheat.scan_diff()` | E011 | BLOCK |
| L3-06 | Anti-Cheat | `anti_cheat.scan_diff()` | - | - |
| L3-07 | Anti-Cheat | `anti_cheat.check_justification()` | E011 | - |
| L3-08 | Strict Mode | `pipeline.validate()` | E014 | WARN→BLOCK |
| L3-09 | Anti-Cheat | `anti_cheat.scan_diff()` | E011 | BLOCK |
| L4-01 | Developer UX | `cli.generate()` + `cli.check()` | - | - |
| L4-02 | Developer UX | `cli._build_evidence_sections()` | - | - |
| L4-03 | Developer UX | `cli._build_evidence_sections()` | - | - |
| L4-04 | Developer UX | `cli._detect_git_scope()` | - | - |
| L5-01 | Audit Trail | `canonical.validate_canonical()` | CT-001 | BLOCK |
| L5-02 | Audit Trail | `runner.GuardRunner.run()` | - | - |
| L5-03 | Immutability | `canonical.validate_canonical()` | CT-004 | BLOCK |
| L5-04 | Audit Trail | `canonical._validate_scope_inventory()` | B-003 | BLOCK |
| L5-05 | SoD | `canonical._validate_attestation()` | CLS-003 | BLOCK |
| L5-06 | Evidence Exists | `canonical.validate_canonical()` | CT-002 | BLOCK |
| L5-07 | Immutability | `canonical.validate_canonical()` | B-002 | BLOCK |
| L5-08 | Audit Trail | `canonical._validate_conditional_decision()` | CT-009 | BLOCK |
| L6-01 | Zero-Touch | `zero_touch.validate_claim()` | E008 | - |
| L6-02 | Zero-Touch | `zero_touch.validate_claim()` | E008 | BLOCK |
| L6-03 | Zero-Touch | `zero_touch.validate_claim()` | E008 | - |
| L6-04 | Zero-Touch | `zero_touch.validate_packet()` | E008 | WARN |

---

## 7. Execution Order (Red-Green-Refactor)

> **Rationale:** We implement the test suite *before* fixing the packets so we can
> observe the tests **fail** (Red), proving they catch real protocol drift. Only then
> do we fix the packets and watch the tests **pass** (Green). This prevents "Theater
> Tests" that pass regardless of evidence quality.

### Phase 1: Substance Patch
1. Modify `src/aiv/lib/parser.py` — add `_is_substantive()`, integrate into `_collect_evidence_classes`.
2. Unit test the new method in `tests/unit/test_parser.py`.
3. Run existing test suite to verify no regressions.

### Phase 2: Test Suite Implementation (expect RED)
1. Add shared fixtures to `tests/conftest.py`.
2. Implement `tests/integration/test_e2e_compliance.py` — all 6 layers, 39 test cases.
3. Run suite: `python -m pytest tests/integration/test_e2e_compliance.py -v --tb=short`.
4. **Verify L1-01 FAILS** on `VERIFICATION_PACKET_AIV_AUDIT_FIXES.md` (missing Class F).
5. This failure proves the test suite catches real non-compliance.

### Phase 3: Packet Fix (turn GREEN)
1. Add `### Class F (Provenance)` to `VERIFICATION_PACKET_AIV_AUDIT_FIXES.md`.
2. Re-run the suite — **all tests must now pass**.

### Phase 4: Atomic Commits
Per the pre-commit hook policy (1 functional file + 1 verification packet per commit):
1. Commit parser fix + packet update.
2. Commit conftest additions + packet update.
3. Commit test file + packet update.
4. Commit AUDIT_REPORT update if needed.

---

## 8. Expected Test Count

| Layer | Test Cases |
|-------|-----------|
| L1: Self-Compliance | 4 |
| L2: Evidence Substance | 7 |
| L3: Security Properties | 9 |
| L4: Round-Trip | 4 (+3 parametrized = 7 total) |
| L5: Canonical Compliance | 8 |
| L6: Zero-Touch | 4 |
| **Total** | **39** |

Combined with existing 188 tests: **227 total**.

---

## 9. Success Criteria

The test suite is considered complete when:

1. **All 39 E2E tests pass** with zero failures.
2. **All existing 188 tests still pass** (no regressions).
3. **`aiv check` passes on every packet** in `.github/aiv-packets/` (L1-01).
4. **The substance patch** prevents TODO-only sections from counting as evidence (L2-01, L2-02).
5. **The CLI works as a subprocess** — not just via Python API (L1-03, L4-01).
6. **Canonical JSON validation** is tested independently from markdown validation (L5-*).

---

## Appendix A: Known Gaps Not Addressed

These are acknowledged limitations that are out of scope for this test suite but should be tracked:

1. **Network validation:** No tests verify that evidence links are actually accessible (spec acknowledges this as structural-only).
2. **Class A artifact inspection:** `GuardRunner._inspect_class_a_run()` calls the GitHub API — full E2E testing requires API mocking or a live GitHub environment.
3. **SVP Protocol E2E:** The SVP cognitive verification layer (`src/aiv/svp/`) is not tested end-to-end in this suite. A separate SVP E2E spec is recommended.
4. **Pre-commit hook:** The shell-based pre-commit hook (`.husky/pre-commit`) is not tested programmatically. It is validated by the commit process itself.
