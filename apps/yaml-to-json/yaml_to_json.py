#!/usr/bin/env python3
"""Minimal YAML subset → JSON (no PyYAML required). Supports maps/lists/scalars."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path


def parse_scalar(s: str):
    s = s.strip()
    if s in ("null", "~", ""):
        return None
    if s in ("true", "True"):
        return True
    if s in ("false", "False"):
        return False
    if (s.startswith('"') and s.endswith('"')) or (s.startswith("'") and s.endswith("'")):
        return s[1:-1]
    try:
        if "." in s:
            return float(s)
        return int(s)
    except ValueError:
        return s


def parse_yaml(text: str):
    """Tiny indentation-based subset parser — good enough for simple configs."""
    lines = []
    for raw in text.splitlines():
        if not raw.strip() or raw.strip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        lines.append((indent, raw.strip()))

    def parse_block(i: int, indent: int):
        if i >= len(lines):
            return None, i
        _, content = lines[i]
        if content.startswith("- "):
            out = []
            while i < len(lines) and lines[i][0] == indent and lines[i][1].startswith("- "):
                item = lines[i][1][2:]
                if item == "" or item.endswith(":"):
                    key = item[:-1] if item.endswith(":") else None
                    child, i = parse_block(i + 1, indent + 2)
                    if key:
                        out.append({key: child})
                    else:
                        out.append(child)
                elif ":" in item and not item.startswith("{"):
                    k, v = item.split(":", 1)
                    if v.strip() == "":
                        child, i = parse_block(i + 1, indent + 2)
                        out.append({k.strip(): child})
                    else:
                        out.append({k.strip(): parse_scalar(v)})
                        i += 1
                else:
                    out.append(parse_scalar(item))
                    i += 1
            return out, i
        # mapping
        out = {}
        while i < len(lines) and lines[i][0] == indent:
            _, content = lines[i]
            if content.startswith("- "):
                break
            if ":" not in content:
                raise ValueError(f"Expected key: value at {content!r}")
            k, v = content.split(":", 1)
            k = k.strip()
            if v.strip() == "":
                child, i = parse_block(i + 1, indent + 2)
                out[k] = child
            else:
                out[k] = parse_scalar(v)
                i += 1
        return out, i

    if not lines:
        return None
    node, _ = parse_block(0, lines[0][0])
    return node


def main() -> int:
    p = argparse.ArgumentParser(description="Minimal YAML → JSON (no deps)")
    p.add_argument("path", nargs="?", type=Path)
    p.add_argument("--pretty", action="store_true")
    args = p.parse_args()
    text = args.path.read_text() if args.path else sys.stdin.read()
    try:
        data = parse_yaml(text)
    except Exception as e:
        print(f"Parse error: {e}", file=sys.stderr)
        return 1
    print(json.dumps(data, indent=2 if args.pretty else None, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
