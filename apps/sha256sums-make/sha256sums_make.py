#!/usr/bin/env python3
"""Generate SHA256SUMS / sha256sums=() style digests for release artifacts."""
from __future__ import annotations
import argparse
import hashlib
import sys
from pathlib import Path


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    p = argparse.ArgumentParser(description="Make SHA256SUMS or PKGBUILD array")
    p.add_argument("files", nargs="+", type=Path)
    p.add_argument("--pkgbuild", action="store_true", help="Emit sha256sums=(...) snippet")
    args = p.parse_args()
    digests = []
    for f in args.files:
        if not f.is_file():
            print(f"error: {f}", file=sys.stderr)
            return 2
        digests.append((sha256(f), f.name))
    if args.pkgbuild:
        print("sha256sums=(")
        for d, _ in digests:
            print(f"  '{d}'")
        print(")")
    else:
        for d, name in digests:
            print(f"{d}  {name}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
