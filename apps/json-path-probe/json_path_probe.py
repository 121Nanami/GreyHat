#!/usr/bin/env python3
"""Query JSON with dotted paths and [index] segments (stdlib only)."""
from __future__ import annotations
import argparse
import json
import re
import sys
from typing import Any

SEG = re.compile(r"\.?([A-Za-z_][A-Za-z0-9_]*)|\[(\d+)\]")


def resolve(data: Any, path: str) -> Any:
    cur = data
    if path in ("", ".", "$"):
        return cur
    pos = 0
    if path.startswith("$"):
        path = path[1:]
    for m in SEG.finditer(path):
        if m.start() != pos:
            raise ValueError(f"bad path near {path[pos:]!r}")
        pos = m.end()
        if m.group(1) is not None:
            if not isinstance(cur, dict) or m.group(1) not in cur:
                raise KeyError(m.group(1))
            cur = cur[m.group(1)]
        else:
            idx = int(m.group(2))
            if not isinstance(cur, list) or idx >= len(cur):
                raise IndexError(idx)
            cur = cur[idx]
    if pos != len(path):
        raise ValueError(f"trailing junk: {path[pos:]!r}")
    return cur


def main() -> int:
    p = argparse.ArgumentParser(description="Dotted-path JSON probe")
    p.add_argument("path", help="e.g. .users[0].email or $.items[2]")
    p.add_argument("-f", "--file", type=argparse.FileType("r"), default="-")
    p.add_argument("-r", "--raw", action="store_true", help="Print strings without JSON quotes")
    args = p.parse_args()
    text = args.file.read()
    data = json.loads(text)
    try:
        val = resolve(data, args.path)
    except (KeyError, IndexError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    if args.raw and (isinstance(val, (str, int, float, bool)) or val is None):
        print(val)
    else:
        print(json.dumps(val, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
