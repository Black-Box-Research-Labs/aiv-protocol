# AIV Verification Packet (v2.1)

## Classification

```yaml
classification:
  risk_tier: R0
  blast_radius: local
  sod_mode: S0
  critical_surfaces: []
  classification_rationale: "Tooling script — generates a read-only mapping report from git history. No runtime effect on validation pipeline or guard."
  classified_by: "cascade-ai"
  classified_at: "2026-02-07T07:05:00Z"
```

## Claim(s)

1. `scripts/map_packets.py` parses all git commits and produces a bidirectional mapping of source files to verification packets, output as `FILE_PACKET_MAP.json` and `FILE_PACKET_MAP.md`.
2. The script correctly distinguishes packet-only commits, source-only commits, and mixed commits — reporting truly unmapped items only when they never co-occur with a counterpart across the entire history.

## Evidence

### Class B (Referential Evidence)

**Scope Inventory**

- Created:
  - `scripts/map_packets.py`
  - `FILE_PACKET_MAP.json` (generated output)
  - `FILE_PACKET_MAP.md` (generated output)

### Class A (Execution Evidence)

- Execution output:
  ```
  Analyzed 279 commits
  Mapped 66 source files to 87 packets
  Unmapped source files: 9
  Unmapped packets: 3
  ```
- 9 unmapped source files are all documentation (README, SPECIFICATION, CHANGELOG, LICENSE, docs/).
- 3 unmapped packets are structural/meta (TEMPLATE, GITKEEP, AIV_IMPLEMENTATION consolidation).
- Execution environment: Windows, Python 3.x, git CLI.

## Summary

Adds a rerunnable script that analyzes git commit history to produce a full source-file-to-verification-packet mapping, covering 66 source files across 87 packets from 279 commits.
