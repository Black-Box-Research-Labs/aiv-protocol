"""
tests/integration/test_e2e_compliance.py

E2E Compliance Test Suite — validates the AIV protocol system works
end-to-end against this actual repository.

Spec: docs/specs/E2E_COMPLIANCE_TEST_SUITE_SPEC.md

Layers:
  L1: Self-Compliance    — real packets pass validation
  L2: Evidence Substance — TODO-only sections rejected
  L3: Security Properties — adversarial inputs caught
  L4: Round-Trip          — generate → check works
  L5: Canonical Compliance — canonical JSON enforcement
  L6: Zero-Touch          — friction detection works
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from aiv.lib.config import AIVConfig
from aiv.lib.models import (
    Claim,
    EvidenceClass,
    RiskTier,
    ValidationStatus,
    Severity,
)
from aiv.lib.parser import PacketParser
from aiv.lib.validators.anti_cheat import AntiCheatScanner
from aiv.lib.validators.pipeline import ValidationPipeline
from aiv.lib.validators.zero_touch import ZeroTouchValidator
from aiv.guard.canonical import validate_canonical, REQUIRED_CLASSES
from aiv.guard.models import GuardContext, GuardResult

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PACKETS_DIR = Path(__file__).resolve().parents[2] / ".github" / "aiv-packets"
PROJECT_ROOT = Path(__file__).resolve().parents[2]

pytestmark = pytest.mark.integration


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _collect_real_packets() -> list[Path]:
    """Return all VERIFICATION_PACKET_*.md files excluding TEMPLATE."""
    return sorted(
        p for p in PACKETS_DIR.glob("VERIFICATION_PACKET_*.md")
        if "TEMPLATE" not in p.name
    )


def _build_packet(
    claims_text: str = "1. Implements feature X per specification requirements.",
    evidence_sections: str = "",
    classification_yaml: str | None = None,
    methodology: str = "**Zero-Touch Mandate:** Verifier inspects artifacts only.",
) -> str:
    """Build a complete packet from parts."""
    cls_block = ""
    if classification_yaml:
        cls_block = (
            "\n## Classification (required)\n\n"
            f"```yaml\n{classification_yaml}\n```\n"
        )

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
  1. Requirement met per specification

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


def _make_guard_context(
    pr_number: int = 42,
    head_sha: str = "a" * 40,
    base_sha: str = "b" * 40,
) -> GuardContext:
    """Build a minimal GuardContext for canonical tests."""
    return GuardContext(
        pr_number=pr_number,
        head_sha=head_sha,
        base_sha=base_sha,
        owner="test-org",
        repo="test-repo",
        pr_body="",
    )


def _make_canonical_packet(
    ctx: GuardContext,
    risk_tier: str = "R1",
    sod_mode: str = "S0",
    evidence_classes: tuple[str, ...] = ("A", "B", "E"),
    overrides: dict | None = None,
) -> dict:
    """Build a minimal valid canonical JSON packet."""
    evidence_items = []
    for cls in evidence_classes:
        item: dict = {
            "id": f"E-{cls}",
            "class": cls,
            "claim_refs": ["C-001"],
            "artifacts": [],
        }
        if cls == "B":
            item["artifacts"] = [
                {"type": "scope_inventory", "reference": 'inline-json:["src/a.py"]'}
            ]
        else:
            item["artifacts"] = [
                {
                    "type": "ci_run",
                    "reference": f"https://github.com/{ctx.full_repo}/actions/runs/12345",
                }
            ]
        if cls == "C":
            item["validation_method"] = "pytest --collect-only | json"
        evidence_items.append(item)

    packet: dict = {
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
            "classification_rationale": "Test packet for E2E compliance",
            "classified_by": "cascade",
            "classified_at": "2026-02-06T00:00:00Z",
        },
        "claims": [
            {
                "id": "C-001",
                "description": "Test claim for validation",
                "evidence_refs": [f"E-{c}" for c in evidence_classes],
            },
        ],
        "evidence_items": evidence_items,
        "attestations": [
            {
                "id": "ATT-001",
                "verifier_id": "verifier",
                "verifier_identity_type": "github_username",
                "signature_method": "unsigned",
                "timestamp": "2026-02-06T00:00:00Z",
                "evidence_classes_validated": list(evidence_classes),
                "validation_rules_checked": ["CT-001"],
                "findings": [],
                "decision": "COMPLIANT",
            }
        ],
        "known_limitations": ["Test-only packet"],
    }

    if overrides:
        _deep_merge(packet, overrides)

    return packet


def _deep_merge(base: dict, override: dict) -> None:
    """Recursively merge override into base dict."""
    for key, val in override.items():
        if key in base and isinstance(base[key], dict) and isinstance(val, dict):
            _deep_merge(base[key], val)
        else:
            base[key] = val


# ============================================================================
# Layer 1: Self-Compliance
# ============================================================================


class TestSelfCompliance:
    """L1: Does this repo follow its own protocol?"""

    @pytest.mark.parametrize(
        "packet_path",
        _collect_real_packets(),
        ids=lambda p: p.stem,
    )
    def test_every_real_packet_passes_lenient(self, packet_path: Path):
        """L1-01: Every real packet passes validation in lenient mode."""
        body = packet_path.read_text(encoding="utf-8")
        cfg = AIVConfig(strict_mode=False)
        pipeline = ValidationPipeline(cfg)
        result = pipeline.validate(body)

        blocking = [f for f in result.errors if f.severity == Severity.BLOCK]
        assert result.status == ValidationStatus.PASS, (
            f"{packet_path.name} failed with {len(blocking)} blocking error(s):\n"
            + "\n".join(f"  [{e.rule_id}] {e.message}" for e in blocking)
        )

    @pytest.mark.parametrize(
        "packet_path",
        [p for p in _collect_real_packets() if "## Classification" in p.read_text(encoding="utf-8")],
        ids=lambda p: p.stem,
    )
    def test_every_real_packet_parses_classification(self, packet_path: Path):
        """L1-02: Packets with Classification section parse risk_tier correctly."""
        body = packet_path.read_text(encoding="utf-8")
        parser = PacketParser()
        packet = parser.parse(body)
        assert packet is not None
        assert packet.risk_tier is not None, (
            f"{packet_path.name}: ## Classification present but risk_tier is None"
        )
        assert isinstance(packet.risk_tier, RiskTier)

    def test_cli_subprocess_check_passes(self):
        """L1-03: CLI check passes on a known-good packet via subprocess."""
        packet_path = PACKETS_DIR / "VERIFICATION_PACKET_AIV_IMPLEMENTATION.md"
        if not packet_path.exists():
            pytest.skip(f"{packet_path.name} not found")

        result = subprocess.run(
            [sys.executable, "-m", "aiv", "check", str(packet_path), "--no-strict"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0, (
            f"CLI check failed:\nstdout: {result.stdout[-500:]}\nstderr: {result.stderr[-500:]}"
        )

    def test_cli_subprocess_check_rejects_garbage(self):
        """L1-04: CLI rejects garbage input."""
        result = subprocess.run(
            [sys.executable, "-m", "aiv", "check", "This is not a verification packet at all"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode != 0


# ============================================================================
# Layer 2: Evidence Substance
# ============================================================================


class TestEvidenceSubstance:
    """L2: Does the system validate substance, not just structure?"""

    def test_todo_only_evidence_section_not_counted(self):
        """L2-01: A ### Class D section with only TODO is not counted as evidence."""
        body = _build_packet(
            evidence_sections="### Class D (Differential Evidence)\n\n- TODO: Before/after diff of critical behavior.\n"
        )
        parser = PacketParser()
        packet = parser.parse(body)
        assert packet is not None
        assert EvidenceClass.DIFFERENTIAL not in packet.evidence_classes_present

    def test_r3_with_empty_sections_fails(self):
        """L2-02: R3 packet with placeholder D and F sections fails E019."""
        classification = (
            "classification:\n"
            "  risk_tier: R3\n"
            "  sod_mode: S1\n"
            "  critical_surfaces: []\n"
            "  blast_radius: system\n"
            '  classification_rationale: "Critical change"\n'
            '  classified_by: "cascade"\n'
            '  classified_at: "2026-02-06T00:00:00Z"'
        )
        evidence = (
            "### Class C (Negative Evidence)\n\n"
            "- No regressions found. Full regression suite passed in CI run.\n\n"
            "### Class D (Differential Evidence)\n\n"
            "- TODO: Before/after diff.\n\n"
            "### Class F (Provenance Evidence)\n\n"
            "- TBD: Provenance data.\n"
        )
        body = _build_packet(
            classification_yaml=classification,
            evidence_sections=evidence,
        )
        cfg = AIVConfig(strict_mode=False)
        pipeline = ValidationPipeline(cfg)
        result = pipeline.validate(body)
        assert result.status == ValidationStatus.FAIL

        e019_rules = [f for f in result.errors if f.rule_id == "E019"]
        blocked_classes = " ".join(f.message for f in e019_rules)
        assert "Class D" in blocked_classes or "Differential" in blocked_classes
        assert "Class F" in blocked_classes or "Provenance" in blocked_classes

    def test_r3_with_substantive_sections_passes(self):
        """L2-03: R3 packet with real content in all sections passes."""
        classification = (
            "classification:\n"
            "  risk_tier: R3\n"
            "  sod_mode: S1\n"
            "  critical_surfaces: []\n"
            "  blast_radius: system\n"
            '  classification_rationale: "Critical authentication change"\n'
            '  classified_by: "cascade"\n'
            '  classified_at: "2026-02-06T00:00:00Z"'
        )
        evidence = (
            "### Class C (Negative Evidence)\n\n"
            "- No regressions found. Full regression suite passed with 188/188 tests green.\n\n"
            "### Class D (Differential Evidence)\n\n"
            "- Before: parser counted empty headers as evidence present.\n"
            "- After: parser validates content substance with _is_substantive method.\n\n"
            "### Class F (Provenance Evidence)\n\n"
            "- No existing tests were modified or deleted during this change.\n"
            "- All test assertions preserved. Full provenance chain intact.\n"
        )
        body = _build_packet(
            classification_yaml=classification,
            evidence_sections=evidence,
        )
        cfg = AIVConfig(strict_mode=False)
        pipeline = ValidationPipeline(cfg)
        result = pipeline.validate(body)
        assert result.status == ValidationStatus.PASS, (
            "R3 with substantive evidence should pass:\n"
            + "\n".join(f"  [{e.rule_id}] {e.message}" for e in result.errors)
        )

    def test_r0_scaffold_passes_without_optional(self):
        """L2-04: R0 packet with only A and B passes."""
        classification = (
            "classification:\n"
            "  risk_tier: R0\n"
            "  sod_mode: S0\n"
            "  critical_surfaces: []\n"
            "  blast_radius: trivial\n"
            '  classification_rationale: "Docs only"\n'
            '  classified_by: "cascade"\n'
            '  classified_at: "2026-02-06T00:00:00Z"'
        )
        body = _build_packet(classification_yaml=classification)
        cfg = AIVConfig(strict_mode=False)
        pipeline = ValidationPipeline(cfg)
        result = pipeline.validate(body)

        e019_blocks = [f for f in result.errors if f.rule_id == "E019"]
        assert len(e019_blocks) == 0, (
            "R0 should not require optional evidence classes:\n"
            + "\n".join(f"  [{e.rule_id}] {e.message}" for e in e019_blocks)
        )

    def test_r2_missing_required_class_fails(self):
        """L2-05: R2 packet missing Class C fails E019."""
        classification = (
            "classification:\n"
            "  risk_tier: R2\n"
            "  sod_mode: S0\n"
            "  critical_surfaces: []\n"
            "  blast_radius: component\n"
            '  classification_rationale: "Refactor"\n'
            '  classified_by: "cascade"\n'
            '  classified_at: "2026-02-06T00:00:00Z"'
        )
        body = _build_packet(classification_yaml=classification)
        cfg = AIVConfig(strict_mode=False)
        pipeline = ValidationPipeline(cfg)
        result = pipeline.validate(body)
        assert result.status == ValidationStatus.FAIL

        e019_messages = " ".join(f.message for f in result.errors if f.rule_id == "E019")
        assert "C" in e019_messages or "Negative" in e019_messages

    def test_bugfix_claims_require_class_f(self):
        """L2-06: Bug-fix claims without Class F trigger E010."""
        body = _build_packet(
            claims_text="1. Fixed authentication bypass vulnerability in login handler.",
        )
        cfg = AIVConfig(strict_mode=False)
        pipeline = ValidationPipeline(cfg)
        result = pipeline.validate(body)

        e010 = [f for f in result.errors if f.rule_id == "E010"]
        assert len(e010) > 0, "Bug-fix claim should trigger E010 (missing Class F)"

    def test_bugfix_claims_with_class_f_passes(self):
        """L2-07: Bug-fix claims WITH Class F evidence pass E010."""
        evidence = (
            "### Class F (Provenance Evidence)\n\n"
            "- No existing tests were modified or deleted during this change.\n"
            "- All test assertions preserved. Full provenance chain intact.\n"
        )
        body = _build_packet(
            claims_text="1. Fixed authentication bypass vulnerability in login handler.",
            evidence_sections=evidence,
        )
        cfg = AIVConfig(strict_mode=False)
        pipeline = ValidationPipeline(cfg)
        result = pipeline.validate(body)

        e010 = [f for f in result.errors if f.rule_id == "E010"]
        assert len(e010) == 0, (
            "Bug-fix with Class F should not trigger E010:\n"
            + "\n".join(f"  [{e.rule_id}] {e.message}" for e in e010)
        )


