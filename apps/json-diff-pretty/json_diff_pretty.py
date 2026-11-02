#!/usr/bin/env python3
"""Pretty structural JSON diff."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
from typing import Any


def walk(a: Any, b: Any, path: str = "$") -> list[str]:
    lines: list[str] = []
    if type(a) != type(b) or (isinstance(a, dict) and set(a) != set(b)):
        if isinstance(a, dict) and isinstance(b, dict):
            for k in sorted(set(a) | set(b)):
                p = f"{path}.{k}"
                if k not in a:
                    lines.append(f"+ {p} = {json.dumps(b[k])}")
                elif k not in b:
                    lines.append(f"- {p} = {json.dumps(a[k])}")
                else:
                    lines.extend(walk(a[k], b[k], p))
            return lines
        if isinstance(a, list) and isinstance(b, list):
            n = max(len(a), len(b))
            for i in range(n):
                p = f"{path}[{i}]"
                if i >= len(a):
                    lines.append(f"+ {p} = {json.dumps(b[i])}")
                elif i >= len(b):
                    lines.append(f"- {p} = {json.dumps(a[i])}")
                else:
                    lines.extend(walk(a[i], b[i], p))
            return lines
        lines.append(f"~ {path}: {json.dumps(a)} → {json.dumps(b)}")
        return lines
    if isinstance(a, dict):
        for k in sorted(a):
            lines.extend(walk(a[k], b[k], f"{path}.{k}"))
    elif isinstance(a, list):
        for i, (x, y) in enumerate(zip(a, b)):
            lines.extend(walk(x, y, f"{path}[{i}]"))
        if len(a) != len(b):
            longer, shorter, sign = (b, a, "+") if len(b) > len(a) else (a, b, "-")
            for i in range(len(shorter), len(longer)):
                lines.append(f"{sign} {path}[{i}] = {json.dumps(longer[i])}")
    elif a != b:
        lines.append(f"~ {path}: {json.dumps(a)} → {json.dumps(b)}")
    return lines


def main() -> int:
    p = argparse.ArgumentParser(description="Pretty JSON diff")
    p.add_argument("a", type=Path)
    p.add_argument("b", type=Path)
    args = p.parse_args()
    left = json.loads(args.a.read_text())
    right = json.loads(args.b.read_text())
    diffs = walk(left, right)
    if not diffs:
        print("No differences.")
        return 0
    for line in diffs:
        color = "\033[32m" if line.startswith("+") else "\033[31m" if line.startswith("-") else "\033[33m"
        print(f"{color}{line}\033[0m")
    return 1


if __name__ == "__main__":
    sys.exit(main())
