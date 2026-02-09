"""
tests/unit/test_parser.py

Unit tests for PacketParser — classification parsing, evidence collection,
methodology extraction, and evidence enrichment.
"""

import pytest

from aiv.lib.models import EvidenceClass, RiskTier
from aiv.lib.parser import PacketParser


class TestClassificationParsing:
    """Tests for _parse_classification() and risk_tier extraction."""

    @pytest.fixture
    def parser(self):
        return PacketParser()

    def _make_packet(self, classification_block: str) -> str:
        """Helper: build a minimal packet with a given classification block."""
        return f"""\
# AIV Verification Packet (v2.1)

{classification_block}

## Claim(s)

1. Test claim with enough characters to pass validation checks easily.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [Spec](https://github.com/o/r/blob/abc1234/docs/spec.md)
- **Requirements Verified:**
  1. Requirement met

### Class B (Referential Evidence)

**Scope Inventory (required)**

- Modified:
  - `src/file.py`

---

## Summary

Test packet.
"""

    def test_parses_r0(self, parser):
        packet = parser.parse(
            self._make_packet("## Classification (required)\n\n```yaml\nclassification:\n  risk_tier: R0\n```")
        )
        assert packet.risk_tier == RiskTier.R0

    def test_parses_r1(self, parser):
        packet = parser.parse(
            self._make_packet("## Classification (required)\n\n```yaml\nclassification:\n  risk_tier: R1\n```")
        )
        assert packet.risk_tier == RiskTier.R1

    def test_parses_r2(self, parser):
        packet = parser.parse(
            self._make_packet("## Classification (required)\n\n```yaml\nclassification:\n  risk_tier: R2\n```")
        )
        assert packet.risk_tier == RiskTier.R2

    def test_parses_r3(self, parser):
        packet = parser.parse(
            self._make_packet("## Classification (required)\n\n```yaml\nclassification:\n  risk_tier: R3\n```")
        )
        assert packet.risk_tier == RiskTier.R3

    def test_missing_classification_returns_none(self, parser):
        packet = parser.parse(self._make_packet(""))
        assert packet.risk_tier is None

    def test_classification_without_risk_tier_returns_none(self, parser):
        packet = parser.parse(
            self._make_packet("## Classification (required)\n\n```yaml\nclassification:\n  sod_mode: S0\n```")
        )
        assert packet.risk_tier is None

    def test_case_insensitive_risk_tier(self, parser):
        packet = parser.parse(
            self._make_packet("## Classification (required)\n\n```yaml\nclassification:\n  risk_tier: r2\n```")
        )
        assert packet.risk_tier == RiskTier.R2


class TestEvidenceClassCollection:
    """Tests for _collect_evidence_classes() and evidence_classes_present."""

    @pytest.fixture
    def parser(self):
        return PacketParser()

    def test_collects_all_evidence_sections(self, parser):
        packet_text = """\
# AIV Verification Packet (v2.1)

## Claim(s)

1. Test claim with sufficient description length for validation.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [Spec](https://github.com/o/r/blob/abc1234/docs/spec.md)
- **Requirements Verified:**
  1. Done

### Class B (Referential Evidence)

**Scope Inventory (required)**
- Modified: `src/file.py`

### Class A (Execution Evidence)

- CI Run passed

### Class C (Negative Evidence)

- No regressions found

### Class F (Provenance Evidence)

- No tests modified or deleted

---

## Summary

Test.
"""
        packet = parser.parse(packet_text)
        assert EvidenceClass.EXECUTION in packet.evidence_classes_present
        assert EvidenceClass.REFERENTIAL in packet.evidence_classes_present
        assert EvidenceClass.NEGATIVE in packet.evidence_classes_present
        assert EvidenceClass.INTENT in packet.evidence_classes_present
        assert EvidenceClass.PROVENANCE in packet.evidence_classes_present

    def test_intent_always_present(self, parser):
        """Class E should always be in evidence_classes_present if packet parses."""
        packet_text = """\
# AIV Verification Packet (v2.1)

## Claim(s)

1. Minimal claim with enough text to pass the minimum length requirement.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [Spec](https://github.com/o/r/blob/abc1234/docs/spec.md)
- **Requirements Verified:**
  1. Done

---

## Summary

Test.
"""
        packet = parser.parse(packet_text)
        assert EvidenceClass.INTENT in packet.evidence_classes_present


class TestMethodologyExtraction:
    """Tests for Verification Methodology extraction as reproduction field."""

    @pytest.fixture
    def parser(self):
        return PacketParser()

    def test_methodology_extracted_as_reproduction(self, parser):
        packet_text = """\
# AIV Verification Packet (v2.1)

## Claim(s)

1. Test claim with sufficient description length for validation checks.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [Spec](https://github.com/o/r/blob/abc1234/docs/spec.md)
- **Requirements Verified:**
  1. Done

### Class B (Referential Evidence)

**Scope Inventory (required)**
- Modified: `src/file.py`

---

## Verification Methodology

Visual inspection of code changes.

---

## Summary

Test.
"""
        packet = parser.parse(packet_text)
        assert "Visual inspection" in packet.claims[0].reproduction

    def test_missing_methodology_defaults_to_na(self, parser):
        packet_text = """\
# AIV Verification Packet (v2.1)

## Claim(s)

1. Test claim with sufficient description length for validation checks.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [Spec](https://github.com/o/r/blob/abc1234/docs/spec.md)
- **Requirements Verified:**
  1. Done

---

## Summary

Test.
"""
        packet = parser.parse(packet_text)
        assert packet.claims[0].reproduction == "N/A"


