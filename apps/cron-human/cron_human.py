#!/usr/bin/env python3
"""Translate a 5-field cron expression into plain English."""
from __future__ import annotations
import argparse
import sys

DOW = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
MON = ["", "January", "February", "March", "April", "May", "June",
       "July", "August", "September", "October", "November", "December"]


def part(label: str, field: str, names: list[str] | None = None) -> str:
    if field == "*":
        return f"every {label}"
    if field.startswith("*/"):
        return f"every {field[2:]} {label}s"
    if "," in field:
        bits = [names[int(x)] if names and x.isdigit() else x for x in field.split(",")]
        return f"{label} in {', '.join(bits)}"
    if "-" in field and "/" not in field:
        a, b = field.split("-", 1)
        if names and a.isdigit() and b.isdigit():
            return f"{label} from {names[int(a)]} to {names[int(b)]}"
        return f"{label} from {a} to {b}"
    if names and field.isdigit():
        return f"{label} {names[int(field)]}"
    return f"{label} {field}"


def explain(expr: str) -> str:
    bits = expr.split()
    if len(bits) != 5:
        raise ValueError("need 5 fields: min hour dom mon dow")
    minute, hour, dom, mon, dow = bits
    chunks = [
        part("minute", minute),
        part("hour", hour),
        part("day-of-month", dom),
        part("month", mon, MON),
        part("weekday", dow, DOW),
    ]
    return "; ".join(chunks)


def main() -> int:
    p = argparse.ArgumentParser(description="Cron → English")
    p.add_argument("expr", nargs="+", help="5-field cron (quote it)")
    args = p.parse_args()
    expr = " ".join(args.expr)
    try:
        print(explain(expr))
    except ValueError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
