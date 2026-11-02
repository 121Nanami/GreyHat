#!/usr/bin/env python3
"""Unified / side-by-side line diff for two text files (stdlib difflib)."""
from __future__ import annotations
import argparse
import difflib
import sys
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description="Line diff two files")
    p.add_argument("a", type=Path)
    p.add_argument("b", type=Path)
    p.add_argument("-c", "--context", type=int, default=3)
    p.add_argument("-s", "--side-by-side", action="store_true")
    p.add_argument("-w", "--width", type=int, default=60)
    args = p.parse_args()
    A = args.a.read_text(encoding="utf-8", errors="replace").splitlines()
    B = args.b.read_text(encoding="utf-8", errors="replace").splitlines()
    if args.side_by_side:
        rows = difflib.HtmlDiff().make_table  # noqa: keep import unused path
        for line in difflib.ndiff(A, B):
            print(line)
        return 0 if A == B else 1
    ud = difflib.unified_diff(A, B, fromfile=str(args.a), tofile=str(args.b), lineterm="", n=args.context)
    out = list(ud)
    print("\n".join(out))
    return 0 if not out else 1


if __name__ == "__main__":
    sys.exit(main())
