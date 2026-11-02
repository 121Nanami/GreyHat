#!/usr/bin/env python3
"""Re-run a command every N seconds (mini watch)."""
from __future__ import annotations
import argparse
import subprocess
import sys
import time


def main() -> int:
    p = argparse.ArgumentParser(description="Run a command repeatedly")
    p.add_argument("-n", "--interval", type=float, default=2.0)
    p.add_argument("-c", "--clear", action="store_true")
    p.add_argument("cmd", nargs=argparse.REMAINDER, help="Command after --")
    args = p.parse_args()
    cmd = args.cmd
    if cmd and cmd[0] == "--":
        cmd = cmd[1:]
    if not cmd:
        print("Usage: watch_cmd.py [-n 2] [-c] -- command args…", file=sys.stderr)
        return 2
    try:
        while True:
            if args.clear:
                print("\033[2J\033[H", end="")
            print(f"Every {args.interval}s: {' '.join(cmd)}\n")
            subprocess.call(cmd)
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print()
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
