#!/usr/bin/env python3
"""List zip/tar contents safely without extracting."""
from __future__ import annotations
import argparse
import sys
import tarfile
import zipfile
from pathlib import Path


def peek_zip(path: Path) -> None:
    with zipfile.ZipFile(path) as zf:
        total = 0
        for info in zf.infolist():
            total += info.file_size
            flag = "/" if info.is_dir() else " "
            print(f"{info.file_size:12d}{flag}  {info.filename}")
        print(f"— {len(zf.infolist())} entries, {total} uncompressed bytes")


def peek_tar(path: Path) -> None:
    with tarfile.open(path) as tf:
        total = 0
        n = 0
        for m in tf.getmembers():
            n += 1
            total += m.size
            flag = "/" if m.isdir() else " "
            print(f"{m.size:12d}{flag}  {m.name}")
        print(f"— {n} entries, {total} bytes")


def main() -> int:
    p = argparse.ArgumentParser(description="Peek inside zip/tar without extracting")
    p.add_argument("archive", type=Path)
    args = p.parse_args()
    path = args.archive
    if not path.is_file():
        print(f"Not a file: {path}", file=sys.stderr)
        return 2
    name = path.name.lower()
    try:
        if zipfile.is_zipfile(path):
            peek_zip(path)
        elif name.endswith((".tar", ".tar.gz", ".tgz", ".tar.bz2", ".tbz2", ".tar.xz", ".txz")) or tarfile.is_tarfile(path):
            peek_tar(path)
        else:
            print("Unsupported archive type", file=sys.stderr)
            return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
