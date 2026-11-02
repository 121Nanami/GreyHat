#!/usr/bin/env python3
"""Check a numeric column against Benford's law (CSV or one number per line)."""
from __future__ import annotations
import argparse
import csv
import math
import sys
from collections import Counter
from pathlib import Path


def leading_digit(n: float) -> int | None:
    if n == 0 or not math.isfinite(n):
        return None
    s = f"{abs(n):.15e}"
    for ch in s:
        if ch in "123456789":
            return int(ch)
    return None


def expected() -> dict[int, float]:
    return {d: math.log10(1 + 1 / d) for d in range(1, 10)}


def main() -> int:
    p = argparse.ArgumentParser(description="Benford check on a column")
    p.add_argument("file", nargs="?", type=Path, help="CSV or numbers file (stdin ok)")
    p.add_argument("-c", "--column", default="0", help="CSV column name or 0-based index")
    p.add_argument("--csv", action="store_true", help="Force CSV mode")
    args = p.parse_args()
    text = args.file.read_text(encoding="utf-8") if args.file else sys.stdin.read()
    nums: list[float] = []
    if args.csv or (args.file and args.file.suffix.lower() == ".csv"):
        rows = list(csv.DictReader(text.splitlines()) if not args.column.isdigit()
                    else csv.reader(text.splitlines()))
        if not rows:
            print("error: empty", file=sys.stderr)
            return 2
        if args.column.isdigit():
            idx = int(args.column)
            if isinstance(rows[0], list):
                # skip header if non-numeric
                start = 1 if rows and rows[0] and not _is_num(rows[0][idx] if idx < len(rows[0]) else "") else 0
                for r in rows[start:]:
                    if idx < len(r) and _is_num(r[idx]):
                        nums.append(float(r[idx]))
            else:
                pass
        else:
            for r in rows:  # dict rows
                v = r.get(args.column, "")
                if _is_num(v):
                    nums.append(float(v))
    else:
        for line in text.splitlines():
            line = line.strip()
            if _is_num(line):
                nums.append(float(line))

    digs = [leading_digit(n) for n in nums]
    digs = [d for d in digs if d]
    if not digs:
        print("error: no numeric values", file=sys.stderr)
        return 2
    c = Counter(digs)
    total = len(digs)
    exp = expected()
    print(f"n={total}")
    print(f"{'d':>2}  {'obs':>7}  {'exp':>7}  {'delta':>7}")
    chi = 0.0
    for d in range(1, 10):
        o = c[d] / total
        e = exp[d]
        chi += total * ((c[d] / total - e) ** 2) / e
        print(f"{d:2d}  {o:7.3f}  {e:7.3f}  {o-e:+7.3f}")
    print(f"chi-square (df=8) ≈ {chi:.3f}")
    return 0


def _is_num(s: str) -> bool:
    try:
        float(s.replace(",", ""))
        return True
    except ValueError:
        return False


if __name__ == "__main__":
    sys.exit(main())
