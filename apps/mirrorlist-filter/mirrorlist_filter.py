#!/usr/bin/env python3
"""Filter Arch mirrorlist by country comment / https-only / uncommented."""
from __future__ import annotations
import argparse
import sys
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description="Filter pacman mirrorlist")
    p.add_argument("file", nargs="?", type=Path, help="mirrorlist path (stdin if omitted)")
    p.add_argument("--country", action="append", default=[], help="Match ## Country header")
    p.add_argument("--https-only", action="store_true")
    p.add_argument("--enable", action="store_true", help="Strip leading # from Server lines that pass filters")
    p.add_argument("--servers-only", action="store_true", help="Emit Server lines only")
    args = p.parse_args()
    lines = (args.file.read_text(encoding="utf-8") if args.file else sys.stdin.read()).splitlines()
    country_ok = not args.country
    current_country = ""
    out = []
    for line in lines:
        if line.startswith("##"):
            current_country = line.lstrip("# ").strip()
            if args.country:
                country_ok = any(c.lower() in current_country.lower() for c in args.country)
            if not args.servers_only:
                out.append(line)
            continue
        stripped = line.lstrip("# ").strip()
        if stripped.startswith("Server"):
            if args.country and not country_ok:
                continue
            url = stripped.split("=", 1)[-1].strip() if "=" in stripped else ""
            if args.https_only and not url.startswith("https://"):
                continue
            if args.enable:
                out.append(f"Server = {url}" if url else stripped)
            else:
                out.append(line if not args.servers_only else (f"Server = {url}" if url else stripped))
            continue
        if not args.servers_only:
            out.append(line)
    print("\n".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