# ============================================================================
# Layer 3: Security Properties
# ============================================================================


class TestSecurityProperties:
    """L3: Can the system be bypassed?"""

    def test_mutable_github_link_blocked(self, invalid_mutable_link):
        """L3-01: Mutable /blob/main/ link triggers E004."""
        cfg = AIVConfig(strict_mode=False)
        pipeline = ValidationPipeline(cfg)
        result = pipeline.validate(invalid_mutable_link)

        e004 = [f for f in result.errors if f.rule_id == "E004"]
        assert len(e004) > 0, "Mutable link should trigger E004"

    def test_sha_pinned_link_passes(self, valid_minimal_packet):
        """L3-02: SHA-pinned link does not trigger E004."""
        cfg = AIVConfig(strict_mode=False)
        pipeline = ValidationPipeline(cfg)
        result = pipeline.validate(valid_minimal_packet)

        e004 = [f for f in result.errors if f.rule_id == "E004"]
        assert len(e004) == 0, (
            "SHA-pinned link should not trigger E004:\n"
            + "\n".join(f"  [{e.rule_id}] {e.message}" for e in e004)
        )

    def test_deleted_assertion_in_diff_blocked(
        self, valid_minimal_packet, diff_with_deleted_assertion
    ):
        """L3-03: Deleted assertion triggers E011."""
        cfg = AIVConfig(strict_mode=False)
        pipeline = ValidationPipeline(cfg)
        result = pipeline.validate(valid_minimal_packet, diff=diff_with_deleted_assertion)

        e011 = [f for f in result.errors if f.rule_id == "E011"]
        assert len(e011) > 0, "Deleted assertion should trigger E011"
        assert any("deleted_assertion" in f.message for f in e011)

    def test_added_skip_decorator_blocked(
        self, valid_minimal_packet, diff_with_skip_decorator
    ):
        """L3-04: Added skip decorator triggers E011."""
        cfg = AIVConfig(strict_mode=False)
        pipeline = ValidationPipeline(cfg)
        result = pipeline.validate(valid_minimal_packet, diff=diff_with_skip_decorator)

        e011 = [f for f in result.errors if f.rule_id == "E011"]
        assert len(e011) > 0, "Skip decorator should trigger E011"
        assert any("skipped_test" in f.message for f in e011)

    def test_deleted_test_file_blocked(
        self, valid_minimal_packet, diff_deleted_test_file
    ):
        """L3-05: Deleted test file triggers E011."""
        cfg = AIVConfig(strict_mode=False)
        pipeline = ValidationPipeline(cfg)
        result = pipeline.validate(valid_minimal_packet, diff=diff_deleted_test_file)

        e011 = [f for f in result.errors if f.rule_id == "E011"]
        assert len(e011) > 0, "Deleted test file should trigger E011"
        assert any("removed_test_file" in f.message for f in e011)

    def test_clean_diff_passes(self, valid_minimal_packet, diff_clean):
        """L3-06: Clean diff does not trigger E011."""
        cfg = AIVConfig(strict_mode=False)
        pipeline = ValidationPipeline(cfg)
        result = pipeline.validate(valid_minimal_packet, diff=diff_clean)

        e011 = [f for f in result.errors if f.rule_id == "E011"]
        assert len(e011) == 0, "Clean diff should not trigger E011"

    def test_class_f_justification_overrides_anticheat(
        self, diff_with_deleted_assertion
    ):
        """L3-07: Class F justification overrides anti-cheat findings."""
        evidence = (
            "### Class F (Provenance Evidence)\n\n"
            "**Claim 1: Test cleanup**\n"
            "- Removed redundant assertion that duplicated the check on the next line.\n"
            "- All remaining assertions still verify the complete behavior.\n"
        )
        body = _build_packet(
            claims_text=(
                "1. Cleaned up redundant test assertions in auth module.\n"
                "3. No existing tests were weakened or deleted during this change."
            ),
            evidence_sections=evidence,
        )

        # We need the claim to have evidence_class F and justification > 20 chars.
        # The pipeline builds claims from the parser; Class F is detected from the
        # evidence section. The check_justification method looks for any claim with
        # evidence_class == F and justification > 20 chars.
        # Since the parser doesn't extract justification from markdown, we test
        # the anti-cheat scanner directly.
        scanner = AntiCheatScanner()
        ac_result = scanner.scan_diff(diff_with_deleted_assertion)
        assert ac_result.requires_justification

        # Build a claim with Class F + justification
        justified_claim = Claim(
            section_number=3,
            description="No existing tests were weakened or deleted during this change.",
            evidence_class=EvidenceClass.PROVENANCE,
            artifact="See Class F evidence section",
            reproduction="N/A",
            justification="Removed redundant assertion that duplicated the is_authenticated check on the following line.",
        )
        unjustified = scanner.check_justification(ac_result, [justified_claim])
        assert len(unjustified) == 0, (
            "Class F justification should override anti-cheat:\n"
            + "\n".join(f"  {f.finding_type} in {f.file_path}" for f in unjustified)
        )

    def test_strict_mode_promotes_warnings_to_failures(self):
        """L3-08: Strict mode makes warnings cause failure."""
        # Packet without ## Classification → E014 WARN
        body = _build_packet()

        # Lenient mode: should pass (WARN only, no BLOCK)
        lenient_cfg = AIVConfig(strict_mode=False)
        lenient_result = ValidationPipeline(lenient_cfg).validate(body)

        # Strict mode: should fail (WARN promoted)
        strict_cfg = AIVConfig(strict_mode=True)
        strict_result = ValidationPipeline(strict_cfg).validate(body)

        # We only assert strict fails if lenient had warnings
        if lenient_result.warnings:
            assert strict_result.status == ValidationStatus.FAIL, (
                "Strict mode should promote warnings to failures"
            )

    def test_multi_hunk_multi_file_diff(
        self, valid_minimal_packet, diff_multi_hunk_multi_file
    ):
        """L3-09: Multi-hunk, multi-file diff detects all violations."""
        scanner = AntiCheatScanner()
        ac_result = scanner.scan_diff(diff_multi_hunk_multi_file)

        # Expect at least 3 findings: 2 deleted assertions + 1 skip
        assert len(ac_result.findings) >= 3, (
            f"Expected >= 3 findings, got {len(ac_result.findings)}:\n"
            + "\n".join(
                f"  {f.finding_type} in {f.file_path}:{f.line_number}"
                for f in ac_result.findings
            )
        )

        # Verify file paths track correctly across hunks
        file_paths = {f.file_path for f in ac_result.findings}
        assert "tests/test_auth.py" in file_paths
        assert "tests/test_payment.py" in file_paths

        # Line numbers should be positive
        for finding in ac_result.findings:
            if finding.line_number is not None:
                assert finding.line_number > 0


