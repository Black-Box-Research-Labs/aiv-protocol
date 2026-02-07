"""
tests/unit/test_guard.py

Unit tests for the AIV Guard module (§7.5 P2 refactor).
"""

from __future__ import annotations

import json
import pytest

from aiv.guard.models import (
    GuardContext,
    GuardFinding,
    GuardResult,
    GuardSeverity,
    EvidenceClassResult,
    OverallResult,
    RuleResult,
    HEX_SHA_40_OR_64,
    MUTABLE_BRANCH_PATTERN,
    GITHUB_BLOB_FULL_SHA,
    GITHUB_ACTIONS_RUN,
    LINE_ANCHOR,
)
from aiv.guard.canonical import validate_canonical, REQUIRED_CLASSES, _get_path
from aiv.guard.manifest import (
    validate_class_a_manifest,
    validate_class_c_manifest,
    validate_semantic_manifest,
    validate_durable_manifest,
)
from aiv.guard.runner import GuardRunner
from aiv.guard.github_api import GitHubAPI, ChangedFile


# ------------------------------------------------------------------ #
# Fixtures
# ------------------------------------------------------------------ #

@pytest.fixture
def ctx() -> GuardContext:
    return GuardContext(
        pr_number=42,
        head_sha="a" * 40,
        base_sha="b" * 40,
        owner="TestOwner",
        repo="test-repo",
        pr_body="",
    )


@pytest.fixture
def result() -> GuardResult:
    return GuardResult()


def _minimal_canonical(ctx: GuardContext) -> dict:
    """Build a minimal valid canonical packet for the given context."""
    return {
        "aiv_version": "1.0.0",
        "packet_schema_version": "1.0.0",
        "identification": {
            "head_sha": ctx.head_sha,
            "pr_id": ctx.pr_number,
            "pr_url": f"https://github.com/{ctx.owner}/{ctx.repo}/pull/{ctx.pr_number}",
            "base_sha": ctx.base_sha,
            "created_at": "2026-01-01T00:00:00Z",
            "created_by": "author",
        },
        "classification": {
            "risk_tier": "R0",
            "sod_mode": "S0",
            "blast_radius": "local",
            "classification_rationale": "Trivial change",
            "classified_by": "author",
            "classified_at": "2026-01-01T00:00:00Z",
            "critical_surfaces": [],
        },
        "claims": [
            {"id": "C1", "description": "Test claim", "evidence_refs": ["E-B1"]},
        ],
        "evidence_items": [
            {"id": "E-A1", "class": "A", "claim_refs": ["C1"],
             "artifacts": [{"type": "ci_run", "reference": "https://github.com/x/y/actions/runs/123"}]},
            {"id": "E-B1", "class": "B", "claim_refs": ["C1"],
             "artifacts": [{"type": "scope_inventory",
                            "reference": "inline-json:" + json.dumps(["README.md"])}]},
        ],
        "attestations": [{
            "id": "att-1",
            "verifier_id": "verifier",
            "verifier_identity_type": "github",
            "timestamp": "2026-01-01T00:00:00Z",
            "evidence_classes_validated": ["A", "B"],
            "validation_rules_checked": ["CT-001"],
            "findings": [],
            "signature_method": "unsigned",
            "decision": "COMPLIANT",
        }],
        "known_limitations": ["Markdown-only validation"],
    }


# ------------------------------------------------------------------ #
# Model tests
# ------------------------------------------------------------------ #

