#!/usr/bin/env python3
"""Top disk consumers one level deep (no find/du required beyond Python)."""
from __future__ import annotations
import argparse
import os
import sys
from pathlib import Path


def dir_size(path: Path) -> int:
    total = 0
    try:
        for root, dirs, files in os.walk(path, followlinks=False):
            for f in files:
                fp = Path(root) / f
                try:
                    total += fp.stat().st_size
                except OSError:
                    pass
    except OSError:
        pass
    return total


def fmt(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:7.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


def main() -> int:
    p = argparse.ArgumentParser(description="Largest children of a directory")
    p.add_argument("path", nargs="?", type=Path, default=Path("."))
    p.add_argument("-n", "--top", type=int, default=15)
    args = p.parse_args()
    root = args.path.resolve()
    if not root.is_dir():
        print(f"Not a directory: {root}", file=sys.stderr)
        return 2
    rows = []
    try:
        children = list(root.iterdir())
    except OSError as e:
        print(e, file=sys.stderr)
        return 1
    for child in children:
        try:
            if child.is_symlink():
                continue
            if child.is_file():
                sz = child.stat().st_size
            elif child.is_dir():
                sz = dir_size(child)
            else:
                continue
            rows.append((sz, child.name + ("/" if child.is_dir() else "")))
        except OSError:
            continue
    rows.sort(reverse=True)
    for sz, name in rows[: args.top]:
        print(f"{fmt(sz)}  {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
