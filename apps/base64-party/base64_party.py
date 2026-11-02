#!/usr/bin/env python3
"""Encode/decode base64 (std / url-safe) from args, stdin, or files."""
from __future__ import annotations
import argparse
import base64
import sys


def main() -> int:
    p = argparse.ArgumentParser(description="Base64 encode/decode helper")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("-e", "--encode", action="store_true")
    g.add_argument("-d", "--decode", action="store_true")
    p.add_argument("-u", "--urlsafe", action="store_true")
    p.add_argument("-w", "--wrap", type=int, default=0, help="Wrap encoded output every N cols")
    p.add_argument("data", nargs="?", help="Text (omit to read stdin)")
    p.add_argument("-f", "--file", type=argparse.FileType("rb"), help="Binary file input")
    args = p.parse_args()
    if args.file:
        raw = args.file.read()
    elif args.data is not None:
        raw = args.data.encode()
    else:
        raw = sys.stdin.buffer.read()

    if args.encode:
        enc = base64.urlsafe_b64encode if args.urlsafe else base64.b64encode
        out = enc(raw).decode("ascii")
        if args.wrap and args.wrap > 0:
            out = "\n".join(out[i : i + args.wrap] for i in range(0, len(out), args.wrap))
        print(out)
        return 0
    text = raw.decode("ascii", errors="ignore").strip()
    pad = "=" * ((4 - len(text) % 4) % 4)
    dec = base64.urlsafe_b64decode if args.urlsafe else base64.b64decode
    sys.stdout.buffer.write(dec(text + pad))
    return 0


if __name__ == "__main__":
    sys.exit(main())
