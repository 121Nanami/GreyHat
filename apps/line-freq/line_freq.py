#!/usr/bin/env python3
"""Frequency count of lines (or fields) from stdin/file — like sort | uniq -c."""
from __future__ import annotations
import argparse
import collections
import sys
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description="Line / field frequency counter")
    p.add_argument("file", nargs="?", type=Path)
    p.add_argument("-n", type=int, default=0, help="Show top N (0=all)")
    p.add_argument("-f", "--field", type=int, default=0, help="1-based field number")
    p.add_argument("-d", "--delim", default=None, help="Field delimiter (default whitespace)")
    p.add_argument("-r", "--reverse", action="store_true", help="Ascending count")
    args = p.parse_args()
    fh = args.file.open(encoding="utf-8", errors="replace") if args.file else sys.stdin
    c: collections.Counter[str] = collections.Counter()
    with fh:
        for line in fh:
            line = line.rstrip("\n")
            if args.field:
                parts = line.split(args.delim) if args.delim is not None else line.split()
                if len(parts) < args.field:
                    continue
                key = parts[args.field - 1]
            else:
                key = line
            c[key] += 1
    items = c.most_common() if not args.reverse else sorted(c.items(), key=lambda kv: (kv[1], kv[0]))
    if args.n > 0:
        items = items[: args.n] if not args.reverse else items[: args.n]
    width = len(str(items[0][1])) if items else 1
    for key, n in items:
        print(f"{n:>{width}}  {key}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
