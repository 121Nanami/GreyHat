#!/usr/bin/env python3
"""Fetch and print response headers (and optional status timing)."""
from __future__ import annotations
import argparse
import sys
import time
import urllib.error
import urllib.request


def main() -> int:
    p = argparse.ArgumentParser(description="HTTP response header peek")
    p.add_argument("url")
    p.add_argument("-X", "--method", default="GET")
    p.add_argument("-t", "--timeout", type=float, default=10.0)
    p.add_argument("--body", action="store_true", help="Also print body (truncated)")
    args = p.parse_args()
    req = urllib.request.Request(args.url, method=args.method.upper(), headers={"User-Agent": "greyhatinc-headers-peek/0.1"})
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=args.timeout) as resp:
            ms = (time.perf_counter() - t0) * 1000
            print(f"HTTP {resp.status} {resp.reason}  ({ms:.0f} ms)")
            for k, v in resp.headers.items():
                print(f"{k}: {v}")
            if args.body:
                data = resp.read(4096)
                print("\n--- body (first 4KiB) ---")
                sys.stdout.buffer.write(data)
                print()
    except urllib.error.HTTPError as e:
        ms = (time.perf_counter() - t0) * 1000
        print(f"HTTP {e.code} {e.reason}  ({ms:.0f} ms)", file=sys.stderr)
        for k, v in e.headers.items():
            print(f"{k}: {v}")
        return 1
    except Exception as e:  # noqa: BLE001
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
