#!/usr/bin/env python3
"""Print environment with secret-looking values redacted (safe to paste)."""
from __future__ import annotations
import argparse
import os
import re
import sys

SECRET_KEY = re.compile(
    r"(secret|token|password|passwd|api[_-]?key|auth|credential|private|bearer|cookie|session)",
    re.I,
)


def redact(k: str, v: str, show: int) -> str:
    if not SECRET_KEY.search(k):
        return v
    if show <= 0:
        return "***REDACTED***"
    if len(v) <= show * 2:
        return "***REDACTED***"
    return f"{v[:show]}…{v[-show:]}(redacted)"


def main() -> int:
    p = argparse.ArgumentParser(description="Dump env with secrets redacted")
    p.add_argument("-p", "--prefix", help="Only keys starting with PREFIX")
    p.add_argument("--show", type=int, default=0, help="Keep N chars at each end of secrets")
    args = p.parse_args()
    items = sorted(os.environ.items())
    for k, v in items:
        if args.prefix and not k.startswith(args.prefix):
            continue
        print(f"{k}={redact(k, v, args.show)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
