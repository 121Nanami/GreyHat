#!/usr/bin/env python3
"""Human-friendly stat(1) for one or more paths."""
from __future__ import annotations
import argparse
import os
import stat
import sys
import time
from pathlib import Path


def mode_str(mode: int) -> str:
    return stat.filemode(mode)


def main() -> int:
    p = argparse.ArgumentParser(description="Friendly path stat")
    p.add_argument("paths", nargs="+", type=Path)
    args = p.parse_args()
    rc = 0
    for path in args.paths:
        try:
            st = path.lstat()
        except OSError as e:
            print(f"{path}: {e}", file=sys.stderr)
            rc = 1
            continue
        kind = "symlink" if stat.S_ISLNK(st.st_mode) else (
            "dir" if stat.S_ISDIR(st.st_mode) else (
            "file" if stat.S_ISREG(st.st_mode) else "other"))
        print(f"{path}")
        print(f"  type:  {kind}")
        print(f"  mode:  {mode_str(st.st_mode)} ({oct(st.st_mode & 0o777)})")
        print(f"  size:  {st.st_size} bytes")
        print(f"  uid/gid: {st.st_uid}/{st.st_gid}")
        print(f"  mtime: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(st.st_mtime))}")
        if kind == "symlink":
            print(f"  target: {os.readlink(path)}")
        print()
    return rc


if __name__ == "__main__":
    sys.exit(main())
