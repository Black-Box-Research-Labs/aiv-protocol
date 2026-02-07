#!/usr/bin/env python3
"""Map source files to verification packets by analyzing git commit history.

For each commit that contains a VERIFICATION_PACKET_*.md file alongside
other changed files, we record the association. The output is a JSON
mapping and a Markdown report.
"""

import json
import subprocess
import sys
from collections import defaultdict
from pathlib import Path

PACKET_PREFIX = ".github/aiv-packets/VERIFICATION_PACKET_"
PACKET_SUFFIX = ".md"

# Files/dirs to exclude from the "source file" side of the mapping
EXCLUDE_PREFIXES = (
    ".github/aiv-packets/",
    ".svp/",
)
EXCLUDE_FILES = {
    ".github/aiv-packets/.gitkeep",
}


def get_commits_with_files() -> list[dict]:
    """Return list of {sha, subject, files} dicts from git log."""
    # Use %x00 as record separator, %x01 as field separator
    fmt = "%H%x01%s"
    result = subprocess.run(
        ["git", "log", "--pretty=format:" + fmt, "--name-only"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        print(f"git log failed: {result.stderr}", file=sys.stderr)
        sys.exit(1)

    commits = []
    current = None
    for line in result.stdout.splitlines():
        if "\x01" in line:
            # New commit header
            if current:
                commits.append(current)
            sha, subject = line.split("\x01", 1)
            current = {"sha": sha.strip(), "subject": subject.strip(), "files": []}
        elif line.strip() and current is not None:
            current["files"].append(line.strip())

    if current:
        commits.append(current)

    return commits


def is_packet(path: str) -> bool:
    return path.startswith(PACKET_PREFIX) and path.endswith(PACKET_SUFFIX)


def is_source_file(path: str) -> bool:
    if any(path.startswith(p) for p in EXCLUDE_PREFIXES):
        return False
    if path in EXCLUDE_FILES:
        return False
    return True


def packet_name(path: str) -> str:
    """Extract short packet name, e.g. VERIFICATION_PACKET_FOO.md -> FOO"""
    name = path.replace(".github/aiv-packets/VERIFICATION_PACKET_", "")
    return name.replace(".md", "")


def build_mapping(commits: list[dict]) -> dict:
    """Build source_file -> [packet_info] mapping."""
    file_to_packets: dict[str, list[dict]] = defaultdict(list)
    packet_to_files: dict[str, list[dict]] = defaultdict(list)
    all_source_files: set[str] = set()
    all_packets_seen: set[str] = set()

    for commit in commits:
        packets_in_commit = [f for f in commit["files"] if is_packet(f)]
        sources_in_commit = [f for f in commit["files"] if is_source_file(f)]

        # Track all source files and all packets seen across all commits
        for src in sources_in_commit:
            all_source_files.add(src)
        for pkt in packets_in_commit:
            all_packets_seen.add(packet_name(pkt))

        if packets_in_commit and sources_in_commit:
            for src in sources_in_commit:
                for pkt in packets_in_commit:
                    pname = packet_name(pkt)
                    entry = {
                        "packet": pname,
                        "packet_path": pkt,
                        "commit": commit["sha"][:7],
                        "subject": commit["subject"],
                    }
                    # Avoid duplicates
                    if not any(
                        e["packet"] == pname and e["commit"] == entry["commit"]
                        for e in file_to_packets[src]
                    ):
                        file_to_packets[src].append(entry)

                    src_entry = {
                        "file": src,
                        "commit": commit["sha"][:7],
                        "subject": commit["subject"],
                    }
                    if not any(
                        e["file"] == src and e["commit"] == src_entry["commit"]
                        for e in packet_to_files[pname]
                    ):
                        packet_to_files[pname].append(src_entry)

    # Unmapped = files/packets that NEVER got a mapping across any commit
    unmapped_files = all_source_files - set(file_to_packets.keys())
    unmapped_packets = all_packets_seen - set(packet_to_files.keys())

    return {
        "file_to_packets": dict(file_to_packets),
        "packet_to_files": dict(packet_to_files),
        "unmapped_files": sorted(unmapped_files),
        "unmapped_packets": sorted(unmapped_packets),
    }


def write_markdown_report(mapping: dict, path: Path) -> None:
    f2p = mapping["file_to_packets"]
    p2f = mapping["packet_to_files"]
    unmapped_files = mapping["unmapped_files"]
    unmapped_packets = mapping["unmapped_packets"]

    lines = []
    lines.append("# Source File ↔ Verification Packet Mapping")
    lines.append("")
    lines.append("Auto-generated from git commit history.")
    lines.append("")

    # Summary stats
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- **Mapped source files:** {len(f2p)}")
    lines.append(f"- **Mapped packets:** {len(p2f)}")
    lines.append(f"- **Unmapped source files:** {len(unmapped_files)}")
    lines.append(f"- **Unmapped packets (packet-only commits):** {len(unmapped_packets)}")
    lines.append("")

    # Section 1: Source files → packets
    lines.append("## Source Files → Verification Packets")
    lines.append("")

    # Group by directory
    dirs: dict[str, list[str]] = defaultdict(list)
    for filepath in sorted(f2p.keys()):
        parent = str(Path(filepath).parent)
        dirs[parent].append(filepath)

    for dirpath in sorted(dirs.keys()):
        lines.append(f"### `{dirpath}/`")
        lines.append("")
        lines.append("| Source File | Packet(s) | Commit(s) |")
        lines.append("|---|---|---|")
        for filepath in sorted(dirs[dirpath]):
            fname = Path(filepath).name
            packets = f2p[filepath]
            pkt_names = ", ".join(sorted(set(p["packet"] for p in packets)))
            commits = ", ".join(sorted(set(f'`{p["commit"]}`' for p in packets)))
            lines.append(f"| `{fname}` | {pkt_names} | {commits} |")
        lines.append("")

    # Section 2: Packets → source files
    lines.append("## Verification Packets → Source Files")
    lines.append("")
    lines.append("| Packet | Source File(s) | Commit(s) |")
    lines.append("|---|---|---|")
    for pname in sorted(p2f.keys()):
        files_list = p2f[pname]
        fnames = ", ".join(sorted(set(f'`{e["file"]}`' for e in files_list)))
        commits = ", ".join(sorted(set(f'`{e["commit"]}`' for e in files_list)))
        lines.append(f"| {pname} | {fnames} | {commits} |")
    lines.append("")

    # Section 3: Unmapped source files
    if unmapped_files:
        lines.append("## Unmapped Source Files")
        lines.append("")
        lines.append("These files were committed without an accompanying verification packet.")
        lines.append("")
        for f in unmapped_files:
            lines.append(f"- `{f}`")
        lines.append("")

    # Section 4: Unmapped packets
    if unmapped_packets:
        lines.append("## Unmapped Packets (Packet-Only Commits)")
        lines.append("")
        lines.append("These packets were committed alone (e.g., SHA backfill, classification fix).")
        lines.append("")
        for p in unmapped_packets:
            lines.append(f"- {p}")
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
    print(f"Markdown report: {path}")


def main():
    repo_root = Path(
        subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
        ).stdout.strip()
    )

    commits = get_commits_with_files()
    print(f"Analyzed {len(commits)} commits")

    mapping = build_mapping(commits)
    print(
        f"Mapped {len(mapping['file_to_packets'])} source files "
        f"to {len(mapping['packet_to_files'])} packets"
    )
    print(f"Unmapped source files: {len(mapping['unmapped_files'])}")
    print(f"Unmapped packets: {len(mapping['unmapped_packets'])}")

    # Write JSON
    json_path = repo_root / "FILE_PACKET_MAP.json"
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)
    print(f"JSON mapping: {json_path}")

    # Write Markdown
    md_path = repo_root / "FILE_PACKET_MAP.md"
    write_markdown_report(mapping, md_path)


if __name__ == "__main__":
    main()
