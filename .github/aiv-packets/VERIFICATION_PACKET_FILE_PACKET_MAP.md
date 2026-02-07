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
3. The script detects ghost packets (deleted from disk but present in git history) and deleted source files (relocated or removed), partitioning them into separate sections so live mapping counts are accurate.

## Evidence

### Class E (Intent Alignment)

- **Directive:** Provide traceability between source files and their verification packets across the entire commit history, enabling coverage analysis and gap detection.

### Class B (Referential Evidence)

**Scope Inventory**

- Created:
  - `scripts/map_packets.py`
  - `FILE_PACKET_MAP.json` (generated output)
  - `FILE_PACKET_MAP.md` (generated output)

### Class A (Execution Evidence)

- Execution output:
  ```
  Analyzed 291 commits
  Mapped 56 live source files to 62 live packets
  Unmapped source files: 11
  Unmapped packets: 3
  Ghost packets (deleted from disk): 27
  Deleted source files: 11
  ```
- 27 ghost packets correctly identified (all consolidated into AIV_IMPLEMENTATION).
- 11 deleted source files correctly identified (7 src/svp/ relocated, 4 dead modules removed).
- Execution environment: Windows, Python 3.x, git CLI.

## Summary

Rerunnable script mapping source files to verification packets from git history. Now detects ghost packets and deleted files, reporting 56 live source files across 62 live packets from 291 commits.
