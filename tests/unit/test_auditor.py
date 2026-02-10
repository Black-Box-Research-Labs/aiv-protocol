"""
tests/unit/test_auditor.py

Unit tests for the PacketAuditor — verifies detection of quality issues
that the validation pipeline does not catch.
"""

from pathlib import Path
from unittest.mock import patch

from aiv.lib.auditor import AuditSeverity, PacketAuditor

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

MINIMAL_CLEAN_PACKET = """\
# AIV Verification Packet (v2.1)

**Commit:** `abc1234`
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: module
  classification_rationale: "Test packet"
  classified_by: "cascade"
  classified_at: "2026-02-07T00:00:00Z"
```

## Claim(s)

1. Added a new feature to the system.
2. All tests pass with zero regressions.
3. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [Test Spec](https://github.com/ImmortalDemonGod/aiv-protocol/blob/abc1234/SPECIFICATION.md)
- **Requirements Verified:**
  1. Feature implemented per spec

### Class B (Referential Evidence)

**Scope Inventory (required)**

- Modified:
  - `src/feature.py`

### Class A (Execution Evidence)

- 100/100 pytest tests pass

---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.

---

## Summary

Added new feature per specification.
"""


def _write_packet(tmp_path: Path, name: str, content: str) -> Path:
    """Write a packet file and return its path."""
    packet_path = tmp_path / name
    packet_path.write_text(content, encoding="utf-8")
    return packet_path


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestAuditorCleanPacket:
    """A well-formed packet should produce zero findings."""

    def test_clean_packet_no_findings(self, tmp_path: Path):
        _write_packet(tmp_path, "VERIFICATION_PACKET_CLEAN.md", MINIMAL_CLEAN_PACKET)
        auditor = PacketAuditor()
        result = auditor.audit(tmp_path)
        assert result.packets_scanned == 1
        assert result.packets_with_issues == 0
        assert len(result.findings) == 0

    def test_template_excluded(self, tmp_path: Path):
        _write_packet(tmp_path, "VERIFICATION_PACKET_TEMPLATE.md", "# Template")
        _write_packet(tmp_path, "VERIFICATION_PACKET_CLEAN.md", MINIMAL_CLEAN_PACKET)
        auditor = PacketAuditor()
        result = auditor.audit(tmp_path)
        assert result.packets_scanned == 1  # template excluded


class TestCommitPending:
    """Detect packets where commit SHA was never backfilled."""

    def test_commit_pending_detected(self, tmp_path: Path):
        body = MINIMAL_CLEAN_PACKET.replace("`abc1234`", "`pending`")
        _write_packet(tmp_path, "VERIFICATION_PACKET_BAD.md", body)
        auditor = PacketAuditor()
        result = auditor.audit(tmp_path)
        commit_findings = [f for f in result.findings if f.finding_type == "COMMIT_PENDING"]
        assert len(commit_findings) == 1
        assert commit_findings[0].severity == AuditSeverity.ERROR

    def test_commit_filled_passes(self, tmp_path: Path):
        _write_packet(tmp_path, "VERIFICATION_PACKET_OK.md", MINIMAL_CLEAN_PACKET)
        auditor = PacketAuditor()
        result = auditor.audit(tmp_path)
        commit_findings = [f for f in result.findings if f.finding_type == "COMMIT_PENDING"]
        assert len(commit_findings) == 0


class TestClassELink:
    """Detect plain-text or mutable Class E links."""

    def test_plain_text_link_detected(self, tmp_path: Path):
        body = MINIMAL_CLEAN_PACKET.replace(
            "- **Link:** [Test Spec](https://github.com/ImmortalDemonGod/aiv-protocol/blob/abc1234/SPECIFICATION.md)",
            "- **Link:** AUDIT_REPORT.md — Finding L01",
        )
        _write_packet(tmp_path, "VERIFICATION_PACKET_BAD.md", body)
        auditor = PacketAuditor()
        result = auditor.audit(tmp_path)
        link_findings = [f for f in result.findings if f.finding_type == "CLASS_E_NO_URL"]
        assert len(link_findings) == 1
        assert link_findings[0].severity == AuditSeverity.WARNING

    def test_mutable_link_detected(self, tmp_path: Path):
        body = MINIMAL_CLEAN_PACKET.replace(
            "https://github.com/ImmortalDemonGod/aiv-protocol/blob/abc1234/SPECIFICATION.md",
            "https://github.com/ImmortalDemonGod/aiv-protocol/blob/main/SPECIFICATION.md",
        )
        _write_packet(tmp_path, "VERIFICATION_PACKET_BAD.md", body)
        auditor = PacketAuditor()
        result = auditor.audit(tmp_path)
        mutable_findings = [f for f in result.findings if f.finding_type == "CLASS_E_MUTABLE"]
        assert len(mutable_findings) == 1
        assert mutable_findings[0].severity == AuditSeverity.ERROR

    def test_sha_pinned_link_passes(self, tmp_path: Path):
        _write_packet(tmp_path, "VERIFICATION_PACKET_OK.md", MINIMAL_CLEAN_PACKET)
        auditor = PacketAuditor()
        result = auditor.audit(tmp_path)
        link_findings = [
            f for f in result.findings if f.finding_type in ("CLASS_E_NO_URL", "CLASS_E_MUTABLE", "CLASS_E_EMPTY")
        ]
        assert len(link_findings) == 0


