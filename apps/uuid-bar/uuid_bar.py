#!/usr/bin/env python3
"""Mint UUIDs / nanoid-ish tokens in bulk."""
from __future__ import annotations
import argparse
import secrets
import string
import uuid


def nanoid(n: int = 21) -> str:
    alphabet = string.ascii_letters + string.digits + "_-"
    return "".join(secrets.choice(alphabet) for _ in range(n))


def main() -> int:
    p = argparse.ArgumentParser(description="Bulk UUID / nanoid mint")
    p.add_argument("-n", type=int, default=1)
    p.add_argument("-t", "--type", choices=["uuid4", "uuid1", "nanoid"], default="uuid4")
    p.add_argument("--len", type=int, default=21, help="nanoid length")
    args = p.parse_args()
    for _ in range(max(1, args.n)):
        if args.type == "uuid4":
            print(str(uuid.uuid4()))
        elif args.type == "uuid1":
            print(str(uuid.uuid1()))
        else:
            print(nanoid(args.len))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
