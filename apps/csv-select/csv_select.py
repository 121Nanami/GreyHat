#!/usr/bin/env python3
"""Select / reorder CSV columns by name or index; optional filter."""
from __future__ import annotations
import argparse
import csv
import re
import sys
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description="Select CSV columns")
    p.add_argument("file", nargs="?", type=Path)
    p.add_argument("-c", "--columns", required=True, help="Comma list of names or 0-based indices")
    p.add_argument("--where", help="Simple col=value filter")
    args = p.parse_args()
    fh = args.file.open(newline="", encoding="utf-8") if args.file else sys.stdin
    cols = [c.strip() for c in args.columns.split(",") if c.strip()]
    with fh:
        reader = csv.DictReader(fh)
        if reader.fieldnames is None:
            print("error: no header", file=sys.stderr)
            return 2
        fields = list(reader.fieldnames)
        selected = []
        for c in cols:
            if c.isdigit():
                selected.append(fields[int(c)])
            else:
                if c not in fields:
                    print(f"error: unknown column {c}", file=sys.stderr)
                    return 2
                selected.append(c)
        where = None
        if args.where:
            m = re.match(r"^([^=]+)=(.*)$", args.where)
            if not m:
                print("error: --where needs col=value", file=sys.stderr)
                return 2
            where = (m.group(1).strip(), m.group(2))
        w = csv.DictWriter(sys.stdout, fieldnames=selected, lineterminator="\n")
        w.writeheader()
        for row in reader:
            if where and row.get(where[0]) != where[1]:
                continue
            w.writerow({k: row.get(k, "") for k in selected})
    return 0


if __name__ == "__main__":
    sys.exit(main())
