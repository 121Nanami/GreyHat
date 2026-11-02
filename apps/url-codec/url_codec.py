#!/usr/bin/env python3
"""URL encode / decode from args or stdin."""
from __future__ import annotations
import argparse
import sys
from urllib.parse import quote, unquote, urlencode, parse_qsl


def main() -> int:
    p = argparse.ArgumentParser(description="URL encode/decode")
    p.add_argument("text", nargs="?", help="Text (default: stdin)")
    g = p.add_mutually_exclusive_group()
    g.add_argument("-d", "--decode", action="store_true")
    g.add_argument("-e", "--encode", action="store_true", default=True)
    p.add_argument("--plus", action="store_true", help="Use + for spaces (form encoding)")
    args = p.parse_args()
    text = args.text if args.text is not None else sys.stdin.read().rstrip("\n")
    if args.decode:
        print(unquote(text.replace("+", " ") if args.plus else text))
    else:
        print(quote(text, safe="") if not args.plus else quote(text, safe="").replace("%20", "+"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