class TestTodoRemnants:
    """Detect TODO/TBD left in filled-in sections."""

    def test_todo_in_claim_detected(self, tmp_path: Path):
        body = MINIMAL_CLEAN_PACKET.replace(
            "1. Added a new feature to the system.",
            "1. TODO: Primary claim.",
        )
        _write_packet(tmp_path, "VERIFICATION_PACKET_BAD.md", body)
        auditor = PacketAuditor()
        result = auditor.audit(tmp_path)
        todo_findings = [f for f in result.findings if f.finding_type == "CLAIM_TODO"]
        assert len(todo_findings) == 1
        assert todo_findings[0].severity == AuditSeverity.ERROR

    def test_todo_in_summary_detected(self, tmp_path: Path):
        body = MINIMAL_CLEAN_PACKET.replace(
            "Added new feature per specification.",
            "TODO: One-line summary.",
        )
        _write_packet(tmp_path, "VERIFICATION_PACKET_BAD.md", body)
        auditor = PacketAuditor()
        result = auditor.audit(tmp_path)
        summary_findings = [f for f in result.findings if f.finding_type == "SUMMARY_TODO"]
        assert len(summary_findings) == 1
        assert summary_findings[0].severity == AuditSeverity.ERROR

    def test_classified_by_todo_detected(self, tmp_path: Path):
        body = MINIMAL_CLEAN_PACKET.replace(
            'classified_by: "cascade"',
            'classified_by: "TODO"',
        )
        _write_packet(tmp_path, "VERIFICATION_PACKET_BAD.md", body)
        auditor = PacketAuditor()
        result = auditor.audit(tmp_path)
        cb_findings = [f for f in result.findings if f.finding_type == "CLASSIFIED_BY_TODO"]
        assert len(cb_findings) == 1

    def test_blast_radius_todo_detected(self, tmp_path: Path):
        body = MINIMAL_CLEAN_PACKET.replace(
            "blast_radius: module",
            "blast_radius: TODO",
        )
        _write_packet(tmp_path, "VERIFICATION_PACKET_BAD.md", body)
        auditor = PacketAuditor()
        result = auditor.audit(tmp_path)
        br_findings = [f for f in result.findings if f.finding_type == "BLAST_RADIUS_TODO"]
        assert len(br_findings) == 1

    def test_todo_meta_description_not_flagged(self, tmp_path: Path):
        """Lines that *describe* the TODO system should not trigger TODO_PRESENT."""
        body = MINIMAL_CLEAN_PACKET.replace(
            "1. Added a new feature to the system.",
            "1. The substance patch correctly rejects TODO-only evidence sections.",
        )
        _write_packet(tmp_path, "VERIFICATION_PACKET_META.md", body)
        auditor = PacketAuditor()
        result = auditor.audit(tmp_path)
        todo_findings = [f for f in result.findings if f.finding_type == "TODO_PRESENT"]
        assert len(todo_findings) == 0

    def test_todo_finding_type_name_not_flagged(self, tmp_path: Path):
        """Lines listing auditor finding types (COMMIT_PENDING, TODO remnants) should not trigger."""
        body = MINIMAL_CLEAN_PACKET.replace(
            "1. Added a new feature to the system.",
            "1. Auditor detects COMMIT_PENDING, CLASS_E_NO_URL, TODO remnants, and missing Class F.",
        )
        _write_packet(tmp_path, "VERIFICATION_PACKET_META2.md", body)
        auditor = PacketAuditor()
        result = auditor.audit(tmp_path)
        todo_findings = [f for f in result.findings if f.finding_type == "TODO_PRESENT"]
        assert len(todo_findings) == 0


