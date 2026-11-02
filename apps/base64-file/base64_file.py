#!/usr/bin/env python3
"""Base64 encode/decode files (stdin/stdout friendly)."""
from __future__ import annotations
import argparse
import base64
import sys
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description="Base64 encode/decode files")
    p.add_argument("path", nargs="?", type=Path, help="Input file (default stdin)")
    p.add_argument("-d", "--decode", action="store_true")
    p.add_argument("-o", "--output", type=Path)
    p.add_argument("-w", "--wrap", type=int, default=76, help="Wrap width for encode (0=off)")
    args = p.parse_args()
    data = args.path.read_bytes() if args.path else sys.stdin.buffer.read()
    if args.decode:
        # tolerate whitespace
        out = base64.b64decode(data)
    else:
        out = base64.b64encode(data)
        if args.wrap:
            text = out.decode("ascii")
            lines = [text[i : i + args.wrap] for i in range(0, len(text), args.wrap)]
            out = ("\n".join(lines) + ("\n" if lines else "")).encode()
        else:
            out = out + b"\n"
    if args.output:
        args.output.write_bytes(out)
    else:
        sys.stdout.buffer.write(out if args.decode else out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
