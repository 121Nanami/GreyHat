#!/usr/bin/env python3
"""Tiny unit converter oracle."""
from __future__ import annotations
import argparse
import sys

# to SI base-ish
LENGTH = {"m": 1.0, "km": 1000, "cm": 0.01, "mm": 0.001, "mi": 1609.344, "ft": 0.3048, "in": 0.0254, "yd": 0.9144}
MASS = {"kg": 1.0, "g": 0.001, "lb": 0.45359237, "oz": 0.028349523125, "t": 1000}
TEMP = {"c", "f", "k"}


def convert_temp(v: float, src: str, dst: str) -> float:
    # to C
    if src == "c":
        c = v
    elif src == "f":
        c = (v - 32) * 5 / 9
    else:
        c = v - 273.15
    if dst == "c":
        return c
    if dst == "f":
        return c * 9 / 5 + 32
    return c + 273.15


def convert(v: float, src: str, dst: str) -> float:
    src, dst = src.lower(), dst.lower()
    if src in TEMP and dst in TEMP:
        return convert_temp(v, src, dst)
    for table in (LENGTH, MASS):
        if src in table and dst in table:
            return v * table[src] / table[dst]
    raise SystemExit(f"Cannot convert {src} → {dst}. Known: {sorted(LENGTH)|sorted(MASS)|sorted(TEMP)}")


def main() -> int:
    p = argparse.ArgumentParser(description="Convert units: VALUE FROM to TO")
    p.add_argument("value", type=float)
    p.add_argument("src")
    p.add_argument("to_word", nargs="?", default="to", help="literal 'to' (optional)")
    p.add_argument("dst")
    args = p.parse_args()
    dst = args.dst if args.to_word.lower() == "to" else args.to_word
    # allow: 10 km to mi   OR  10 km mi
    if args.to_word.lower() != "to":
        dst = args.to_word
    result = convert(args.value, args.src, dst)
    print(f"{args.value:g} {args.src} = {result:.6g} {dst}")
    return 0


if __name__ == "__main__":
    # Fix argv for "10 km to mi" style
    sys.exit(main())
