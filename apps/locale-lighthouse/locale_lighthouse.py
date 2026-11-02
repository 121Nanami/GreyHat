#!/usr/bin/env python3
"""Suggest locale + timezone pairs for first-boot (Ellen Joe spin helper)."""
from __future__ import annotations
import argparse
import sys

REGIONS = {
    "us-west": ("en_US.UTF-8", "America/Los_Angeles", "US West Coast"),
    "us-east": ("en_US.UTF-8", "America/New_York", "US East Coast"),
    "uk": ("en_GB.UTF-8", "Europe/London", "United Kingdom"),
    "de": ("de_DE.UTF-8", "Europe/Berlin", "Germany"),
    "fr": ("fr_FR.UTF-8", "Europe/Paris", "France"),
    "jp": ("ja_JP.UTF-8", "Asia/Tokyo", "Japan"),
    "br": ("pt_BR.UTF-8", "America/Sao_Paulo", "Brazil"),
    "in": ("en_IN.UTF-8", "Asia/Kolkata", "India"),
    "utc": ("en_US.UTF-8", "UTC", "Coordinated Universal Time"),
}


def main() -> int:
    p = argparse.ArgumentParser(description="Locale Lighthouse — first-boot locale/TZ suggestions")
    p.add_argument("region", nargs="?", help="Region key, e.g. jp, us-west")
    p.add_argument("--list", action="store_true")
    args = p.parse_args()
    if args.list or not args.region:
        print("Regions:")
        for k, (loc, tz, label) in REGIONS.items():
            print(f"  {k:8}  {label:28}  {loc}  {tz}")
        if not args.region:
            return 0
    key = args.region.lower()
    if key not in REGIONS:
        print(f"Unknown region {args.region!r}. Try --list", file=sys.stderr)
        return 1
    loc, tz, label = REGIONS[key]
    print(f"# {label}")
    print(f"LANG={loc}")
    print(f"TZ={tz}")
    print(f"# timedatectl set-timezone {tz}")
    print(f"# localectl set-locale LANG={loc}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