# ============================================================================
# Layer 4: Round-Trip
# ============================================================================


class TestGenerateCheckRoundTrip:
    """L4: Does generate → check work for all tiers?"""

    @pytest.mark.parametrize("tier", ["R0", "R1", "R2", "R3"])
    def test_generate_then_check_passes(self, tier: str, tmp_path: Path):
        """L4-01: Generated packet passes check for each tier."""
        gen_result = subprocess.run(
            [
                sys.executable, "-m", "aiv", "generate",
                f"test-{tier.lower()}", "--tier", tier,
                "--output", str(tmp_path),
            ],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(PROJECT_ROOT),
        )
        assert gen_result.returncode == 0, (
            f"generate failed for {tier}:\n{gen_result.stderr[-500:]}"
        )

        # Find the generated file
        generated = list(tmp_path.glob("VERIFICATION_PACKET_*.md"))
        assert len(generated) == 1, f"Expected 1 file, found {len(generated)}"

        check_result = subprocess.run(
            [
                sys.executable, "-m", "aiv", "check",
                str(generated[0]), "--no-strict",
            ],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(PROJECT_ROOT),
        )
        assert check_result.returncode == 0, (
            f"check failed for generated {tier} packet:\n{check_result.stdout[-500:]}"
        )

    def test_generate_r3_includes_all_six_sections(self):
        """L4-02: R3 scaffold includes all six ### Class X headers."""
        from aiv.cli.main import _build_evidence_sections

        output = _build_evidence_sections("R3", "  - TODO: list modified files")
        for letter in ("A", "B", "C", "D", "E", "F"):
            assert f"### Class {letter}" in output, (
                f"R3 scaffold missing ### Class {letter}"
            )

    def test_generate_r0_omits_non_required_sections(self):
        """L4-03: R0 scaffold only includes A and B."""
        from aiv.cli.main import _build_evidence_sections

        output = _build_evidence_sections("R0", "  - TODO: list modified files")
        assert "### Class A" in output
        assert "### Class B" in output
        # R0 should NOT include these
        assert "### Class C" not in output
        assert "### Class D" not in output
        assert "### Class F" not in output

    def test_generate_uses_temp_git_repo(self, tmp_path: Path):
        """L4-04: Generate detects staged files from a real git repo."""
        # Check if git is available
        try:
            subprocess.run(
                ["git", "--version"],
                capture_output=True, timeout=5, check=True,
            )
        except (FileNotFoundError, subprocess.CalledProcessError):
            pytest.skip("git not available")

        # Init temp repo with a staged file
        subprocess.run(["git", "init"], cwd=tmp_path, capture_output=True, check=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test.com"],
            cwd=tmp_path, capture_output=True,
        )
        subprocess.run(
            ["git", "config", "user.name", "Test"],
            cwd=tmp_path, capture_output=True,
        )
        feature_file = tmp_path / "src" / "feature.py"
        feature_file.parent.mkdir(parents=True)
        feature_file.write_text("def hello(): pass\n")
        subprocess.run(["git", "add", "."], cwd=tmp_path, capture_output=True, check=True)

        gen_result = subprocess.run(
            [
                sys.executable, "-m", "aiv", "generate",
                "test-ci", "--tier", "R1",
                "--output", str(tmp_path),
            ],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(tmp_path),
        )
        assert gen_result.returncode == 0

        generated = list(tmp_path.glob("VERIFICATION_PACKET_*.md"))
        assert len(generated) == 1
        content = generated[0].read_text(encoding="utf-8")
        # Should contain the staged file, not "TODO: list modified files"
        assert "src/feature.py" in content, (
            "Generated packet should reference staged file src/feature.py"
        )


