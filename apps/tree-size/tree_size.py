#!/usr/bin/env python3
"""Directory disk-usage tree (no deps)."""
from __future__ import annotations
import argparse
import os
import sys
from pathlib import Path


def human(n: int) -> str:
    x = float(n)
    for u in ("B", "K", "M", "G", "T"):
        if x < 1024 or u == "T":
            return f"{x:7.1f}{u}" if u != "B" else f"{int(x):7d}B"
        x /= 1024
    return str(n)


def walk(root: Path, max_depth: int) -> list[tuple[int, int, Path]]:
    rows: list[tuple[int, int, Path]] = []

    def rec(p: Path, depth: int) -> int:
        total = 0
        try:
            if p.is_symlink():
                return 0
            if p.is_file():
                return p.stat().st_size
            if not p.is_dir():
                return 0
            for child in sorted(p.iterdir(), key=lambda c: c.name.lower()):
                total += rec(child, depth + 1)
            if depth <= max_depth:
                rows.append((depth, total, p))
        except (PermissionError, OSError):
            return 0
        return total

    rec(root, 0)
    return rows


def main() -> int:
    p = argparse.ArgumentParser(description="Disk usage tree")
    p.add_argument("path", nargs="?", default=".", type=Path)
    p.add_argument("-d", "--depth", type=int, default=2)
    p.add_argument("-n", "--top", type=int, default=0, help="If >0, show only largest N at each depth")
    args = p.parse_args()
    root = args.path.resolve()
    if not root.exists():
        print(f"error: {root} missing", file=sys.stderr)
        return 2
    rows = walk(root, args.depth)
    rows.sort(key=lambda r: (r[0], -r[1]))
    if args.top > 0:
        from collections import defaultdict
        bucket: dict[int, list] = defaultdict(list)
        for r in rows:
            bucket[r[0]].append(r)
        rows = []
        for d in sorted(bucket):
            rows.extend(sorted(bucket[d], key=lambda r: -r[1])[: args.top])
        rows.sort(key=lambda r: (r[0], -r[1]))
    for depth, size, path in rows:
        rel = path if depth == 0 else path.relative_to(root)
        print(f"{human(size)}  {'  ' * depth}{rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
