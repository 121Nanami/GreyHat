#!/usr/bin/env python3
"""Convert epoch ↔ human time (UTC / local)."""
from __future__ import annotations
import argparse
import sys
from datetime import datetime, timezone


def main() -> int:
    p = argparse.ArgumentParser(description="Epoch ↔ datetime converter")
    p.add_argument("value", nargs="?", help="Epoch seconds/ms OR ISO datetime; omit for now")
    p.add_argument("--local", action="store_true", help="Show local time instead of UTC")
    args = p.parse_args()
    if args.value is None:
        now = datetime.now(timezone.utc)
        print(f"epoch: {int(now.timestamp())}")
        print(f"iso:   {now.isoformat()}")
        return 0
    v = args.value
    # numeric epoch?
    try:
        num = float(v)
        if num > 1e12:  # ms
            num /= 1000.0
        dt = datetime.fromtimestamp(num, tz=timezone.utc)
        if args.local:
            dt = dt.astimezone()
        print(dt.isoformat())
        return 0
    except ValueError:
        pass
    # parse ISO-ish
    raw = v.replace("Z", "+00:00")
    try:
        dt = datetime.fromisoformat(raw)
    except ValueError:
        print(f"Cannot parse: {v}", file=sys.stderr)
        return 1
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    print(int(dt.timestamp()))
    print(dt.astimezone(timezone.utc).isoformat())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
