#!/usr/bin/env python3
"""Fetch and print HTTP response headers."""
from __future__ import annotations
import argparse
import sys
import urllib.request


def main() -> int:
    p = argparse.ArgumentParser(description="Print HTTP response headers")
    p.add_argument("url")
    p.add_argument("-X", "--method", default="GET", choices=["GET", "HEAD"])
    p.add_argument("-t", "--timeout", type=float, default=10.0)
    args = p.parse_args()
    url = args.url if "://" in args.url else "https://" + args.url
    req = urllib.request.Request(url, method=args.method, headers={"User-Agent": "http-headers/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=args.timeout) as resp:
            print(f"HTTP {resp.status} {resp.reason}")
            for k, v in resp.headers.items():
                print(f"{k}: {v}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
