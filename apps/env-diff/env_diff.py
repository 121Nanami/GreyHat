#!/usr/bin/env python3
"""Compare two .env-style files; never prints secret values by default."""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

ASSIGN = re.compile(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$")


def parse(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        m = ASSIGN.match(line)
        if not m:
            continue
        k, v = m.group(1), m.group(2).strip()
        if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
            v = v[1:-1]
        out[k] = v
    return out


def mask(v: str, show: bool) -> str:
    if show:
        return v
    if not v:
        return "(empty)"
    return f"<{len(v)} chars>"


def main() -> int:
    p = argparse.ArgumentParser(description="Diff two .env files (values masked by default)")
    p.add_argument("a", type=Path)
    p.add_argument("b", type=Path)
    p.add_argument("--show-values", action="store_true", help="Print actual values (careful)")
    args = p.parse_args()
    try:
        A, B = parse(args.a), parse(args.b)
    except OSError as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    only_a = sorted(set(A) - set(B))
    only_b = sorted(set(B) - set(A))
    changed = sorted(k for k in set(A) & set(B) if A[k] != B[k])
    same = sorted(k for k in set(A) & set(B) if A[k] == B[k])
    print(f"only in {args.a.name}: {len(only_a)}")
    for k in only_a:
        print(f"  - {k} = {mask(A[k], args.show_values)}")
    print(f"only in {args.b.name}: {len(only_b)}")
    for k in only_b:
        print(f"  + {k} = {mask(B[k], args.show_values)}")
    print(f"changed: {len(changed)}")
    for k in changed:
        print(f"  ~ {k}: {mask(A[k], args.show_values)} → {mask(B[k], args.show_values)}")
    print(f"unchanged: {len(same)}")
    return 1 if (only_a or only_b or changed) else 0


if __name__ == "__main__":
    sys.exit(main())
