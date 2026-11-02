#!/usr/bin/env python3
"""Re-run a command when files change (simple polling watcher)."""
from __future__ import annotations
import argparse
import subprocess
import sys
import time
from pathlib import Path


def snapshot(paths: list[Path]) -> dict[str, float]:
    out: dict[str, float] = {}
    for p in paths:
        if p.is_file():
            out[str(p)] = p.stat().st_mtime
        elif p.is_dir():
            for f in p.rglob("*"):
                if f.is_file():
                    try:
                        out[str(f)] = f.stat().st_mtime
                    except OSError:
                        pass
    return out


def main() -> int:
    p = argparse.ArgumentParser(description="Poll paths and re-run command on change")
    p.add_argument("-p", "--path", action="append", type=Path, required=True)
    p.add_argument("-i", "--interval", type=float, default=1.0)
    p.add_argument("-c", "--clear", action="store_true")
    p.add_argument("cmd", nargs=argparse.REMAINDER, help="Command after --")
    args = p.parse_args()
    cmd = args.cmd[1:] if args.cmd and args.cmd[0] == "--" else args.cmd
    if not cmd:
        print("error: provide command after --", file=sys.stderr)
        return 2
    last = snapshot(args.path)

    def run() -> None:
        if args.clear:
            print("\033[2J\033[H", end="")
        print(f"$ {' '.join(cmd)}", flush=True)
        subprocess.call(cmd)

    run()
    try:
        while True:
            time.sleep(args.interval)
            cur = snapshot(args.path)
            if cur != last:
                last = cur
                run()
    except KeyboardInterrupt:
        print()
        return 0


if __name__ == "__main__":
    sys.exit(main())