class TestGuardModels:
    def test_guard_result_add_block(self, result: GuardResult):
        f = result.add_block("CT-001", "test error")
        assert result.block_count == 1
        assert result.overall_result == OverallResult.FAIL
        assert f.severity == GuardSeverity.BLOCK

    def test_guard_result_add_warn(self, result: GuardResult):
        result.add_warn("CT-002", "test warning")
        assert result.warn_count == 1
        assert result.block_count == 0

    def test_guard_result_finalize_pass(self, result: GuardResult):
        result.finalize()
        assert result.overall_result == OverallResult.PASS

    def test_guard_result_finalize_fail(self, result: GuardResult):
        result.add_block("X-001", "blocker")
        result.finalize()
        assert result.overall_result == OverallResult.FAIL
        assert result.compliance_level == "NON-COMPLIANT"

    def test_guard_result_to_dict(self, result: GuardResult):
        result.add_warn("W-001", "warning")
        d = result.to_dict()
        assert "validation_result" in d
        vr = d["validation_result"]
        assert vr["warn_count"] == 1
        assert vr["block_count"] == 0
        assert len(vr["findings"]) == 1

    def test_upsert_rule_result_insert(self, result: GuardResult):
        result.upsert_rule_result("CT-001", "PASS")
        assert len(result.validation_rule_results) == 1
        assert result.validation_rule_results[0].result == "PASS"

    def test_upsert_rule_result_update(self, result: GuardResult):
        result.upsert_rule_result("CT-001", "PASS")
        result.upsert_rule_result("CT-001", "FAIL", "F-1")
        assert len(result.validation_rule_results) == 1
        assert result.validation_rule_results[0].result == "FAIL"

    def test_guard_context_full_repo(self, ctx: GuardContext):
        assert ctx.full_repo == "TestOwner/test-repo"

    def test_evidence_class_result_to_dict(self):
        ecr = EvidenceClassResult("A", True, True, True)
        d = ecr.to_dict()
        assert d["class"] == "A"
        assert d["required"] is True


# ------------------------------------------------------------------ #
# Regex tests
# ------------------------------------------------------------------ #

class TestGuardRegex:
    def test_hex_sha_40(self):
        assert HEX_SHA_40_OR_64.match("a" * 40)

    def test_hex_sha_64(self):
        assert HEX_SHA_40_OR_64.match("a" * 64)

    def test_hex_sha_short_rejects(self):
        assert not HEX_SHA_40_OR_64.match("a" * 10)

    def test_mutable_branch_main(self):
        assert MUTABLE_BRANCH_PATTERN.search("/blob/main/src/foo.py")

    def test_immutable_sha(self):
        assert not MUTABLE_BRANCH_PATTERN.search(f"/blob/{'a' * 40}/src/foo.py")

    def test_github_actions_run(self):
        assert GITHUB_ACTIONS_RUN.search("https://github.com/o/r/actions/runs/12345")

    def test_line_anchor(self):
        assert LINE_ANCHOR.search("#L10-L20")
        assert not LINE_ANCHOR.search("#section-1")


# ------------------------------------------------------------------ #
# Canonical validation tests
# ------------------------------------------------------------------ #

