# AIV Evidence File (v1.0)

**File:** `tests/unit/test_evidence_collector.py`
**Commit:** `cbfdd24`
**Previous:** `033974b`
**Generated:** 2026-02-09T19:37:55Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R0
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "tests/unit/test_evidence_collector.py"
  classification_rationale: "Test file: tests ARE the evidence, no execution proof needed"
  classified_by: "ImmortalDemonGod"
  classified_at: "2026-02-09T19:37:55Z"
```

## Claim(s)

1. TestCallVisitorSubprocessDetection verifies _CallVisitor detects aiv CLI commands from subprocess.run and list literals
2. test_subprocess_cli_test_detected verifies find_covering_tests matches subprocess-invoked CLI commands
3. test_subprocess_cli_via_helper_detected verifies helper indirection propagates CLI commands to test functions
4. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/aiv-protocol/blob/cbfdd242419b51b4a32f60fc3c6fa6e832bc25f1/docs/CLAIM_AWARE_EVIDENCE_PLAN.md](https://github.com/ImmortalDemonGod/aiv-protocol/blob/cbfdd242419b51b4a32f60fc3c6fa6e832bc25f1/docs/CLAIM_AWARE_EVIDENCE_PLAN.md)
- **Requirements Verified:** Theater Gap 2: AST binding tests must cover subprocess CLI detection to prevent regression

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`cbfdd24`](https://github.com/ImmortalDemonGod/aiv-protocol/tree/cbfdd242419b51b4a32f60fc3c6fa6e832bc25f1))

- [`tests/unit/test_evidence_collector.py#L490-L548`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/cbfdd242419b51b4a32f60fc3c6fa6e832bc25f1/tests/unit/test_evidence_collector.py#L490-L548)
- [`tests/unit/test_evidence_collector.py#L609-L650`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/cbfdd242419b51b4a32f60fc3c6fa6e832bc25f1/tests/unit/test_evidence_collector.py#L609-L650)

### Class A (Execution Evidence)

- Local checks skipped (--skip-checks).
- **Skip reason:** Test files are the verification evidence, not the subject of verification


---

## Verification Methodology

**R0 (trivial) -- local checks skipped.**
**Reason:** Test files are the verification evidence, not the subject of verification
Only git diff scope inventory was collected. No execution evidence.

---

## Summary

Add 5 tests for subprocess-based CLI detection in AST binding
