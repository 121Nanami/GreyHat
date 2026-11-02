#!/usr/bin/env python3
"""Merge hosts-file snippets; dedupe by hostname (last wins). Dry-run by default."""
from __future__ import annotations
import argparse
import sys
from pathlib import Path


def parse_hosts(text: str) -> list[tuple[str, list[str], str]]:
    """Return list of (ip, names, original_line_or_comment). Comments kept as ('#', [], line)."""
    rows = []
    for line in text.splitlines():
        raw = line.rstrip()
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            rows.append(("#", [], raw))
            continue
        parts = stripped.split()
        if len(parts) < 2:
            rows.append(("#", [], raw))
            continue
        rows.append((parts[0], parts[1:], raw))
    return rows


def main() -> int:
    p = argparse.ArgumentParser(description="Merge hosts files (last hostname wins)")
    p.add_argument("files", nargs="+", type=Path)
    p.add_argument("-o", "--output", type=Path, help="Write merged file (else stdout)")
    p.add_argument("--apply", action="store_true", help="Required to write -o (safety)")
    args = p.parse_args()
    # hostname -> (ip, source_note)
    mapping: dict[str, str] = {}
    comments: list[str] = []
    for path in args.files:
        text = path.read_text(encoding="utf-8", errors="replace")
        for ip, names, raw in parse_hosts(text):
            if ip == "#":
                comments.append(raw)
                continue
            for name in names:
                mapping[name.lower()] = ip
    # group names by ip
    by_ip: dict[str, list[str]] = {}
    for name, ip in sorted(mapping.items()):
        by_ip.setdefault(ip, []).append(name)
    lines = ["# merged by hosts-merge", "# sources: " + ", ".join(str(f) for f in args.files)]
    for ip, names in sorted(by_ip.items(), key=lambda kv: kv[0]):
        lines.append(f"{ip}\t{' '.join(names)}")
    out = "\n".join(lines) + "\n"
    if args.output:
        if not args.apply:
            print("Refusing to write without --apply (dry-run). Showing result:\n", file=sys.stderr)
            print(out)
            return 0
        args.output.write_text(out)
        print(f"Wrote {args.output} ({len(mapping)} hostnames)", file=sys.stderr)
    else:
        print(out, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
