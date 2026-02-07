"""
tests/integration/test_svp_full_workflow.py

E2E tests for the SVP Protocol Suite workflow.

Validates the verifier's journey through all 4 phases:
  Phase 1: Black Box Prediction (svp predict)
  Phase 2: Mental Trace (svp trace)
  Phase 3: Adversarial Probe (svp probe)
  Phase 4: Ownership Lock (manual — tested via model injection)

Also tests:
  - Session persistence to .svp/ directory
  - Validation gate (svp validate) exit codes
  - S014 enforcement (missing falsification scenarios)
  - Incremental session building across commands
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = pytest.mark.integration

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class TestSVPFullWorkflow:
    """E2E: Does the full SVP verifier journey work via CLI?"""

    @pytest.fixture(autouse=True)
    def svp_dir(self, tmp_path, monkeypatch):
        """Run each test in a clean temp directory with its own .svp/."""
        monkeypatch.chdir(tmp_path)
        self.tmp = tmp_path
        self.svp = tmp_path / ".svp"

    def _run(self, *args: str, expect_ok: bool = True) -> subprocess.CompletedProcess:
        """Run an aiv svp subcommand."""
        result = subprocess.run(
            [sys.executable, "-m", "aiv", "svp", *args],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=str(self.tmp),
            env={**__import__("os").environ, "PYTHONPATH": str(PROJECT_ROOT), "PYTHONUTF8": "1"},
            encoding="utf-8",
            errors="replace",
        )
        if expect_ok:
            assert result.returncode == 0, (
                f"Command failed: aiv svp {' '.join(args)}\n"
                f"STDOUT: {result.stdout[-500:]}\n"
                f"STDERR: {result.stderr[-500:]}"
            )
        return result

    def _session_path(self, pr: int = 42) -> Path:
        return self.svp / f"session-pr{pr}.json"

    def _load_session(self, pr: int = 42) -> dict:
        return json.loads(self._session_path(pr).read_text(encoding="utf-8"))

    # ------------------------------------------------------------------ #
    # Phase 1: Prediction
    # ------------------------------------------------------------------ #

    def test_predict_creates_session(self):
        """SVP-E2E-01: svp predict creates .svp/session-pr42.json."""
        self._run(
            "predict", "42",
            "--repo", "test-org/test-repo",
            "--verifier", "alice",
            "--test-file", "tests/test_auth.py",
            "--approach", "The implementation should validate JWT tokens by checking expiry and signature using the standard library hmac module.",
            "--complexity", "O(n)",
            "--edge-cases", "expired token",
            "--edge-cases", "malformed header",
        )

        assert self._session_path().exists(), ".svp/session-pr42.json should exist"
        session = self._load_session()
        assert session["pr_number"] == 42
        assert session["verifier_id"] == "alice"
        assert session["prediction"] is not None
        assert session["prediction"]["predicted_complexity"] == "O(n)"
        assert len(session["prediction"]["expected_edge_cases"]) == 2

    # ------------------------------------------------------------------ #
    # Phase 2: Trace
    # ------------------------------------------------------------------ #

    def test_trace_appends_to_session(self):
        """SVP-E2E-02: svp trace appends a trace record to existing session."""
        # First create the session via predict
        self._run(
            "predict", "42",
            "--repo", "test-org/test-repo",
            "--verifier", "alice",
            "--test-file", "tests/test_auth.py",
            "--approach", "The implementation should validate JWT tokens by checking expiry and signature using the standard library hmac module.",
            "--edge-cases", "expired token",
            "--edge-cases", "malformed header",
        )

        # Then add a trace
        self._run(
            "trace", "42",
            "--repo", "test-org/test-repo",
            "--verifier", "alice",
            "--function", "src/auth.py::verify_token",
            "--notes", "The function first decodes the base64 header, extracts the exp claim, compares to current UTC time. If expired, raises AuthError. Then verifies HMAC signature against the secret.",
            "--edge-case", "Token with exp=0 (epoch start)",
            "--predicted-output", "AuthError('Token expired')",
            "--confidence", "high",
        )

        session = self._load_session()
        assert len(session["traces"]) == 1
        assert session["traces"][0]["function_path"] == "src/auth.py::verify_token"
        assert session["traces"][0]["confidence"] == "high"

    # ------------------------------------------------------------------ #
    # Phase 3: Probe
    # ------------------------------------------------------------------ #

    def test_probe_records_checklist(self):
        """SVP-E2E-03: svp probe records adversarial probe with falsification scenario."""
        # Build session through phases 1-2
        self._run(
            "predict", "42",
            "--repo", "test-org/test-repo",
            "--verifier", "alice",
            "--test-file", "tests/test_auth.py",
            "--approach", "The implementation should validate JWT tokens by checking expiry and signature using the standard library hmac module.",
            "--edge-cases", "expired token",
            "--edge-cases", "malformed header",
        )
        self._run(
            "trace", "42",
            "--repo", "test-org/test-repo",
            "--verifier", "alice",
            "--function", "src/auth.py::verify_token",
            "--notes", "The function first decodes the base64 header, extracts the exp claim, compares to current UTC time. If expired, raises AuthError. Then verifies HMAC signature against the secret.",
            "--edge-case", "Token with exp=0 (epoch start)",
            "--predicted-output", "AuthError('Token expired')",
        )

        # Add probe with falsification scenario
        self._run(
            "probe", "42",
            "--repo", "test-org/test-repo",
            "--verifier", "alice",
            "--assessment", "No AI tells detected. Token validation uses constant-time comparison.",
            "--why-question", "Why was hmac.compare_digest chosen over == for signature comparison?",
            "--why-context", "Security review of auth module",
            "--falsify-claim", "C-001",
            "--falsify-scenario", "If test_verify_token_expired returns 200 OK instead of 401, the expiry claim is falsified.",
        )

        session = self._load_session()
        assert session["probe"] is not None
        assert session["probe"]["happy_path_bias_checked"] is True
        assert session["probe"]["context_amnesia_checked"] is True
        assert session["probe"]["fragile_assertions_checked"] is True
        assert len(session["probe"]["why_questions"]) == 1
        assert len(session["probe"]["falsification_scenarios"]) == 1
        assert session["probe"]["falsification_scenarios"][0]["claim_id"] == "C-001"

    # ------------------------------------------------------------------ #
    # Validate: Gate behavior
    # ------------------------------------------------------------------ #

    def test_validate_incomplete_session_fails(self):
        """SVP-E2E-04: svp validate exits 1 when phases are missing."""
        # Only predict — missing trace, probe, ownership
        self._run(
            "predict", "42",
            "--repo", "test-org/test-repo",
            "--verifier", "alice",
            "--test-file", "tests/test_auth.py",
            "--approach", "The implementation should validate JWT tokens by checking expiry and signature using the standard library hmac module.",
            "--edge-cases", "expired token",
            "--edge-cases", "malformed header",
        )

        result = self._run("validate", "42", expect_ok=False)
        assert result.returncode == 1, "Incomplete session should exit 1"

        output = json.loads(result.stdout)
        assert len(output["errors"]) > 0
        rule_ids = {e["rule_id"] for e in output["errors"]}
        assert "S005" in rule_ids, "Missing trace should trigger S005"

    def test_validate_no_session_fails(self):
        """SVP-E2E-05: svp validate exits 1 when no session exists."""
        result = self._run("validate", "999", expect_ok=False)
        assert result.returncode == 1

    def test_validate_missing_falsification_fails(self):
        """SVP-E2E-06: svp validate exits 1 when probe has no falsification scenarios (S014)."""
        # Build session through phases 1-3 but WITHOUT falsification scenario
        self._run(
            "predict", "42",
            "--repo", "test-org/test-repo",
            "--verifier", "alice",
            "--test-file", "tests/test_auth.py",
            "--approach", "The implementation should validate JWT tokens by checking expiry and signature using the standard library hmac module.",
            "--edge-cases", "expired token",
            "--edge-cases", "malformed header",
        )
        self._run(
            "trace", "42",
            "--repo", "test-org/test-repo",
            "--verifier", "alice",
            "--function", "src/auth.py::verify_token",
            "--notes", "The function first decodes the base64 header, extracts the exp claim, compares to current UTC time. If expired, raises AuthError. Then verifies HMAC signature against the secret.",
            "--edge-case", "Token with exp=0 (epoch start)",
            "--predicted-output", "AuthError('Token expired')",
        )
        # Probe WITHOUT --falsify-claim / --falsify-scenario
        self._run(
            "probe", "42",
            "--repo", "test-org/test-repo",
            "--verifier", "alice",
            "--assessment", "No AI tells detected in this PR.",
            "--why-question", "Why was this approach chosen over alternatives?",
        )

        result = self._run("validate", "42", expect_ok=False)
        assert result.returncode == 1, "Missing falsification scenarios should exit 1"

        output = json.loads(result.stdout)
        rule_ids = {e["rule_id"] for e in output["errors"]}
        assert "S014" in rule_ids, (
            f"S014 should fire for missing falsification scenarios. Got: {rule_ids}"
        )

    # ------------------------------------------------------------------ #
    # Full journey (phases 1-3 via CLI + phase 4 via model injection)
    # ------------------------------------------------------------------ #

    def test_full_journey_passes_validation(self):
        """SVP-E2E-07: Complete 4-phase journey passes svp validate.

        Phases 1-3 are exercised via CLI commands.
        Phase 4 (ownership commit) is injected directly into the session
        JSON because it requires actual git operations that we mock here.
        """
        # Phase 1: Predict
        self._run(
            "predict", "42",
            "--repo", "test-org/test-repo",
            "--verifier", "alice",
            "--test-file", "tests/test_auth.py",
            "--approach", "The implementation should validate JWT tokens by checking expiry and signature using the standard library hmac module.",
            "--edge-cases", "expired token",
            "--edge-cases", "malformed header",
        )

        # Phase 2: Trace
        self._run(
            "trace", "42",
            "--repo", "test-org/test-repo",
            "--verifier", "alice",
            "--function", "src/auth.py::verify_token",
            "--notes", "The function first decodes the base64 header, extracts the exp claim, compares to current UTC time. If expired, raises AuthError. Then verifies HMAC signature against the secret.",
            "--edge-case", "Token with exp=0 (epoch start)",
            "--predicted-output", "AuthError('Token expired')",
        )

        # Phase 3: Probe (with falsification scenario)
        self._run(
            "probe", "42",
            "--repo", "test-org/test-repo",
            "--verifier", "alice",
            "--assessment", "No AI tells detected. Token validation uses constant-time comparison.",
            "--why-question", "Why was hmac.compare_digest chosen over == for signature comparison?",
            "--why-context", "Security review of auth module",
            "--falsify-claim", "C-001",
            "--falsify-scenario", "If test_verify_token_expired returns 200 OK instead of 401, the expiry claim is falsified.",
        )

        # Phase 4: Inject ownership commit directly into session JSON
        session_data = self._load_session()
        session_data["ownership_commit"] = {
            "pr_number": 42,
            "repository": "test-org/test-repo",
            "commit_sha": "a" * 40,
            "author_github_id": "alice",
            "commit_message": "ownership: clarify verify_token naming and add docstring",
            "committed_at": "2026-02-07T03:30:00Z",
            "renames": [{
                "file_path": "src/auth.py",
                "original_name": "check_tok",
                "new_name": "verify_token_expiry",
                "change_type": "function",
                "justification": "Clarifies that this function specifically checks token expiry",
            }],
            "docstrings": [],
            "verified_at": "2026-02-07T03:30:00Z",
        }
        self._session_path().write_text(
            json.dumps(session_data, indent=2), encoding="utf-8"
        )

        # Validate: should pass
        result = self._run("validate", "42")
        output = json.loads(result.stdout)

        assert output["phase_0_complete"] is True, "Phase 0 (Sanity) should pass"
        assert output["phase_1_complete"] is True, "Phase 1 (Prediction) should pass"
        assert output["phase_2_complete"] is True, "Phase 2 (Trace) should pass"
        assert output["phase_3_complete"] is True, "Phase 3 (Probe) should pass"
        assert output["phase_4_complete"] is True, "Phase 4 (Ownership) should pass"
        assert len(output["errors"]) == 0, (
            f"Complete session should have 0 errors, got:\n"
            + "\n".join(f"  [{e['rule_id']}] {e['message']}" for e in output["errors"])
        )

    # ------------------------------------------------------------------ #
    # Status command
    # ------------------------------------------------------------------ #

    def test_status_shows_progress(self):
        """SVP-E2E-08: svp status shows phase completion for partial session."""
        self._run(
            "predict", "42",
            "--repo", "test-org/test-repo",
            "--verifier", "alice",
            "--test-file", "tests/test_auth.py",
            "--approach", "The implementation should validate JWT tokens by checking expiry and signature using the standard library hmac module.",
            "--edge-cases", "expired token",
            "--edge-cases", "malformed header",
        )

        result = self._run("status", "42")
        assert "Phase 1" in result.stdout
        assert "Prediction" in result.stdout

    def test_status_no_session(self):
        """SVP-E2E-09: svp status exits 1 when no session exists."""
        result = self._run("status", "999", expect_ok=False)
        assert result.returncode == 1
