#!/usr/bin/env python3
"""Find duplicate files by size then content hash."""
from __future__ import annotations
import argparse
import hashlib
import os
import sys
from collections import defaultdict
from pathlib import Path


def file_hash(path: Path, chunk: int = 1 << 20) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def main() -> int:
    p = argparse.ArgumentParser(description="Find duplicate files")
    p.add_argument("root", nargs="?", default=".", type=Path)
    p.add_argument("--min-size", type=int, default=1, help="Skip files smaller than N bytes")
    args = p.parse_args()
    by_size: dict[int, list[Path]] = defaultdict(list)
    for dirpath, _, files in os.walk(args.root):
        for name in files:
            path = Path(dirpath) / name
            try:
                if path.is_symlink():
                    continue
                st = path.stat()
                if st.st_size < args.min_size:
                    continue
                by_size[st.st_size].append(path)
            except OSError:
                continue
    groups = 0
    for size, paths in sorted(by_size.items(), reverse=True):
        if len(paths) < 2:
            continue
        by_hash: dict[str, list[Path]] = defaultdict(list)
        for path in paths:
            try:
                by_hash[file_hash(path)].append(path)
            except OSError:
                continue
        for digest, g in by_hash.items():
            if len(g) < 2:
                continue
            groups += 1
            print(f"## {len(g)} files · {size} bytes · sha256:{digest[:12]}…")
            for path in g:
                print(f"  {path}")
            print()
    if groups == 0:
        print("No duplicates found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
