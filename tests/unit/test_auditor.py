"""
tests/unit/test_auditor.py

Unit tests for the PacketAuditor — verifies detection of quality issues
that the validation pipeline does not catch.
"""

import pytest
from pathlib import Path

from aiv.lib.auditor import PacketAuditor, AuditSeverity


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
            f for f in result.findings
            if f.finding_type in ("CLASS_E_NO_URL", "CLASS_E_MUTABLE", "CLASS_E_EMPTY")
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
        fixed_body = p.read_text(encoding="utf-8")
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
        result = auditor.audit(tmp_path, fix=True)
        fixed_body = p.read_text(encoding="utf-8")
        # Should have converted to a URL (even without git, falls back to "main")
        assert "https://github.com/" in fixed_body
        assert "AUDIT_REPORT.md" in fixed_body


class TestMultipleFindings:
    """A single packet can have multiple issues."""

    def test_multiple_issues_all_reported(self, tmp_path: Path):
        body = MINIMAL_CLEAN_PACKET.replace("`abc1234`", "`pending`").replace(
            "1. Added a new feature to the system.",
            "1. TODO: Primary claim.",
        ).replace(
            "Added new feature per specification.",
            "TODO: One-line summary.",
        ).replace(
            'classified_by: "cascade"',
            'classified_by: "TODO"',
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
            [sys.executable, "-m", "aiv", "audit", str(tmp_path)],
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
            [sys.executable, "-m", "aiv", "audit", str(tmp_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert result.returncode == 1
