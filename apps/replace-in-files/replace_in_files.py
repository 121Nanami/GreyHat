#!/usr/bin/env python3
"""Bulk find/replace across files with optional dry-run and regex."""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description="Bulk replace in files")
    p.add_argument("pattern")
    p.add_argument("replacement")
    p.add_argument("files", nargs="+", type=Path)
    p.add_argument("-E", "--regex", action="store_true")
    p.add_argument("-n", "--dry-run", action="store_true")
    p.add_argument("-i", "--ignore-case", action="store_true")
    args = p.parse_args()
    flags = re.I if args.ignore_case else 0
    rx = re.compile(args.pattern if args.regex else re.escape(args.pattern), flags)
    changed = 0
    for path in args.files:
        if not path.is_file():
            print(f"skip {path}", file=sys.stderr)
            continue
        text = path.read_text(encoding="utf-8", errors="surrogateescape")
        new, n = rx.subn(args.replacement, text)
        if n:
            changed += 1
            print(f"{path}: {n} replacement(s)")
            if not args.dry_run:
                path.write_text(new, encoding="utf-8", errors="surrogateescape")
    if args.dry_run:
        print("(dry-run — no files written)")
    return 0 if changed else 1


if __name__ == "__main__":
    sys.exit(main())
