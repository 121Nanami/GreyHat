#!/usr/bin/env python3
"""Explain chmod octal / symbolic modes in plain language."""
from __future__ import annotations
import argparse
import re
import sys

BITS = [
    (0o400, "owner read"),
    (0o200, "owner write"),
    (0o100, "owner execute"),
    (0o040, "group read"),
    (0o020, "group write"),
    (0o010, "group execute"),
    (0o004, "other read"),
    (0o002, "other write"),
    (0o001, "other execute"),
]
SPECIAL = [(0o4000, "setuid"), (0o2000, "setgid"), (0o1000, "sticky")]


def from_octal(s: str) -> int:
    return int(s, 8)


def explain(mode: int) -> None:
    print(f"octal: {oct(mode)}")
    print(f"rwx:   {mode_to_rwx(mode)}")
    for bit, label in SPECIAL + BITS:
        if mode & bit:
            print(f"  + {label}")


def mode_to_rwx(mode: int) -> str:
    chars = []
    for who_shift in (6, 3, 0):
        triad = (mode >> who_shift) & 0o7
        chars.append("r" if triad & 4 else "-")
        chars.append("w" if triad & 2 else "-")
        chars.append("x" if triad & 1 else "-")
    # special bits overlay
    if mode & 0o4000:
        chars[2] = "s" if chars[2] == "x" else "S"
    if mode & 0o2000:
        chars[5] = "s" if chars[5] == "x" else "S"
    if mode & 0o1000:
        chars[8] = "t" if chars[8] == "x" else "T"
    return "".join(chars)


def main() -> int:
    p = argparse.ArgumentParser(description="Explain chmod modes")
    p.add_argument("mode", help="Octal like 755 or 0755, or rwx string like rwxr-xr-x")
    args = p.parse_args()
    m = args.mode
    if re.fullmatch(r"[0-7]{3,4}", m):
        explain(from_octal(m))
        return 0
    if re.fullmatch(r"[r-][w-][xsS-][r-][w-][xsS-][r-][w-][xtT-]", m):
        mode = 0
        mapbits = [
            (0, 0o400, "r"), (1, 0o200, "w"), (2, 0o100, "x"),
            (3, 0o040, "r"), (4, 0o020, "w"), (5, 0o010, "x"),
            (6, 0o004, "r"), (7, 0o002, "w"), (8, 0o001, "x"),
        ]
        for idx, bit, ch in mapbits:
            if m[idx] in (ch, "s", "S", "t", "T") and m[idx] not in "-":
                if m[idx] in "xstST" and ch == "x":
                    if m[idx] in "xst":
                        mode |= bit
                elif m[idx] == ch:
                    mode |= bit
        if m[2] in "sS":
            mode |= 0o4000
        if m[5] in "sS":
            mode |= 0o2000
        if m[8] in "tT":
            mode |= 0o1000
        explain(mode)
        return 0
    print("error: expected octal (755) or rwx string", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main())
