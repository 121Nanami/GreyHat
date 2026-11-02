#!/usr/bin/env python3
"""Verify file checksums (SHA-256 / SHA-512 / MD5) — consumer trust helper."""
from __future__ import annotations
import argparse
import hashlib
import sys
from pathlib import Path

ALGOS = {"sha256": hashlib.sha256, "sha512": hashlib.sha512, "md5": hashlib.md5}


def digest(path: Path, algo: str) -> str:
    h = ALGOS[algo]()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    p = argparse.ArgumentParser(description="Ellen Checksum Desk — verify downloads safely")
    p.add_argument("file", type=Path)
    p.add_argument("-a", "--algo", choices=ALGOS, default="sha256")
    p.add_argument("-e", "--expect", help="Expected hex digest (optional)")
    p.add_argument("-c", "--checksum-file", type=Path, help="File containing expected digest")
    args = p.parse_args()
    if not args.file.is_file():
        print(f"Missing file: {args.file}", file=sys.stderr)
        return 2
    got = digest(args.file, args.algo)
    print(f"{args.algo}: {got}")
    print(f"file: {args.file} ({args.file.stat().st_size} bytes)")
    expect = args.expect
    if args.checksum_file:
        expect = args.checksum_file.read_text().strip().split()[0]
    if expect:
        ok = got.lower() == expect.lower().strip()
        print("MATCH ✓" if ok else "MISMATCH ✗")
        print(f"expected: {expect.strip()}")
        return 0 if ok else 1
    print("(pass --expect HEX or -c checksums.txt to verify)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
