#!/usr/bin/env python3
"""Generate a Markdown table of contents from headings."""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

HEAD = re.compile(r"^(#{1,6})\s+(.*)$")


def slug(text: str) -> str:
    s = text.strip().lower()
    s = re.sub(r"[^\w\s-]", "", s)
    return re.sub(r"\s+", "-", s)


def main() -> int:
    p = argparse.ArgumentParser(description="Markdown TOC generator")
    p.add_argument("file", type=Path, nargs="?", help="Markdown file (else stdin)")
    p.add_argument("--min", type=int, default=1)
    p.add_argument("--max", type=int, default=3)
    args = p.parse_args()
    text = args.file.read_text(encoding="utf-8") if args.file else sys.stdin.read()
    in_fence = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if in_fence:
            continue
        m = HEAD.match(line)
        if not m:
            continue
        level = len(m.group(1))
        if level < args.min or level > args.max:
            continue
        title = m.group(2).strip()
        print(f"{'  ' * (level - args.min)}- [{title}](#{slug(title)})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