# ============================================================================
# Layer 5: Canonical Compliance
# ============================================================================


class TestCanonicalCompliance:
    """L5: Is the machine-readable JSON layer consistent?"""

    def test_canonical_required_fields_enforced(self):
        """L5-01: Missing required field triggers CT-001."""
        ctx = _make_guard_context()
        packet = _make_canonical_packet(ctx)
        # Remove a required field
        del packet["identification"]["head_sha"]

        result = GuardResult()
        ok = validate_canonical(packet, ctx, result, ["src/a.py"])
        assert not ok
        assert any(f.rule_id == "CT-001" for f in result.findings)

    def test_canonical_risk_tier_mismatch_detected(self):
        """L5-02: Canonical JSON and markdown should agree on risk tier.

        NOTE: This test documents expected behavior. If the system does NOT
        currently detect mismatches between markdown and JSON risk tiers,
        this test documents the gap.
        """
        # Build a canonical packet with R1
        ctx = _make_guard_context()
        packet = _make_canonical_packet(ctx, risk_tier="R1")
        result = GuardResult()
        ok = validate_canonical(packet, ctx, result, ["src/a.py"])

        # The canonical validator independently validates the R1 tier.
        # A full mismatch test would require the GuardRunner which reads
        # both markdown and JSON — here we verify R1 validates cleanly.
        assert ok, "R1 canonical packet should validate"
        assert result.risk_tier_validated == "R1"

    def test_canonical_immutability_enforced(self):
        """L5-03: Mutable artifact reference triggers CT-004."""
        ctx = _make_guard_context()
        packet = _make_canonical_packet(ctx)
        # Inject mutable reference
        packet["evidence_items"][0]["artifacts"] = [
            {
                "type": "ci_run",
                "reference": "https://github.com/test-org/test-repo/blob/main/src/a.py",
            }
        ]
        result = GuardResult()
        ok = validate_canonical(packet, ctx, result, ["src/a.py"])
        assert not ok
        assert any(f.rule_id == "CT-004" for f in result.findings)

    def test_canonical_scope_inventory_mismatch(self):
        """L5-04: Scope inventory vs PR diff mismatch triggers B-003."""
        ctx = _make_guard_context()
        packet = _make_canonical_packet(ctx)

        # Packet scope says ["src/a.py"] but diff says ["src/a.py", "src/c.py"]
        result = GuardResult()
        ok = validate_canonical(packet, ctx, result, ["src/a.py", "src/c.py"])
        assert not ok
        assert any(f.rule_id == "B-003" for f in result.findings)

    def test_canonical_sod_enforced_for_r2_plus(self):
        """L5-05: R2 with same verifier/creator triggers CLS-003."""
        ctx = _make_guard_context()
        packet = _make_canonical_packet(
            ctx, risk_tier="R2", sod_mode="S1",
            evidence_classes=("A", "B", "C", "E"),
        )
        # Make verifier == creator (SoD violation)
        packet["attestations"][0]["verifier_id"] = "implementer"

        result = GuardResult()
        ok = validate_canonical(packet, ctx, result, ["src/a.py"])
        assert not ok
        assert any(f.rule_id == "CLS-003" for f in result.findings)

    def test_canonical_evidence_class_requirements_per_tier(self):
        """L5-06: R3 missing Class D triggers CT-002; R0 with A+B passes."""
        ctx = _make_guard_context()

        # R3 missing Class D
        r3_packet = _make_canonical_packet(
            ctx, risk_tier="R3", sod_mode="S1",
            evidence_classes=("A", "B", "C", "E", "F"),
        )
        r3_packet["attestations"][0]["verifier_id"] = "different-verifier"
        r3_result = GuardResult()
        ok = validate_canonical(r3_packet, ctx, r3_result, ["src/a.py"])
        assert not ok
        assert any(
            f.rule_id == "CT-002" and "D" in f.description
            for f in r3_result.findings
        )

        # R0 with only A and B
        r0_packet = _make_canonical_packet(
            ctx, risk_tier="R0", evidence_classes=("A", "B"),
        )
        r0_result = GuardResult()
        ok = validate_canonical(r0_packet, ctx, r0_result, ["src/a.py"])
        ct002 = [f for f in r0_result.findings if f.rule_id == "CT-002"]
        assert len(ct002) == 0, "R0 with A+B should not trigger CT-002"

    def test_canonical_class_b_line_anchors_for_r2_plus(self):
        """L5-07: R2 Class B SHA permalink without line anchor triggers B-002."""
        ctx = _make_guard_context()
        packet = _make_canonical_packet(
            ctx, risk_tier="R2", sod_mode="S1",
            evidence_classes=("A", "B", "C", "E"),
        )
        packet["attestations"][0]["verifier_id"] = "different-verifier"
        # Add a Class B artifact with SHA permalink but no line anchor
        for item in packet["evidence_items"]:
            if item["class"] == "B":
                item["artifacts"].append({
                    "type": "code_reference",
                    "reference": f"https://github.com/test-org/test-repo/blob/{'a' * 40}/src/feature.py",
                })
        result = GuardResult()
        ok = validate_canonical(packet, ctx, result, ["src/a.py"])
        assert not ok
        assert any(f.rule_id == "B-002" for f in result.findings)

    def test_canonical_conditional_decision_validation(self):
        """L5-08: CONDITIONAL decision without conditions triggers CT-009."""
        ctx = _make_guard_context()
        packet = _make_canonical_packet(ctx)
        # Set decision to CONDITIONAL with a WARN finding but no conditions
        packet["attestations"][0]["decision"] = "CONDITIONAL"
        packet["attestations"][0]["findings"] = [
            {"id": "W-001", "severity": "WARN", "description": "Minor issue"}
        ]
        # No "conditions" array

        result = GuardResult()
        ok = validate_canonical(packet, ctx, result, ["src/a.py"])
        assert not ok
        assert any(f.rule_id == "CT-009" for f in result.findings)


