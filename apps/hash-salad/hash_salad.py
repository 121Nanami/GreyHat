#!/usr/bin/env python3
"""Hash text or files with common digests."""
from __future__ import annotations
import argparse
import hashlib
import sys
from pathlib import Path

ALGOS = ["md5", "sha1", "sha256", "sha512", "blake2b"]


def main() -> int:
    p = argparse.ArgumentParser(description="Hash text or files")
    p.add_argument("-a", "--algo", choices=ALGOS + ["all"], default="sha256")
    p.add_argument("-f", "--file", type=Path)
    p.add_argument("text", nargs="?", help="Text to hash (else stdin if no --file)")
    args = p.parse_args()
    if args.file:
        data = args.file.read_bytes()
        label = str(args.file)
    elif args.text is not None:
        data = args.text.encode()
        label = "text"
    else:
        data = sys.stdin.buffer.read()
        label = "stdin"
    names = ALGOS if args.algo == "all" else [args.algo]
    for name in names:
        h = hashlib.new(name)
        h.update(data)
        print(f"{name:8s}  {h.hexdigest()}  {label}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