class TestFencedCodeBlockHeadingInjection:
    """Regression test: headings inside fenced code blocks must not be parsed as sections."""

    @pytest.fixture
    def parser(self):
        return PacketParser()

    def test_heading_inside_backtick_fence_ignored(self, parser):
        """## inside ```...``` must not create a new section."""
        packet_text = """\
# AIV Verification Packet (v2.1)

## Claim(s)

1. Parser handles fenced code blocks correctly and does not split on internal headings.

## Evidence

### Class E (Intent Alignment)

- **Link:** [Spec](https://github.com/o/r/blob/abc1234567890abc1234567890abc1234567890a/docs/spec.md)
- **Requirements Verified:**
  1. Headings inside code blocks are not treated as sections.

### Class B (Referential Evidence)

**Scope Inventory**
- Modified: src/parser.py

```python
## This heading should NOT be parsed as a section
def foo():
    pass
```

## Summary

Parser correctly ignores headings inside code blocks.
"""
        sections = parser._extract_sections(packet_text)
        titles = [s.title for s in sections]
        assert "This heading should NOT be parsed as a section" not in titles
        # Should have: header, Claim(s), Evidence, Class E, Class B, Summary = 6
        heading_titles = {s.title for s in sections}
        assert "Claim(s)" in heading_titles
        assert "Summary" in heading_titles

    def test_heading_inside_tilde_fence_ignored(self, parser):
        """## inside ~~~...~~~ must not create a new section."""
        packet_text = """\
# AIV Verification Packet (v2.1)

## Claim(s)

1. Parser handles tilde fenced code blocks correctly without splitting on headings.

## Evidence

### Class E (Intent Alignment)

- **Link:** [Spec](https://github.com/o/r/blob/abc1234567890abc1234567890abc1234567890a/docs/spec.md)
- **Requirements Verified:**
  1. Headings inside tilde fences are not treated as sections.

~~~
## Injected heading inside tilde fence
~~~

## Summary

Done.
"""
        sections = parser._extract_sections(packet_text)
        titles = [s.title for s in sections]
        assert "Injected heading inside tilde fence" not in titles

    def test_nested_fence_markers_handled(self, parser):
        """````...```` (4-backtick fence) should not be broken by ``` inside."""
        packet_text = """\
# AIV Verification Packet (v2.1)

## Claim(s)

1. Nested fences handled correctly without spurious sections being created by inner markers.

## Evidence

### Class E (Intent Alignment)

- **Link:** [Spec](https://github.com/o/r/blob/abc1234567890abc1234567890abc1234567890a/docs/spec.md)
- **Requirements Verified:**
  1. Nested fences work.

````markdown
```python
## This is deeply nested and must not be a section
```
````

## Summary

Done.
"""
        sections = parser._extract_sections(packet_text)
        titles = [s.title for s in sections]
        assert "This is deeply nested and must not be a section" not in titles


class TestEvidenceRefsTable:
    """Tests for Layer 2 evidence references table parsing."""

    @pytest.fixture
    def parser(self):
        return PacketParser()

    def test_evidence_refs_table_extracts_classes(self, parser):
        """Layer 2 packet with evidence refs table should populate evidence_classes_present."""
        packet_text = """\
# AIV Verification Packet (v2.2)

## Claim(s)

1. Changes to src/aiv/lib/change.py are verified by collected evidence.
2. No existing tests were modified or deleted during this change.

---

## Evidence References

| # | Evidence File | Commit SHA | Classes |
|---|---------------|------------|---------|
| 1 | EVIDENCE_LIB_CHANGE.md | `88ea4b4` | A, B |
| 2 | EVIDENCE_CLI_MAIN.md | `38c2c0c` | A, B, C |

### Class E (Intent Alignment)

- **Link:** [Design doc](https://github.com/o/r/blob/abc1234567890abc1234567890abc1234567890a/docs/design.md)
- **Requirements Verified:** Design doc section 7

---

## Summary

Test.
"""
        packet = parser.parse(packet_text)
        assert EvidenceClass.EXECUTION in packet.evidence_classes_present      # A
        assert EvidenceClass.REFERENTIAL in packet.evidence_classes_present     # B
        assert EvidenceClass.NEGATIVE in packet.evidence_classes_present        # C
        assert EvidenceClass.INTENT in packet.evidence_classes_present          # E

    def test_evidence_refs_table_no_classes_column(self, parser):
        """Table without Classes column should not crash."""
        content = [
            "| # | Evidence File | Commit SHA |",
            "|---|---------------|------------|",
            "| 1 | EVIDENCE_FOO.md | `abc1234` |",
        ]
        result = parser._parse_evidence_refs_table(content)
        assert result == set()

    def test_evidence_refs_table_all_classes(self, parser):
        """Table with all 6 classes should extract them all."""
        content = [
            "| # | Evidence File | Classes |",
            "|---|---------------|---------|",
            "| 1 | EV_1.md | A, B, C |",
            "| 2 | EV_2.md | D, E, F |",
        ]
        result = parser._parse_evidence_refs_table(content)
        assert result == {
            EvidenceClass.EXECUTION,
            EvidenceClass.REFERENTIAL,
            EvidenceClass.NEGATIVE,
            EvidenceClass.DIFFERENTIAL,
            EvidenceClass.INTENT,
            EvidenceClass.PROVENANCE,
        }
