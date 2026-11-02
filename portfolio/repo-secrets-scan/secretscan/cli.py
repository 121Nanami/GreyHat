"""CLI for repo-secrets-scan."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .scanner import scan_tree


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="secretscan",
        description=(
            "Defensive secrets-in-repo scanner. Detects likely credentials in a local tree; "
            "does not exfiltrate, crack, or use discovered secrets."
        ),
    )
    p.add_argument("root", nargs="?", default=".", help="Directory to scan (default: .)")
    p.add_argument("-j", "--json", action="store_true", help="JSON report")
    p.add_argument("-q", "--quiet", action="store_true", help="Only print hits (no header)")
    p.add_argument("-V", "--version", action="version", version=f"secretscan {__version__}")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    root = Path(args.root)
    if not root.is_dir():
        print(f"not a directory: {root}", file=sys.stderr)
        return 2
    report = scan_tree(root)
    if args.json:
        json.dump(report.to_dict(), sys.stdout, indent=2)
        print()
    else:
        if not args.quiet:
            print(f"secretscan — root={report.root} files={report.files_scanned} hits={len(report.hits)}")
        for hit in report.hits:
            print(
                f"{hit.severity.upper():<7} {hit.rule_id:<22} {hit.path}:{hit.line}  {hit.excerpt}"
            )
        if not report.hits and not args.quiet:
            print("No likely secrets found.")
    return 1 if report.hits else 0


if __name__ == "__main__":
    sys.exit(main())
