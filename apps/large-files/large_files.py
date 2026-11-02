#!/usr/bin/env python3
"""Find the largest files under a tree."""
from __future__ import annotations
import argparse
import os
import sys
from pathlib import Path


def fmt(n: int) -> str:
    x = float(n)
    for u in ("B", "KB", "MB", "GB", "TB"):
        if x < 1024:
            return f"{x:7.1f} {u}"
        x /= 1024
    return f"{x:.1f} PB"


def main() -> int:
    p = argparse.ArgumentParser(description="Largest files under a path")
    p.add_argument("root", nargs="?", type=Path, default=Path("."))
    p.add_argument("-n", "--top", type=int, default=20)
    p.add_argument("--min", type=int, default=0, help="Min size bytes")
    args = p.parse_args()
    rows: list[tuple[int, str]] = []
    for dirpath, _, files in os.walk(args.root):
        for name in files:
            path = Path(dirpath) / name
            try:
                if path.is_symlink():
                    continue
                sz = path.stat().st_size
                if sz >= args.min:
                    rows.append((sz, str(path)))
            except OSError:
                continue
    rows.sort(reverse=True)
    for sz, path in rows[: args.top]:
        print(f"{fmt(sz)}  {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
