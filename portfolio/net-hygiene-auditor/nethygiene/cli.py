"""CLI for net-hygiene-auditor."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .checks import run_audit


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="nethygiene",
        description=(
            "Read-only local network hygiene auditor. "
            "Inspects resolv.conf, hosts, listening sockets via /proc, SSH key perms, and PATH — "
            "never connects outbound or modifies configuration."
        ),
    )
    p.add_argument("--resolv", type=Path, help="Override path to resolv.conf")
    p.add_argument("--hosts", type=Path, help="Override path to hosts file")
    p.add_argument("--ssh-dir", type=Path, help="Override path to SSH directory")
    p.add_argument("--skip-listen", action="store_true", help="Skip /proc listening socket parse")
    p.add_argument("-j", "--json", action="store_true", help="JSON report")
    p.add_argument("-V", "--version", action="version", version=f"nethygiene {__version__}")
    return p


def print_human(report) -> None:
    print(f"net-hygiene audit — host={report.hostname}")
    if report.listening:
        print(f"\nListening TCP ({len(report.listening)}):")
        for row in report.listening[:30]:
            print(f"  {row['proto']:<6} {row['address']}:{row['port']}  bind={row['bind']}")
        if len(report.listening) > 30:
            print(f"  … {len(report.listening) - 30} more")
    print("\nFindings:")
    for f in report.findings:
        ev = f" [{f.evidence}]" if f.evidence else ""
        print(f"  ({f.severity}) {f.check}: {f.message}{ev}")
    summary = {}
    for f in report.findings:
        summary[f.severity] = summary.get(f.severity, 0) + 1
    print("\nSummary: " + ", ".join(f"{k}={v}" for k, v in sorted(summary.items())))


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    report = run_audit(
        resolv=args.resolv,
        hosts=args.hosts,
        ssh_dir=args.ssh_dir,
        skip_listen=args.skip_listen,
    )
    if args.json:
        json.dump(report.to_dict(), sys.stdout, indent=2)
        print()
    else:
        print_human(report)
    # Exit 1 if any high findings
    if any(f.severity == "high" for f in report.findings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
