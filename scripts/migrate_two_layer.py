#!/usr/bin/env python3
"""
scripts/migrate_two_layer.py

Migration script for Two-Layer Verification Architecture.

What this does:
  1. Creates .github/aiv-evidence/ directory
  2. Copies existing VERIFICATION_PACKET_*.md files to EVIDENCE_*.md in aiv-evidence/
  3. Leaves originals in .github/aiv-packets/ untouched (they remain as legacy Layer 2 packets)
  4. Prints a summary of what was migrated

What this does NOT do:
  - Does NOT delete any files
  - Does NOT run git commands (you stage/commit manually)
  - Does NOT modify any existing packet content

Usage:
  python scripts/migrate_two_layer.py           # Dry run (default)
  python scripts/migrate_two_layer.py --apply   # Actually copy files
"""

from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path


PACKETS_DIR = Path(".github/aiv-packets")
EVIDENCE_DIR = Path(".github/aiv-evidence")

# These are aggregate/meta packets that should NOT become evidence files.
# They cover multiple files or are about the project as a whole.
SKIP_PATTERNS = [
    "VERIFICATION_PACKET_TEMPLATE.md",
    "VERIFICATION_PACKET_AIV_IMPLEMENTATION.md",
    "VERIFICATION_PACKET_AIV_GUARD.md",
]


def normalize_name(packet_name: str) -> str:
    """Convert VERIFICATION_PACKET_FOO.md -> EVIDENCE_FOO.md"""
    # Strip prefix and suffix
    name = packet_name
    if name.startswith("VERIFICATION_PACKET_"):
        name = name[len("VERIFICATION_PACKET_"):]
    if name.endswith(".md"):
        name = name[:-3]
    return f"EVIDENCE_{name}.md"


def main() -> int:
    parser = argparse.ArgumentParser(description="Migrate to Two-Layer Architecture")
    parser.add_argument("--apply", action="store_true", help="Actually perform the migration (default: dry run)")
    args = parser.parse_args()

    if not PACKETS_DIR.exists():
        print(f"ERROR: {PACKETS_DIR} not found. Run from repo root.")
        return 1

    # Find all verification packets
    packets = sorted(PACKETS_DIR.glob("VERIFICATION_PACKET_*.md"))
    if not packets:
        print("No VERIFICATION_PACKET_*.md files found.")
        return 0

    print(f"Found {len(packets)} verification packet(s) in {PACKETS_DIR}/")
    print()

    # Categorize
    to_migrate: list[tuple[Path, str]] = []
    skipped: list[str] = []

    for packet in packets:
        if packet.name in SKIP_PATTERNS:
            skipped.append(packet.name)
            continue
        evidence_name = normalize_name(packet.name)
        to_migrate.append((packet, evidence_name))

    # Print plan
    print(f"Will migrate: {len(to_migrate)} file(s)")
    print(f"Will skip:    {len(skipped)} file(s) (meta/aggregate packets)")
    print()

    if skipped:
        print("SKIPPED (remain as Layer 2 packets only):")
        for s in skipped:
            print(f"  {s}")
        print()

    print("MIGRATION PLAN:")
    print(f"  Source: {PACKETS_DIR}/VERIFICATION_PACKET_*.md")
    print(f"  Target: {EVIDENCE_DIR}/EVIDENCE_*.md")
    print()

    for packet_path, evidence_name in to_migrate[:10]:
        print(f"  {packet_path.name}")
        print(f"    -> {evidence_name}")
    if len(to_migrate) > 10:
        print(f"  ... and {len(to_migrate) - 10} more")
    print()

    if not args.apply:
        print("DRY RUN — no files were changed.")
        print("Run with --apply to perform the migration.")
        return 0

    # Execute migration
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=True)

    # Create .gitkeep
    gitkeep = EVIDENCE_DIR / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.touch()

    migrated = 0
    conflicts = 0

    for packet_path, evidence_name in to_migrate:
        target = EVIDENCE_DIR / evidence_name
        if target.exists():
            print(f"  CONFLICT: {target} already exists, skipping")
            conflicts += 1
            continue

        shutil.copy2(packet_path, target)
        migrated += 1

    print()
    print(f"Migration complete: {migrated} file(s) copied, {conflicts} conflict(s) skipped.")
    print()
    print("Next steps:")
    print(f"  1. Review the files in {EVIDENCE_DIR}/")
    print(f"  2. git add {EVIDENCE_DIR}/")
    print("  3. git commit -m 'refactor(aiv): migrate evidence files to .github/aiv-evidence/'")
    print()
    print("The original packets in .github/aiv-packets/ are preserved.")
    print("They serve as legacy Layer 2 packets until new ones are generated via `aiv close`.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
