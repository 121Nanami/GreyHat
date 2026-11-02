#!/usr/bin/env python3
"""Convert CSV to JSON array of objects."""
from __future__ import annotations
import argparse
import csv
import json
import sys
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description="CSV → JSON")
    p.add_argument("path", nargs="?", type=Path, help="CSV path (default stdin)")
    p.add_argument("--pretty", action="store_true")
    args = p.parse_args()
    f = args.path.open(newline="", encoding="utf-8-sig") if args.path else sys.stdin
    with f:
        rows = list(csv.DictReader(f))
    print(json.dumps(rows, indent=2 if args.pretty else None, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