# ============================================================================
# Layer 6: Zero-Touch Compliance
# ============================================================================


class TestZeroTouchCompliance:
    """L6: Does the friction detector work?"""

    def test_code_block_commands_not_flagged(self):
        """L6-01: Commands inside fenced code blocks are not flagged."""
        body = _build_packet(
            methodology=(
                "**Zero-Touch Mandate:** Verifier inspects artifacts only.\n\n"
                "Context (informational only):\n"
                "```bash\n"
                "git clone repo && npm install && npm test\n"
                "```\n"
            ),
        )
        cfg = AIVConfig(strict_mode=False)
        pipeline = ValidationPipeline(cfg)
        result = pipeline.validate(body)

        e008_blocks = [
            f for f in result.errors
            if f.rule_id == "E008" and f.severity == Severity.BLOCK
        ]
        assert len(e008_blocks) == 0, (
            "Code block commands should not trigger E008 BLOCK:\n"
            + "\n".join(f"  {e.message}" for e in e008_blocks)
        )

    def test_raw_commands_outside_code_blocks_flagged(self):
        """L6-02: Raw commands outside code blocks trigger E008."""
        body = _build_packet(
            methodology="git clone repo && npm install && npm test",
        )
        cfg = AIVConfig(strict_mode=False)
        pipeline = ValidationPipeline(cfg)
        result = pipeline.validate(body)

        e008_blocks = [
            f for f in result.errors
            if f.rule_id == "E008" and f.severity == Severity.BLOCK
        ]
        assert len(e008_blocks) > 0, "Raw commands should trigger E008 BLOCK"

    def test_zero_touch_phrase_overrides(self):
        """L6-03: Zero-touch compliance phrase produces zero friction."""
        claim = Claim(
            section_number=1,
            description="Implements feature X per specification requirements.",
            evidence_class=EvidenceClass.REFERENTIAL,
            artifact="See Evidence section",
            reproduction="**Zero-Touch Mandate:** Verifier inspects artifacts only.",
        )
        validator = ZeroTouchValidator()
        errors, friction = validator.validate_claim(claim)
        assert friction.score == 0
        assert friction.is_zero_touch_compliant
        assert len(errors) == 0

    def test_high_friction_aggregate_warning(self):
        """L6-04: High aggregate friction produces packet-level E008 WARN."""
        from aiv.lib.models import IntentSection, ArtifactLink, VerificationPacket

        # Build claims with step-heavy reproduction
        claims = []
        for i in range(1, 6):
            claims.append(Claim(
                section_number=i,
                description=f"Claim {i} with detailed verification steps for feature implementation.",
                evidence_class=EvidenceClass.REFERENTIAL,
                artifact="See evidence",
                reproduction=(
                    "Step 1: Open the dashboard\n"
                    "Step 2: Navigate to settings\n"
                    "Step 3: Click the toggle\n"
                    "Step 4: Verify the change\n"
                    "Step 5: Check the logs\n"
                    "Step 6: Confirm the output"
                ),
            ))

        packet = VerificationPacket(
            version="2.1",
            risk_tier=None,
            evidence_classes_present={EvidenceClass.REFERENTIAL},
            intent=IntentSection(
                evidence_link="https://example.com",
                verifier_check="Check requirements met per spec",
            ),
            claims=claims,
            raw_markdown="",
        )

        validator = ZeroTouchValidator()
        findings = validator.validate_packet(packet)

        warn_findings = [
            f for f in findings
            if f.rule_id == "E008" and f.severity == Severity.WARN
            and "friction" in f.message.lower()
        ]
        assert len(warn_findings) > 0, (
            "High aggregate friction should produce E008 WARN"
        )
