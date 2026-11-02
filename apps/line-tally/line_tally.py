#!/usr/bin/env python3
"""Count lines by extension under a tree (code LOC sketch)."""
from __future__ import annotations
import argparse
import os
import sys
from collections import Counter
from pathlib import Path

SKIP_DIRS = {".git", "node_modules", "dist", "build", ".venv", "venv", "__pycache__"}


def main() -> int:
    p = argparse.ArgumentParser(description="Line counts by file extension")
    p.add_argument("root", nargs="?", type=Path, default=Path("."))
    p.add_argument("--ext", action="append", help="Only these extensions, e.g. --ext .py")
    args = p.parse_args()
    counts: Counter[str] = Counter()
    files: Counter[str] = Counter()
    for dirpath, dirnames, filenames in os.walk(args.root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            path = Path(dirpath) / name
            ext = path.suffix.lower() or "(none)"
            if args.ext and ext not in args.ext:
                continue
            try:
                # skip huge/binary-ish
                data = path.read_bytes()
                if b"\x00" in data[:2048]:
                    continue
                n = data.count(b"\n") + (0 if data.endswith(b"\n") or not data else 1)
                counts[ext] += n
                files[ext] += 1
            except OSError:
                continue
    rows = sorted(counts.items(), key=lambda kv: -kv[1])
    width = max((len(e) for e, _ in rows), default=4)
    total = 0
    for ext, n in rows:
        print(f"{ext:{width}}  {n:8d} lines  {files[ext]:5d} files")
        total += n
    print(f"{'TOTAL':{width}}  {total:8d} lines")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
