#!/usr/bin/env python3
"""Sparkline of git commit activity by day."""
from __future__ import annotations
import argparse
import subprocess
import sys
from collections import Counter
from datetime import datetime, timedelta


BLOCKS = "▁▂▃▄▅▆▇█"


def spark(values: list[int]) -> str:
    if not values:
        return ""
    lo, hi = min(values), max(values)
    span = hi - lo or 1
    return "".join(BLOCKS[int((v - lo) / span * (len(BLOCKS) - 1))] for v in values)


def main() -> int:
    p = argparse.ArgumentParser(description="Git commit sparkline")
    p.add_argument("-d", "--days", type=int, default=28)
    p.add_argument("-C", "--repo", default=".")
    args = p.parse_args()
    try:
        out = subprocess.check_output(
            ["git", "-C", args.repo, "log", f"--since={args.days}.days", "--pretty=%ad", "--date=short"],
            text=True,
            stderr=subprocess.DEVNULL,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Not a git repo (or git missing).", file=sys.stderr)
        return 1
    counts = Counter(line.strip() for line in out.splitlines() if line.strip())
    today = datetime.utcnow().date()
    days = [(today - timedelta(days=i)).isoformat() for i in range(args.days - 1, -1, -1)]
    vals = [counts.get(d, 0) for d in days]
    print(spark(vals), f"  ({sum(vals)} commits / {args.days}d)")
    print(f"{days[0]} → {days[-1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
