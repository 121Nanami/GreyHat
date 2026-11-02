#!/usr/bin/env python3
"""Pretty-print or compact JSON; optional path sort + key filter."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description="Pretty-print JSON")
    p.add_argument("path", nargs="?", type=Path)
    p.add_argument("-c", "--compact", action="store_true")
    p.add_argument("-s", "--sort-keys", action="store_true")
    args = p.parse_args()
    text = args.path.read_text() if args.path else sys.stdin.read()
    try:
        data = json.loads(text)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {e}", file=sys.stderr)
        return 1
    if args.compact:
        print(json.dumps(data, sort_keys=args.sort_keys, separators=(",", ":"), ensure_ascii=False))
    else:
        print(json.dumps(data, indent=2, sort_keys=args.sort_keys, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
