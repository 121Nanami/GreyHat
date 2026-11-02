#!/usr/bin/env python3
"""Lightweight mirror latency/speed sampler for Arch-style mirrorlists."""
from __future__ import annotations
import argparse
import statistics
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

DEFAULT = [
    "https://geo.mirror.pkgbuild.com/",
    "https://mirror.rackspace.com/archlinux/",
    "https://mirrors.kernel.org/archlinux/",
]


def probe(url: str, timeout: float) -> tuple[str, float | None, str]:
    target = url if url.endswith("/") else url + "/"
    # Prefer a small well-known file when present; fall back to HEAD/GET of root
    candidates = [target + "lastupdate", target + "core/os/x86_64/core.db", target]
    last_err = "no attempt"
    for c in candidates:
        t0 = time.perf_counter()
        try:
            req = urllib.request.Request(c, method="GET", headers={"User-Agent": "greyhatinc-mirror-speed/0.1"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                resp.read(65536)
            ms = (time.perf_counter() - t0) * 1000
            return url, ms, "ok"
        except Exception as e:  # noqa: BLE001 — surface any probe failure
            last_err = f"{type(e).__name__}: {e}"
    return url, None, last_err


def main() -> int:
    p = argparse.ArgumentParser(description="Sample mirror latency (network required)")
    p.add_argument("mirrors", nargs="*", default=DEFAULT, help="Mirror base URLs")
    p.add_argument("-t", "--timeout", type=float, default=5.0)
    p.add_argument("-j", "--jobs", type=int, default=4)
    p.add_argument("-n", "--rounds", type=int, default=1, help="Rounds per mirror (median)")
    args = p.parse_args()

    results = []
    with ThreadPoolExecutor(max_workers=max(1, args.jobs)) as ex:
        futs = []
        for m in args.mirrors:
            for _ in range(max(1, args.rounds)):
                futs.append(ex.submit(probe, m, args.timeout))
        by: dict[str, list[float]] = {m: [] for m in args.mirrors}
        errs: dict[str, str] = {}
        for fut in as_completed(futs):
            url, ms, status = fut.result()
            if ms is None:
                errs[url] = status
            else:
                by[url].append(ms)

    rows = []
    for url in args.mirrors:
        if by[url]:
            rows.append((statistics.median(by[url]), url, "ok"))
        else:
            rows.append((float("inf"), url, errs.get(url, "fail")))
    rows.sort()
    print(f"{'ms':>8}  mirror")
    for ms, url, st in rows:
        if ms == float("inf"):
            print(f"{'FAIL':>8}  {url}  ({st})")
        else:
            print(f"{ms:8.1f}  {url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
