#!/usr/bin/env python3
"""Mint UUIDs / ulids-ish random ids."""
from __future__ import annotations
import argparse
import secrets
import sys
import uuid


def main() -> int:
    p = argparse.ArgumentParser(description="Mint UUIDs")
    p.add_argument("-n", "--count", type=int, default=1)
    p.add_argument("-v", "--version", choices=["4", "1", "hex32"], default="4")
    p.add_argument("--upper", action="store_true")
    args = p.parse_args()
    for _ in range(args.count):
        if args.version == "4":
            s = str(uuid.uuid4())
        elif args.version == "1":
            s = str(uuid.uuid1())
        else:
            s = secrets.token_hex(16)
        print(s.upper() if args.upper else s)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
