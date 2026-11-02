#!/usr/bin/env python3
"""Probe mirror latency with HEAD requests — pick a snappy repo mirror."""
from __future__ import annotations
import argparse
import statistics
import sys
import time
import urllib.error
import urllib.request

DEFAULTS = [
    "https://geo.mirror.pkgbuild.com/",
    "https://mirror.rackspace.com/archlinux/",
    "https://mirrors.kernel.org/archlinux/",
    "https://mirror.arizona.edu/archlinux/",
]


def ping(url: str, timeout: float) -> float | None:
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": "mirror-pulse/1.0"})
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            resp.read(0)
        return (time.perf_counter() - t0) * 1000
    except Exception:
        return None


def main() -> int:
    p = argparse.ArgumentParser(description="Mirror Pulse — latency check for package mirrors")
    p.add_argument("urls", nargs="*", default=DEFAULTS)
    p.add_argument("-n", "--tries", type=int, default=3)
    p.add_argument("-t", "--timeout", type=float, default=5.0)
    args = p.parse_args()
    rows = []
    for url in args.urls:
        samples = [ping(url, args.timeout) for _ in range(args.tries)]
        ok = [s for s in samples if s is not None]
        if not ok:
            rows.append((float("inf"), url, "FAIL", samples))
            print(f"FAIL  {url}")
            continue
        med = statistics.median(ok)
        rows.append((med, url, f"{med:.0f} ms", samples))
        print(f"{med:7.0f} ms  {url}")
    rows.sort(key=lambda r: r[0])
    print()
    if rows and rows[0][0] != float("inf"):
        print(f"fastest → {rows[0][1]}")
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
