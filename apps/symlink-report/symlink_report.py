#!/usr/bin/env python3
"""Report symlinks under a tree: target, broken or not."""
from __future__ import annotations
import argparse
import os
import sys
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description="List symlinks and flag broken ones")
    p.add_argument("root", nargs="?", type=Path, default=Path("."))
    p.add_argument("--broken-only", action="store_true")
    args = p.parse_args()
    broken = 0
    total = 0
    for dirpath, dirnames, filenames in os.walk(args.root):
        # include symlink dirs as entries but don't walk into them
        for name in dirnames + filenames:
            path = Path(dirpath) / name
            try:
                if not path.is_symlink():
                    continue
                total += 1
                target = os.readlink(path)
                ok = path.exists()
                if not ok:
                    broken += 1
                if args.broken_only and ok:
                    continue
                status = "OK" if ok else "BROKEN"
                print(f"{status:7}  {path}  →  {target}")
            except OSError as e:
                print(f"ERROR    {path}  ({e})", file=sys.stderr)
    print(f"— {total} symlinks, {broken} broken", file=sys.stderr)
    return 1 if broken else 0


if __name__ == "__main__":
    raise SystemExit(main())