class TestCanonicalValidation:
    def test_valid_r0_packet(self, ctx: GuardContext, result: GuardResult):
        packet = _minimal_canonical(ctx)
        ok = validate_canonical(packet, ctx, result, ["README.md"])
        assert ok is True
        assert result.block_count == 0

    def test_missing_required_field_blocks(self, ctx: GuardContext, result: GuardResult):
        packet = _minimal_canonical(ctx)
        del packet["identification"]["head_sha"]
        ok = validate_canonical(packet, ctx, result, ["README.md"])
        assert ok is False
        assert result.block_count >= 1

    def test_head_sha_mismatch_blocks(self, ctx: GuardContext, result: GuardResult):
        packet = _minimal_canonical(ctx)
        packet["identification"]["head_sha"] = "c" * 40
        ok = validate_canonical(packet, ctx, result, ["README.md"])
        assert ok is False
        assert any("mismatch" in f.description.lower() for f in result.findings)

    def test_invalid_risk_tier_blocks(self, ctx: GuardContext, result: GuardResult):
        packet = _minimal_canonical(ctx)
        packet["classification"]["risk_tier"] = "R5"
        ok = validate_canonical(packet, ctx, result, ["README.md"])
        assert ok is False

    def test_r2_requires_s1(self, ctx: GuardContext, result: GuardResult):
        packet = _minimal_canonical(ctx)
        packet["classification"]["risk_tier"] = "R2"
        packet["classification"]["sod_mode"] = "S0"
        # Add required evidence for R2
        packet["evidence_items"].append(
            {"id": "E-C1", "class": "C", "claim_refs": ["C1"],
             "validation_method": "AST analysis",
             "artifacts": []}
        )
        packet["evidence_items"].append(
            {"id": "E-E1", "class": "E", "claim_refs": ["C1"],
             "artifacts": [{"type": "requirement_reference",
                            "reference": f"https://github.com/x/y/blob/{'a' * 40}/spec.md#L1-L5"}]}
        )
        ok = validate_canonical(packet, ctx, result, ["README.md"])
        assert ok is False
        assert any("S1" in f.description for f in result.findings)

    def test_scope_inventory_mismatch_blocks(self, ctx: GuardContext, result: GuardResult):
        packet = _minimal_canonical(ctx)
        # Scope says README.md but changed files says something else
        ok = validate_canonical(packet, ctx, result, ["src/main.py"])
        assert ok is False
        assert any("scope inventory" in f.description.lower() for f in result.findings)

    def test_non_compliant_decision_blocks(self, ctx: GuardContext, result: GuardResult):
        packet = _minimal_canonical(ctx)
        packet["attestations"][0]["decision"] = "NON-COMPLIANT"
        packet["attestations"][0]["blocking_findings"] = [{"id": "F-1"}]
        packet["attestations"][0]["rationale"] = "Intentionally non-compliant"
        ok = validate_canonical(packet, ctx, result, ["README.md"])
        assert ok is False

    def test_get_path_helper(self):
        obj = {"a": {"b": {"c": 42}}}
        assert _get_path(obj, ["a", "b", "c"]) == 42
        assert _get_path(obj, ["a", "x"]) is None
        assert _get_path(obj, []) == obj


# ------------------------------------------------------------------ #
# Manifest validation tests
# ------------------------------------------------------------------ #

class TestManifestValidation:
    def test_valid_class_a(self):
        manifest = {
            "schema_version": "1.0.0",
            "head_sha": "a" * 40,
            "run": {"repository": "owner/repo", "run_id": "123"},
            "execution_environment": {
                "os": {"name": "Ubuntu", "release": "22.04"},
                "node": "18.0.0",
                "npm": "9.0.0",
            },
            "test_results": {"pass": 10, "fail": 0, "skip": 0},
            "test_list": ["test1"],
            "executed_checks": [{"id": "test1"}],
        }
        errors = validate_class_a_manifest(manifest, "a" * 40, "owner/repo")
        assert errors == []

    def test_class_a_head_sha_mismatch(self):
        manifest = {
            "schema_version": "1.0.0",
            "head_sha": "b" * 40,
            "run": {"repository": "owner/repo", "run_id": "123"},
            "execution_environment": {
                "os": {"name": "Ubuntu", "release": "22.04"},
                "node": "18.0.0",
                "npm": "9.0.0",
            },
            "test_results": {"pass": 10, "fail": 0, "skip": 0},
            "test_list": ["test1"],
            "executed_checks": [{"id": "test1"}],
        }
        errors = validate_class_a_manifest(manifest, "a" * 40, "owner/repo")
        assert any("mismatch" in e for e in errors)

    def test_valid_class_c(self):
        manifest = {
            "schema_version": "1.0.0",
            "head_sha": "a" * 40,
            "search_method": {"tool": "grep", "deterministic": True},
            "search_scope": ["src/"],
            "patterns": ["console.log"],
            "search_results_artifact": "negative_evidence.txt",
            "test_integrity": {
                "machine_readable": True,
                "required_evidence_files": ["f1"],
                "semantic_report_artifact": "test_integrity_semantic.json",
                "method": "AST semantic analysis",
            },
        }
        errors = validate_class_c_manifest(manifest, "a" * 40)
        assert errors == []

    def test_valid_semantic(self):
        manifest = {
            "schema_version": "1.0.0",
            "head_sha": "a" * 40,
            "base_sha": "b" * 40,
            "overall_result": "PASS",
        }
        errors = validate_semantic_manifest(manifest, "a" * 40, "b" * 40)
        assert errors == []

    def test_semantic_result_fail(self):
        manifest = {
            "schema_version": "1.0.0",
            "head_sha": "a" * 40,
            "overall_result": "FAIL",
        }
        errors = validate_semantic_manifest(manifest, "a" * 40, "")
        assert any("PASS" in e for e in errors)

    def test_valid_durable(self):
        digest = "sha256:" + "a" * 64
        manifest = {
            "schema_version": "1.0.0",
            "head_sha": "a" * 40,
            "backend": "ghcr_oci",
            "export_result": "SUCCESS",
            "digest": digest,
            "oci_ref_digest": f"ghcr.io/x/y@{digest}",
            "tar_sha256": "b" * 64,
        }
        errors = validate_durable_manifest(manifest, "a" * 40)
        assert errors == []

    def test_durable_bad_digest(self):
        manifest = {
            "schema_version": "1.0.0",
            "head_sha": "a" * 40,
            "backend": "ghcr_oci",
            "export_result": "SUCCESS",
            "digest": "not-a-digest",
            "oci_ref_digest": "x",
            "tar_sha256": "b" * 64,
        }
        errors = validate_durable_manifest(manifest, "a" * 40)
        assert any("sha256" in e for e in errors)


