# AIV Verification Packet (v2.1)

## Classification

- **Risk Tier:** R2
- **Blast Radius:** tooling
- **SoD Mode:** S0

## Claim(s)

1. Pre-commit hook safety snapshot replaces tar archive with portable file copy loop that works on Windows where tar is unavailable. Copy failure is fatal (exit 1) because snapshot integrity is critical.

## Evidence

### Class E (Intent Alignment)

- **Link:** [Hook source](https://github.com/ImmortalDemonGod/aiv-protocol/blob/b25af40/.husky/pre-commit)
- **Requirements Verified:**
  1. Untracked files are copied into snapshot directory preserving relative paths.
  2. Copy failure blocks the commit (safety-critical).
  3. No external tool dependency (cp/mkdir only).

### Class B (Referential Evidence)

**Scope Inventory**
- Modified: .husky/pre-commit

### Class A (Execution Evidence)

- Tested with untracked file present: snapshot directory contains copied file with correct path structure.
- Commits proceed normally after successful snapshot.

## Summary

Replaces tar (unavailable on Windows) with cp loop for untracked file snapshots. This is safety-critical — the snapshot has previously prevented data loss from AI-caused deletions.