class TestEvidenceTodoSeverity:
    """Verify that TODOs inside evidence sections are ERROR (blocking), not WARNING.

    These tests cover the auditor change in auditor.py#L251-L262 (CLASS_E_NO_URL
    severity escalation) and auditor.py#L276-L296 (evidence_section tracking).
    """

    def test_evidence_todo_is_error(self, tmp_path: Path):
        """A TODO inside ## Evidence must be AuditSeverity.ERROR, not WARNING.

        Before the fix, all TODO_PRESENT findings were WARNING (non-blocking).
        After: TODOs in evidence sections are ERROR because they mean the
        evidence is missing, not just incomplete metadata.
        """
        body = MINIMAL_CLEAN_PACKET.replace(
            "- 100/100 pytest tests pass",
            "- TODO: Paste test output here",
        )
        _write_packet(tmp_path, "VERIFICATION_PACKET_BAD.md", body)
        auditor = PacketAuditor()
        result = auditor.audit(tmp_path)
        evidence_todos = [
            f for f in result.findings if f.finding_type == "TODO_PRESENT" and f.severity == AuditSeverity.ERROR
        ]
        assert len(evidence_todos) >= 1, (
            f"Expected at least 1 ERROR-severity TODO_PRESENT in evidence section, got findings: {result.findings}"
        )

    def test_class_e_todo_link_is_error(self, tmp_path: Path):
        """Class E link containing 'TODO' must be AuditSeverity.ERROR.

        Before the fix, CLASS_E_NO_URL was always WARNING. After: if the link
        text contains the word 'TODO', it's ERROR because it means the intent
        evidence was never provided.
        """
        body = MINIMAL_CLEAN_PACKET.replace(
            "- **Link:** [Test Spec](https://github.com/ImmortalDemonGod/aiv-protocol/blob/abc1234/SPECIFICATION.md)",
            "- **Link:** TODO: SHA-pinned link to spec/issue/directive",
        )
        _write_packet(tmp_path, "VERIFICATION_PACKET_BAD.md", body)
        auditor = PacketAuditor()
        result = auditor.audit(tmp_path)
        class_e_findings = [f for f in result.findings if f.finding_type == "CLASS_E_NO_URL"]
        assert len(class_e_findings) == 1
        assert class_e_findings[0].severity == AuditSeverity.ERROR, (
            f"Expected ERROR for TODO in Class E link, got {class_e_findings[0].severity}"
        )

    def test_classification_todo_stays_warning(self, tmp_path: Path):
        """A TODO in classification_rationale (outside evidence) stays WARNING.

        Only evidence-section TODOs were escalated to ERROR. TODOs in the
        classification YAML block should remain WARNING because they are
        metadata guidance, not missing evidence.
        """
        body = MINIMAL_CLEAN_PACKET.replace(
            'classification_rationale: "Test packet"',
            'classification_rationale: "TODO: Describe why this tier was chosen"',
        )
        _write_packet(tmp_path, "VERIFICATION_PACKET_WARN.md", body)
        auditor = PacketAuditor()
        result = auditor.audit(tmp_path)
        todo_findings = [f for f in result.findings if f.finding_type == "TODO_PRESENT"]
        # Should have at least one WARNING (not ERROR) for the classification TODO
        warning_todos = [f for f in todo_findings if f.severity == AuditSeverity.WARNING]
        error_todos = [f for f in todo_findings if f.severity == AuditSeverity.ERROR]
        assert len(warning_todos) >= 1, f"Expected WARNING for classification TODO, got findings: {todo_findings}"
        assert len(error_todos) == 0, f"Classification TODO should NOT be ERROR, got: {error_todos}"


class TestFixNoclassF:
    """Detect bug-fix claims without Class F provenance evidence."""

    def test_fix_claim_without_class_f_detected(self, tmp_path: Path):
        body = MINIMAL_CLEAN_PACKET.replace(
            "1. Added a new feature to the system.",
            "1. Fixed authentication bypass vulnerability.",
        )
        _write_packet(tmp_path, "VERIFICATION_PACKET_BAD.md", body)
        auditor = PacketAuditor()
        result = auditor.audit(tmp_path)
        f_findings = [f for f in result.findings if f.finding_type == "FIX_NO_CLASS_F"]
        assert len(f_findings) == 1
        assert f_findings[0].severity == AuditSeverity.ERROR

    def test_autofix_claim_not_flagged(self, tmp_path: Path):
        """Claims mentioning 'auto-fix' (a feature name) should not trigger FIX_NO_CLASS_F."""
        body = MINIMAL_CLEAN_PACKET.replace(
            "1. Added a new feature to the system.",
            "1. Added auto-fix mode for COMMIT_PENDING and CLASS_E_NO_URL auto-remediation.",
        )
        _write_packet(tmp_path, "VERIFICATION_PACKET_AUTOFIX.md", body)
        auditor = PacketAuditor()
        result = auditor.audit(tmp_path)
        f_findings = [f for f in result.findings if f.finding_type == "FIX_NO_CLASS_F"]
        assert len(f_findings) == 0

    def test_fix_claim_with_class_f_passes(self, tmp_path: Path):
        body = MINIMAL_CLEAN_PACKET.replace(
            "1. Added a new feature to the system.",
            "1. Fixed authentication bypass vulnerability.",
        ).replace(
            "### Class A (Execution Evidence)",
            "### Class F (Provenance Evidence)\n\n"
            "**Claim 3: No tests weakened**\n"
            "- All assertions preserved.\n\n"
            "### Class A (Execution Evidence)",
        )
        _write_packet(tmp_path, "VERIFICATION_PACKET_OK.md", body)
        auditor = PacketAuditor()
        result = auditor.audit(tmp_path)
        f_findings = [f for f in result.findings if f.finding_type == "FIX_NO_CLASS_F"]
        assert len(f_findings) == 0