# ------------------------------------------------------------------ #
# Runner tests (with mocked API)
# ------------------------------------------------------------------ #

class MockAPI:
    """Mock GitHubAPI that returns no files / no runs."""
    def list_pr_files(self, ctx):
        return []
    def get_workflow_run(self, ctx, run_id):
        return None
    def list_run_artifacts(self, ctx, run_id):
        return []


class TestGuardRunner:
    def test_empty_body_fails(self, ctx: GuardContext):
        ctx.pr_body = ""
        runner = GuardRunner(ctx, MockAPI())
        result = runner.run()
        # Empty body should fail (no packet header found)
        assert result.block_count >= 1 or result.warn_count >= 1

    def test_valid_markdown_packet(self, ctx: GuardContext):
        ctx.pr_body = (
            "# AIV Verification Packet (v2.1)\n\n"
            "**Commit:** `abc`\n"
            "**Protocol:** AIV v2.0\n\n"
            "## Claim(s)\n\n1. Test claim\n\n"
            "## Evidence\n\n"
            "### Class E (Intent Alignment)\n\n- link\n\n"
            "### Class B (Referential Evidence)\n\n**Scope Inventory (required)**\n\n- x\n\n"
            "### Class A (Execution Evidence)\n\n- ci\n\n"
            "## Verification Methodology\n\nArtifact-based.\n\n"
            "## Summary\n\nDone.\n"
        )
        runner = GuardRunner(ctx, MockAPI())
        result = runner.run()
        # Markdown-only should pass structure checks
        assert result.canonical_enabled is False

    def test_fast_track_docs_only(self, ctx: GuardContext):
        """Docs-only PRs should be fast-track eligible."""
        ctx.pr_body = "# Some docs update"

        class DocsAPI(MockAPI):
            def list_pr_files(self, ctx):
                return [ChangedFile("README.md", "modified")]

        runner = GuardRunner(ctx, DocsAPI())
        assert runner._is_fast_track() is True

    def test_non_fast_track_code(self, ctx: GuardContext):
        """Code PRs should NOT be fast-track eligible."""
        ctx.pr_body = "# Code change"

        class CodeAPI(MockAPI):
            def list_pr_files(self, ctx):
                return [ChangedFile("src/main.py", "modified")]

        runner = GuardRunner(ctx, CodeAPI())
        assert runner._is_fast_track() is False

    def test_required_classes_tiers(self):
        assert REQUIRED_CLASSES["R0"] == ["A", "B"]
        assert REQUIRED_CLASSES["R1"] == ["A", "B", "E"]
        assert REQUIRED_CLASSES["R2"] == ["A", "B", "C", "E"]
        assert REQUIRED_CLASSES["R3"] == ["A", "B", "C", "D", "E", "F"]
