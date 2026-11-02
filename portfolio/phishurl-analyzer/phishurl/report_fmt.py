"""Human-readable report formatting."""

from __future__ import annotations

from .analyze import Report

BADGE = {
    "safe": "[SAFE]",
    "suspicious": "[SUSPICIOUS]",
    "dangerous": "[DANGEROUS]",
    "invalid": "[INVALID]",
}


def print_human(report: Report) -> None:
    badge = BADGE.get(report.verdict, "[?]")
    print(f"{badge} score={report.score}  {report.url}")
    if report.host:
        print(f"  host: {report.host}")
    for finding in report.findings:
        print(f"  - ({finding.severity}) {finding.code}: {finding.message}")


def print_summary_table(reports: list[Report]) -> None:
    print(f"{'VERDICT':<12} {'SCORE':>5}  URL")
    print("-" * 72)
    for r in reports:
        print(f"{r.verdict.upper():<12} {r.score:>5}  {r.url[:60]}")
    counts: dict[str, int] = {}
    for r in reports:
        counts[r.verdict] = counts.get(r.verdict, 0) + 1
    print("-" * 72)
    print("counts: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
