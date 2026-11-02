#!/usr/bin/env python3
"""Deduplicate PATH-like colon lists while preserving order."""
from __future__ import annotations
import argparse
import os
import sys


def main() -> int:
    p = argparse.ArgumentParser(description="Deduplicate PATH entries")
    p.add_argument("value", nargs="?", help="Colon list (default: $PATH)")
    p.add_argument("--check", action="store_true", help="Only report dupes / missing dirs")
    args = p.parse_args()
    raw = args.value if args.value is not None else os.environ.get("PATH", "")
    parts = [x for x in raw.split(":") if x != ""]
    seen = set()
    out = []
    dupes = []
    for part in parts:
        if part in seen:
            dupes.append(part)
            continue
        seen.add(part)
        out.append(part)
    if args.check:
        for d in dupes:
            print(f"dupe: {d}")
        for d in out:
            if not os.path.isdir(d):
                print(f"missing: {d}")
        print(f"entries: {len(parts)} → {len(out)} unique")
        return 0
    print(":".join(out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
