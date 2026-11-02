#!/usr/bin/env python3
"""Verify ISO / image checksums (SHA256/SHA512/MD5) against an expected digest."""
from __future__ import annotations
import argparse
import hashlib
import sys
from pathlib import Path

ALGOS = {"sha256": hashlib.sha256, "sha512": hashlib.sha512, "md5": hashlib.md5, "sha1": hashlib.sha1}


def digest_file(path: Path, algo: str, chunk: int = 1 << 20) -> str:
    h = ALGOS[algo]()
    with path.open("rb") as f:
        while True:
            b = f.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


def main() -> int:
    p = argparse.ArgumentParser(description="Verify ISO/image checksums (read-only)")
    p.add_argument("file", type=Path, help="ISO or image path")
    p.add_argument("-a", "--algo", choices=sorted(ALGOS), default="sha256")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("-e", "--expected", help="Expected hex digest")
    g.add_argument("-c", "--checksum-file", type=Path, help="File containing digest (first token)")
    p.add_argument("--print-only", action="store_true", help="Only print computed digest")
    args = p.parse_args()

    if not args.file.is_file():
        print(f"error: not a file: {args.file}", file=sys.stderr)
        return 2

    expected = args.expected
    if args.checksum_file:
        text = args.checksum_file.read_text(encoding="utf-8", errors="replace").strip()
        expected = text.split()[0]

    got = digest_file(args.file, args.algo)
    print(f"{args.algo.upper()}({args.file.name}) = {got}")
    if args.print_only:
        return 0
    exp = expected.strip().lower()
    if got.lower() == exp:
        print("OK — digest matches")
        return 0
    print("FAIL — digest does not match expected", file=sys.stderr)
    print(f"expected: {exp}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