class TestAutoFix:
    """Test the --fix mode auto-remediation."""

    def test_fix_commit_pending(self, tmp_path: Path):
        body = MINIMAL_CLEAN_PACKET.replace("`abc1234`", "`pending`")
        p = _write_packet(tmp_path, "VERIFICATION_PACKET_PENDING.md", body)
        auditor = PacketAuditor()
        result = auditor.audit(tmp_path, fix=True)
        # Should have attempted fix (may not succeed without git, but logic runs)
        p.read_text(encoding="utf-8")
        # In a non-git context, commit SHA won't be found, so pending stays
        # Just verify the auditor didn't crash
        assert result.packets_scanned == 1

    def test_fix_class_e_local_ref(self, tmp_path: Path):
        body = MINIMAL_CLEAN_PACKET.replace(
            "- **Link:** [Test Spec](https://github.com/ImmortalDemonGod/aiv-protocol/blob/abc1234/SPECIFICATION.md)",
            "- **Link:** AUDIT_REPORT.md — Finding L01",
        )
        p = _write_packet(tmp_path, "VERIFICATION_PACKET_PLAINLINK.md", body)
        auditor = PacketAuditor()
        auditor.audit(tmp_path, fix=True)
        fixed_body = p.read_text(encoding="utf-8")
        # Should have converted to a URL (even without git, falls back to "main")
        assert "https://github.com/" in fixed_body
        assert "AUDIT_REPORT.md" in fixed_body


class TestMultipleFindings:
    """A single packet can have multiple issues."""

    def test_multiple_issues_all_reported(self, tmp_path: Path):
        body = (
            MINIMAL_CLEAN_PACKET.replace("`abc1234`", "`pending`")
            .replace(
                "1. Added a new feature to the system.",
                "1. TODO: Primary claim.",
            )
            .replace(
                "Added new feature per specification.",
                "TODO: One-line summary.",
            )
            .replace(
                'classified_by: "cascade"',
                'classified_by: "TODO"',
            )
        )
        _write_packet(tmp_path, "VERIFICATION_PACKET_MANY.md", body)
        auditor = PacketAuditor()
        result = auditor.audit(tmp_path)
        types = {f.finding_type for f in result.findings}
        assert "COMMIT_PENDING" in types
        assert "CLAIM_TODO" in types
        assert "SUMMARY_TODO" in types
        assert "CLASSIFIED_BY_TODO" in types
        assert result.packets_with_issues == 1


