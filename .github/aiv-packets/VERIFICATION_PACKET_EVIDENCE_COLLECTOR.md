# AIV Verification Packet (v2.1)

**Commit:** `cf3639c`
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R2
  sod_mode: S1
  critical_surfaces: []
  blast_radius: "src/aiv/lib/evidence_collector.py"
  classification_rationale: "New module replacing template-based evidence generation with tool-based evidence collection"
  classified_by: "ImmortalDemonGod"
  classified_at: "2026-02-09T01:15:51Z"
```

## Claim(s)

1. Class B evidence is collected from git diff --cached line ranges as SHA-pinned permalinks
2. Class A evidence runs pytest and extracts specific test names covering the changed file
3. Class C evidence scans the diff for deleted assertions, deleted test files, and added skip markers
4. Class F evidence scans test file integrity from git diff
5. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/aiv-protocol/blob/cf3639c/SPECIFICATION.md](https://github.com/ImmortalDemonGod/aiv-protocol/blob/cf3639c/SPECIFICATION.md)
- **Requirements Verified:** See linked spec/issue.

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`cf3639c`](https://github.com/ImmortalDemonGod/aiv-protocol/tree/cf3639c6b4658d0d271061cee31f523a1834a5cf))

- [`src/aiv/lib/evidence_collector.py#L1-L341`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/cf3639c6b4658d0d271061cee31f523a1834a5cf/src/aiv/lib/evidence_collector.py#L1-L341)

### Class A (Execution Evidence)

- **pytest:** 503 passed, 0 failed in 36.56s
- **WARNING:** No tests found that directly import or reference the changed file.
- **ruff:** All checks passed
- **mypy:** Success: no issues found in 1 source file

### Class C (Negative Evidence)

**Search methodology:** Ran `git diff --cached` and scanned for regression indicators.

- Test file deletions: **none**
- Test file modifications: **none**
- Deleted assertions (`assert` removals in diff): **none found**
- Added skip markers (`@pytest.mark.skip`, `@unittest.skip`): **none found**

### Class F (Provenance Evidence)

- No test files deleted. No assertions removed. Full test suite passes.

---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence was collected by `aiv commit` running: git diff, pytest -v, ruff, mypy, anti-cheat scan.

---

## Summary

Evidence collector: Class B from git diff hunks, Class A from pytest -v, Class C from anti-cheat scan, Class F from test file integrity
