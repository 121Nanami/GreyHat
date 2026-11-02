"""CLI entry for phishurl-analyzer."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .analyze import analyze
from .report_fmt import print_human, print_summary_table


def _load_list(path: str | None) -> set[str]:
    if not path:
        return set()
    entries: set[str] = set()
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip().lower()
        if line and not line.startswith("#"):
            entries.add(line)
    return entries


def _iter_urls(args: argparse.Namespace) -> list[str]:
    urls: list[str] = []
    urls.extend(args.urls or [])
    if args.file:
        for line in Path(args.file).read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#"):
                urls.append(line)
    if args.stdin or (not urls and not sys.stdin.isatty()):
        for line in sys.stdin:
            line = line.strip()
            if line and not line.startswith("#"):
                urls.append(line)
    return urls


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="phishurl",
        description=(
            "Offline phishing URL analyzer (defensive). "
            "Never fetches remote hosts; analyzes only the URL string you supply."
        ),
    )
    p.add_argument("urls", nargs="*", help="URL(s) to check")
    p.add_argument("-f", "--file", help="Read URLs from a file (one per line)")
    p.add_argument("--stdin", action="store_true", help="Read URLs from stdin")
    p.add_argument("--allowlist", help="Host allowlist file (one host/suffix per line)")
    p.add_argument("--blocklist", help="Host blocklist file (one host/suffix per line)")
    p.add_argument("-j", "--json", action="store_true", help="Emit JSON")
    p.add_argument("-q", "--quiet", action="store_true", help="Verdict-only text lines")
    p.add_argument(
        "--summary",
        action="store_true",
        help="Print a compact table summarizing a batch",
    )
    p.add_argument("-V", "--version", action="version", version=f"phishurl {__version__}")
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    urls = _iter_urls(args)
    if not urls:
        parser.error("provide a URL, --file, or pipe URLs on stdin")

    allow = _load_list(args.allowlist)
    block = _load_list(args.blocklist)
    reports = [analyze(u, allowlist=allow, blocklist=block) for u in urls]

    worst = 0
    for report in reports:
        if report.verdict in {"dangerous", "invalid"}:
            worst = max(worst, 2)
        elif report.verdict == "suspicious":
            worst = max(worst, 1)

    if args.json:
        payload = [r.to_dict() for r in reports]
        json.dump(payload if len(payload) > 1 else payload[0], sys.stdout, indent=2)
        print()
    elif args.summary:
        print_summary_table(reports)
    else:
        for i, report in enumerate(reports):
            if args.quiet:
                print(f"{report.verdict.upper()}\t{report.score}\t{report.url}")
            else:
                print_human(report)
                if i < len(reports) - 1:
                    print()
    return worst


if __name__ == "__main__":
    sys.exit(main())