class TestAuditCLI:
    """Test the aiv audit CLI integration."""

    def test_audit_cli_runs(self, tmp_path: Path):
        """Verify the CLI command can be invoked via subprocess."""
        import subprocess
        import sys

        _write_packet(tmp_path, "VERIFICATION_PACKET_CLEAN.md", MINIMAL_CLEAN_PACKET)
        result = subprocess.run(
            [sys.executable, "-m", "aiv", "audit", str(tmp_path), "--no-evidence"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 0
        assert "Audit" in result.stdout

    def test_audit_cli_exits_1_on_errors(self, tmp_path: Path):
        """CLI exits 1 when ERROR-severity findings exist."""
        import subprocess
        import sys

        body = MINIMAL_CLEAN_PACKET.replace("`abc1234`", "`pending`")
        _write_packet(tmp_path, "VERIFICATION_PACKET_BAD.md", body)
        result = subprocess.run(
            [sys.executable, "-m", "aiv", "audit", str(tmp_path), "--no-evidence"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 1


# ---------------------------------------------------------------------------
# Git-history audit tests
# ---------------------------------------------------------------------------


class TestIsPacketPath:
    def test_standard_packet(self) -> None:
        auditor = PacketAuditor()
        assert auditor._is_packet_path(".github/aiv-packets/VERIFICATION_PACKET_FOO.md") is True

    def test_legacy_packet(self) -> None:
        auditor = PacketAuditor()
        assert auditor._is_packet_path(".github/VERIFICATION_PACKET_OLD.md") is True

    def test_not_a_packet(self) -> None:
        auditor = PacketAuditor()
        assert auditor._is_packet_path("README.md") is False
        assert auditor._is_packet_path("src/main.py") is False


class TestIsFunctionalPath:
    def test_src_functional(self) -> None:
        auditor = PacketAuditor()
        assert auditor._is_functional_path("src/aiv/cli/main.py") is True

    def test_tests_functional(self) -> None:
        auditor = PacketAuditor()
        assert auditor._is_functional_path("tests/unit/test_foo.py") is True

    def test_root_file_functional(self) -> None:
        auditor = PacketAuditor()
        assert auditor._is_functional_path("pyproject.toml") is True

    def test_docs_not_functional(self) -> None:
        auditor = PacketAuditor()
        assert auditor._is_functional_path("docs/guide.md") is False
        assert auditor._is_functional_path("README.md") is False

    def test_custom_prefixes_respected(self) -> None:
        """P0-4: _is_functional_path accepts custom prefixes from .aiv.yml."""
        auditor = PacketAuditor()
        custom_prefixes = ("backend/", "frontend/")
        custom_roots: set[str] = set()
        assert auditor._is_functional_path("backend/api.py", custom_prefixes, custom_roots) is True
        assert auditor._is_functional_path("frontend/app.ts", custom_prefixes, custom_roots) is True
        assert auditor._is_functional_path("src/main.py", custom_prefixes, custom_roots) is False

    def test_custom_root_files_respected(self) -> None:
        """
        Verify that _is_functional_path recognizes custom root filenames from configuration.
        
        Asserts that a filename present in the provided root set is treated as a functional path and a filename not in the set is not.
        """
        auditor = PacketAuditor()
        custom_prefixes: tuple[str, ...] = ()
        custom_roots = {"Makefile", "Dockerfile"}
        assert auditor._is_functional_path("Makefile", custom_prefixes, custom_roots) is True
        assert auditor._is_functional_path("pyproject.toml", custom_prefixes, custom_roots) is False


def _make_git_log_output(commits: list[tuple[str, list[str]]]) -> str:
    """
    Build a fake git log output using the format produced by `git log --format=%H --name-only`.
    
    Parameters:
        commits (list[tuple[str, list[str]]]): Sequence of commits where each item is a tuple
            (commit_sha, file_paths). `commit_sha` is the commit hash string; `file_paths`
            is a list of file path strings changed in that commit.
    
    Returns:
        str: A single string where each commit appears as the SHA on its own line followed by
        its file paths on separate lines, and commits are separated by a blank line.
    """
    parts = []
    for sha, files in commits:
        parts.append(sha)
        for f in files:
            parts.append(f)
        parts.append("")  # blank line separator
    return "\n".join(parts)


class TestAuditCommitsHookBypass:
    """Detect commits where functional files lack a verification packet."""

    def test_hook_bypass_detected(self, tmp_path: Path) -> None:
        fake_log = _make_git_log_output(
            [
                ("a" * 40, ["src/aiv/cli/main.py"]),
            ]
        )
        auditor = PacketAuditor()
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = fake_log
            result = auditor.audit_commits(tmp_path, num_commits=5)

        bypass = [f for f in result.findings if f.finding_type == "HOOK_BYPASS"]
        assert len(bypass) == 1
        assert bypass[0].severity == AuditSeverity.ERROR
        assert "main.py" in bypass[0].message

    def test_clean_commit_no_findings(self, tmp_path: Path) -> None:
        fake_log = _make_git_log_output(
            [
                (
                    "b" * 40,
                    [
                        "src/aiv/cli/main.py",
                        ".github/aiv-packets/VERIFICATION_PACKET_CLI.md",
                    ],
                ),
            ]
        )
        auditor = PacketAuditor()
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = fake_log
            result = auditor.audit_commits(tmp_path, num_commits=5)

        bypass = [f for f in result.findings if f.finding_type == "HOOK_BYPASS"]
        assert len(bypass) == 0

    def test_docs_only_skipped(self, tmp_path: Path) -> None:
        fake_log = _make_git_log_output(
            [
                ("c" * 40, ["README.md", "docs/guide.md"]),
            ]
        )
        auditor = PacketAuditor()
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = fake_log
            result = auditor.audit_commits(tmp_path, num_commits=5)

        assert len(result.findings) == 0


class TestAuditCommitsAtomicViolation:
    """Detect commits that bundle multiple functional files."""

    def test_multi_file_detected(self, tmp_path: Path) -> None:
        fake_log = _make_git_log_output(
            [
                (
                    "d" * 40,
                    [
                        "src/aiv/cli/main.py",
                        "src/aiv/lib/config.py",
                        "tests/unit/test_config.py",
                        ".github/aiv-packets/VERIFICATION_PACKET_CONFIG.md",
                    ],
                ),
            ]
        )
        auditor = PacketAuditor()
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = fake_log
            result = auditor.audit_commits(tmp_path, num_commits=5)

        atomic = [f for f in result.findings if f.finding_type == "ATOMIC_VIOLATION"]
        assert len(atomic) == 1
        assert atomic[0].severity == AuditSeverity.WARNING
        assert "3 functional files" in atomic[0].message

    def test_single_functional_no_violation(self, tmp_path: Path) -> None:
        fake_log = _make_git_log_output(
            [
                (
                    "e" * 40,
                    [
                        "src/aiv/cli/main.py",
                        ".github/aiv-packets/VERIFICATION_PACKET_CLI.md",
                    ],
                ),
            ]
        )
        auditor = PacketAuditor()
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = fake_log
            result = auditor.audit_commits(tmp_path, num_commits=5)

        atomic = [f for f in result.findings if f.finding_type == "ATOMIC_VIOLATION"]
        assert len(atomic) == 0


class TestAuditCommitsCombined:
    """Test that both HOOK_BYPASS and ATOMIC_VIOLATION fire on the same commit."""

    def test_bypass_and_violation_both_reported(self, tmp_path: Path) -> None:
        fake_log = _make_git_log_output(
            [
                (
                    "f" * 40,
                    [
                        "src/aiv/cli/main.py",
                        "src/aiv/lib/evidence_collector.py",
                        "tests/unit/test_evidence_collector.py",
                    ],
                ),
            ]
        )
        auditor = PacketAuditor()
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 0
            mock_run.return_value.stdout = fake_log
            result = auditor.audit_commits(tmp_path, num_commits=5)

        types = {f.finding_type for f in result.findings}
        assert "HOOK_BYPASS" in types
        assert "ATOMIC_VIOLATION" in types

    def test_git_failure_returns_empty(self, tmp_path: Path) -> None:
        auditor = PacketAuditor()
        with patch("subprocess.run") as mock_run:
            mock_run.return_value.returncode = 128
            mock_run.return_value.stdout = ""
            result = auditor.audit_commits(tmp_path, num_commits=5)

        assert len(result.findings) == 0
        assert result.packets_scanned == 0


# ---------------------------------------------------------------------------
# Evidence file auditing tests
# ---------------------------------------------------------------------------

CLEAN_EVIDENCE = """\
# AIV Evidence File (v1.0)

**File:** `src/auth.py`
**Commit:** `abc1234`
**Generated:** 2026-02-09T08:00:00Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "src/auth.py"
  classification_rationale: "Standard bug fix"
  classified_by: "alice"
  classified_at: "2026-02-09T08:00:00Z"
```

## Claim(s)

1. TokenValidator rejects expired tokens with 401
2. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/org/repo/blob/abc1234def/SPEC.md](https://github.com/org/repo/blob/abc1234def/SPEC.md)
- **Requirements Verified:** Section 4.2 requires token expiry handling

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`abc1234`](https://github.com/org/repo/tree/abc1234def))

- [`src/auth.py#L42-L58`](https://github.com/org/repo/blob/abc1234def/src/auth.py#L42-L58)

### Class A (Execution Evidence)

- pytest: 404 passed, 0 failed
- ruff: clean
- mypy: clean

---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence collected by `aiv commit` running: git diff, pytest (404 passed, 0 failed), ruff (clean), mypy (clean).

---

## Summary

Handle expired JWT tokens with proper 401 response
"""


def _write_evidence(directory: Path, name: str, body: str) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    p = directory / name
    p.write_text(body, encoding="utf-8")
    return p


class TestEvidenceAudit:
    """Tests for Layer 1 evidence file auditing."""

    def test_clean_evidence_no_findings(self, tmp_path: Path) -> None:
        packets_dir = tmp_path / "packets"
        packets_dir.mkdir()
        evidence_dir = tmp_path / "evidence"
        _write_evidence(evidence_dir, "EVIDENCE_AUTH.md", CLEAN_EVIDENCE)

        auditor = PacketAuditor()
        with patch("aiv.lib.auditor._get_introducing_commit", return_value="abc1234"):
            result = auditor.audit(packets_dir, evidence_dir=evidence_dir)

        assert result.packets_scanned == 1
        assert len(result.findings) == 0

    def test_mutable_class_e_link_detected(self, tmp_path: Path) -> None:
        body = CLEAN_EVIDENCE.replace(
            "blob/abc1234def/SPEC.md](https://github.com/org/repo/blob/abc1234def/SPEC.md)",
            "blob/main/SPEC.md](https://github.com/org/repo/blob/main/SPEC.md)",
        )
        packets_dir = tmp_path / "packets"
        packets_dir.mkdir()
        evidence_dir = tmp_path / "evidence"
        _write_evidence(evidence_dir, "EVIDENCE_AUTH.md", body)

        auditor = PacketAuditor()
        with patch("aiv.lib.auditor._get_introducing_commit", return_value="abc1234"):
            result = auditor.audit(packets_dir, evidence_dir=evidence_dir)

        types = {f.finding_type for f in result.findings}
        assert "EVIDENCE_MUTABLE_LINK" in types

    def test_tier_skip_detected(self, tmp_path: Path) -> None:
        """R1 + --skip-checks should be flagged as EVIDENCE_TIER_SKIP."""
        body = CLEAN_EVIDENCE.replace(
            "- pytest: 404 passed, 0 failed\n- ruff: clean\n- mypy: clean",
            "- Local checks skipped (--skip-checks).",
        )
        packets_dir = tmp_path / "packets"
        packets_dir.mkdir()
        evidence_dir = tmp_path / "evidence"
        _write_evidence(evidence_dir, "EVIDENCE_AUTH.md", body)

        auditor = PacketAuditor()
        with patch("aiv.lib.auditor._get_introducing_commit", return_value="abc1234"):
            result = auditor.audit(packets_dir, evidence_dir=evidence_dir)

        types = {f.finding_type for f in result.findings}
        assert "EVIDENCE_TIER_SKIP" in types

    def test_r0_skip_no_tier_skip_finding(self, tmp_path: Path) -> None:
        """R0 + --skip-checks should NOT produce EVIDENCE_TIER_SKIP."""
        body = (
            CLEAN_EVIDENCE.replace("risk_tier: R1", "risk_tier: R0")
            .replace(
                "- pytest: 404 passed, 0 failed\n- ruff: clean\n- mypy: clean",
                "- Local checks skipped (--skip-checks).\n- **Skip reason:** Docs only",
            )
            .replace(
                "Evidence collected by `aiv commit` running: git diff, pytest (404 passed, 0 failed), ruff (clean), mypy (clean).",
                "**R0 (trivial) -- local checks skipped.**\n**Reason:** Docs only\nOnly git diff scope inventory was collected. No execution evidence.",
            )
        )
        packets_dir = tmp_path / "packets"
        packets_dir.mkdir()
        evidence_dir = tmp_path / "evidence"
        _write_evidence(evidence_dir, "EVIDENCE_AUTH.md", body)

        auditor = PacketAuditor()
        with patch("aiv.lib.auditor._get_introducing_commit", return_value="abc1234"):
            result = auditor.audit(packets_dir, evidence_dir=evidence_dir)

        types = {f.finding_type for f in result.findings}
        assert "EVIDENCE_TIER_SKIP" not in types
        assert "EVIDENCE_THEATER" not in types

    def test_no_skip_reason_detected(self, tmp_path: Path) -> None:
        """--skip-checks without --skip-reason should be flagged."""
        body = (
            CLEAN_EVIDENCE.replace("risk_tier: R1", "risk_tier: R0")
            .replace(
                "- pytest: 404 passed, 0 failed\n- ruff: clean\n- mypy: clean",
                "- Local checks skipped (--skip-checks).",
            )
            .replace(
                "Evidence collected by `aiv commit` running: git diff, pytest (404 passed, 0 failed), ruff (clean), mypy (clean).",
                "**R0 (trivial) -- local checks skipped.**\nOnly git diff scope inventory was collected.",
            )
        )
        packets_dir = tmp_path / "packets"
        packets_dir.mkdir()
        evidence_dir = tmp_path / "evidence"
        _write_evidence(evidence_dir, "EVIDENCE_AUTH.md", body)

        auditor = PacketAuditor()
        with patch("aiv.lib.auditor._get_introducing_commit", return_value="abc1234"):
            result = auditor.audit(packets_dir, evidence_dir=evidence_dir)

        types = {f.finding_type for f in result.findings}
        assert "EVIDENCE_NO_SKIP_REASON" in types

    def test_theater_methodology_detected(self, tmp_path: Path) -> None:
        """Methodology claims tools ran but Class A says skipped -> EVIDENCE_THEATER."""
        body = CLEAN_EVIDENCE.replace(
            "- pytest: 404 passed, 0 failed\n- ruff: clean\n- mypy: clean",
            "- Local checks skipped (--skip-checks).",
        )
        # Methodology still claims tools ran (the lie)
        packets_dir = tmp_path / "packets"
        packets_dir.mkdir()
        evidence_dir = tmp_path / "evidence"
        _write_evidence(evidence_dir, "EVIDENCE_AUTH.md", body)

        auditor = PacketAuditor()
        with patch("aiv.lib.auditor._get_introducing_commit", return_value="abc1234"):
            result = auditor.audit(packets_dir, evidence_dir=evidence_dir)

        types = {f.finding_type for f in result.findings}
        assert "EVIDENCE_THEATER" in types

    def test_evidence_dir_none_skips_scan(self, tmp_path: Path) -> None:
        """evidence_dir=None should skip evidence scanning entirely."""
        packets_dir = tmp_path / "packets"
        packets_dir.mkdir()

        auditor = PacketAuditor()
        result = auditor.audit(packets_dir, evidence_dir=None)

        assert result.packets_scanned == 0
        assert len(result.findings) == 0

    def test_no_evidence_flag_skips_evidence(self, tmp_path: Path) -> None:
        """Passing a nonexistent evidence_dir should not crash."""
        packets_dir = tmp_path / "packets"
        packets_dir.mkdir()
        nonexistent = tmp_path / "does_not_exist"

        auditor = PacketAuditor()
        result = auditor.audit(packets_dir, evidence_dir=nonexistent)

        assert result.packets_scanned == 0

    def test_unverified_claim_flagged(self, tmp_path: Path) -> None:
        """EVIDENCE_UNVERIFIED_CLAIM fires for each FAIL UNVERIFIED in the matrix."""
        body = CLEAN_EVIDENCE.replace(
            "---\n\n## Verification Methodology",
            "## Claim Verification Matrix\n\n"
            "| # | Claim | Type | Evidence | Verdict |\n"
            "|---|-------|------|----------|---------|"
            "\n| 1 | TokenValidator rejects expired tokens | symbol | 3 tests call validate | PASS VERIFIED |"
            "\n| 2 | quickstart prints workflow | symbol | 0 tests call quickstart | FAIL UNVERIFIED |"
            "\n\n---\n\n## Verification Methodology",
        )
        packets_dir = tmp_path / "packets"
        packets_dir.mkdir()
        evidence_dir = tmp_path / "evidence"
        _write_evidence(evidence_dir, "EVIDENCE_AUTH.md", body)

        auditor = PacketAuditor()
        with patch("aiv.lib.auditor._get_introducing_commit", return_value="abc1234"):
            result = auditor.audit(packets_dir, evidence_dir=evidence_dir)

        unverified = [f for f in result.findings if f.finding_type == "EVIDENCE_UNVERIFIED_CLAIM"]
        assert len(unverified) == 1
        assert "Claim 2" in unverified[0].message

    def test_high_unverified_flagged(self, tmp_path: Path) -> None:
        """EVIDENCE_HIGH_UNVERIFIED fires when >50% of bindable claims are UNVERIFIED."""
        body = CLEAN_EVIDENCE.replace(
            "---\n\n## Verification Methodology",
            "## Claim Verification Matrix\n\n"
            "| # | Claim | Type | Evidence | Verdict |\n"
            "|---|-------|------|----------|---------|"
            "\n| 1 | init creates config | symbol | 0 tests call init | FAIL UNVERIFIED |"
            "\n| 2 | close generates packet | symbol | 0 tests call close | FAIL UNVERIFIED |"
            "\n| 3 | No tests deleted | structural | Class C clean | REVIEW MANUAL REVIEW |"
            "\n\n---\n\n## Verification Methodology",
        )
        packets_dir = tmp_path / "packets"
        packets_dir.mkdir()
        evidence_dir = tmp_path / "evidence"
        _write_evidence(evidence_dir, "EVIDENCE_AUTH.md", body)

        auditor = PacketAuditor()
        with patch("aiv.lib.auditor._get_introducing_commit", return_value="abc1234"):
            result = auditor.audit(packets_dir, evidence_dir=evidence_dir)

        types = {f.finding_type for f in result.findings}
        assert "EVIDENCE_HIGH_UNVERIFIED" in types
        high = [f for f in result.findings if f.finding_type == "EVIDENCE_HIGH_UNVERIFIED"][0]
        assert "2/2" in high.message
        assert "100%" in high.message

    def test_manual_review_flagged(self, tmp_path: Path) -> None:
        """EVIDENCE_MANUAL_REVIEW fires when claims need human review."""
        body = CLEAN_EVIDENCE.replace(
            "---\n\n## Verification Methodology",
            "## Claim Verification Matrix\n\n"
            "| # | Claim | Type | Evidence | Verdict |\n"
            "|---|-------|------|----------|---------|"
            "\n| 1 | TokenValidator rejects expired tokens | symbol | 3 tests | PASS VERIFIED |"
            "\n| 2 | Blocking message updated | unresolved | No binding | REVIEW MANUAL REVIEW |"
            "\n| 3 | No tests deleted | structural | Class C not collected | REVIEW MANUAL REVIEW |"
            "\n\n---\n\n## Verification Methodology",
        )
        packets_dir = tmp_path / "packets"
        packets_dir.mkdir()
        evidence_dir = tmp_path / "evidence"
        _write_evidence(evidence_dir, "EVIDENCE_AUTH.md", body)

        auditor = PacketAuditor()
        with patch("aiv.lib.auditor._get_introducing_commit", return_value="abc1234"):
            result = auditor.audit(packets_dir, evidence_dir=evidence_dir)

        manual = [f for f in result.findings if f.finding_type == "EVIDENCE_MANUAL_REVIEW"]
        assert len(manual) == 1
        assert "2 claim(s)" in manual[0].message

    def test_all_verified_no_claim_findings(self, tmp_path: Path) -> None:
        """All PASS VERIFIED claims should produce zero claim-level findings."""
        body = CLEAN_EVIDENCE.replace(
            "---\n\n## Verification Methodology",
            "## Claim Verification Matrix\n\n"
            "| # | Claim | Type | Evidence | Verdict |\n"
            "|---|-------|------|----------|---------|"
            "\n| 1 | TokenValidator rejects expired tokens | symbol | 3 tests | PASS VERIFIED |"
            "\n| 2 | No tests deleted | structural | Class C clean | PASS VERIFIED |"
            "\n\n---\n\n## Verification Methodology",
        )
        packets_dir = tmp_path / "packets"
        packets_dir.mkdir()
        evidence_dir = tmp_path / "evidence"
        _write_evidence(evidence_dir, "EVIDENCE_AUTH.md", body)

        auditor = PacketAuditor()
        with patch("aiv.lib.auditor._get_introducing_commit", return_value="abc1234"):
            result = auditor.audit(packets_dir, evidence_dir=evidence_dir)

        claim_findings = [
            f
            for f in result.findings
            if f.finding_type in ("EVIDENCE_UNVERIFIED_CLAIM", "EVIDENCE_HIGH_UNVERIFIED", "EVIDENCE_MANUAL_REVIEW")
        ]
        assert len(claim_findings) == 0

    def test_commit_pending_in_evidence(self, tmp_path: Path) -> None:
        body = CLEAN_EVIDENCE.replace("`abc1234`", "`pending`")
        packets_dir = tmp_path / "packets"
        packets_dir.mkdir()
        evidence_dir = tmp_path / "evidence"
        _write_evidence(evidence_dir, "EVIDENCE_AUTH.md", body)

        auditor = PacketAuditor()
        with patch("aiv.lib.auditor._get_introducing_commit", return_value="abc1234"):
            result = auditor.audit(packets_dir, evidence_dir=evidence_dir)

        types = {f.finding_type for f in result.findings}
        assert "COMMIT_PENDING" in types