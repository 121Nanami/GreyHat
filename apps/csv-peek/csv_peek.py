#!/usr/bin/env python3
"""Quick CSV peek: shape, dtypes guess, sample rows."""
from __future__ import annotations
import argparse
import csv
import statistics
import sys
from collections import Counter
from pathlib import Path


def is_float(s: str) -> bool:
    try:
        float(s.replace(",", ""))
        return s.strip() != ""
    except ValueError:
        return False


def main() -> int:
    p = argparse.ArgumentParser(description="Peek at a CSV file")
    p.add_argument("path", type=Path)
    p.add_argument("-n", "--rows", type=int, default=5)
    args = p.parse_args()
    with args.path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            print("No header row found", file=sys.stderr)
            return 1
        rows = list(reader)
    print(f"file: {args.path}")
    print(f"rows: {len(rows)}  cols: {len(reader.fieldnames)}")
    print("columns:")
    for col in reader.fieldnames:
        vals = [r.get(col, "") or "" for r in rows]
        nonempty = [v for v in vals if v.strip()]
        nums = [float(v.replace(",", "")) for v in nonempty if is_float(v)]
        if len(nums) >= max(3, len(nonempty) * 0.6):
            mean = statistics.fmean(nums)
            print(f"  · {col}: numeric n={len(nums)} mean={mean:.4g} min={min(nums):.4g} max={max(nums):.4g}")
        else:
            top = Counter(nonempty).most_common(3)
            sample = ", ".join(f"{k!r}×{v}" for k, v in top) or "(empty)"
            print(f"  · {col}: text unique≈{len(set(nonempty))} top={sample}")
    print(f"\nsample ({min(args.rows, len(rows))} rows):")
    for r in rows[: args.rows]:
        print(" ", {k: r[k] for k in reader.fieldnames})
    return 0


if __name__ == "__main__":
    sys.exit(main())
