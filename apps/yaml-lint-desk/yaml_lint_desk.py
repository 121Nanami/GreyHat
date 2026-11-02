#!/usr/bin/env python3
"""Structural YAML sanity checks without PyYAML (indent/key heuristics)."""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

KEY = re.compile(r"^(\s*)([^:#\s][^:#]*?):\s*(.*)$")
LIST = re.compile(r"^(\s*)-\s+(.*)$")


def lint(text: str) -> list[str]:
    issues: list[str] = []
    indents: list[int] = []
    for i, line in enumerate(text.splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if "\t" in line:
            issues.append(f"L{i}: tab character (use spaces)")
        m = KEY.match(line) or LIST.match(line)
        if not m:
            if line.strip().startswith("---") or line.strip() == "...":
                continue
            # bare scalar continuation — allow
            continue
        sp = len(m.group(1).replace("\t", "    "))
        if sp % 2 != 0:
            issues.append(f"L{i}: odd indent {sp}")
        while indents and sp < indents[-1]:
            indents.pop()
        if indents and sp > indents[-1] and sp - indents[-1] not in (2, 4):
            issues.append(f"L{i}: jump indent {indents[-1]} → {sp}")
        if not indents or sp > indents[-1]:
            indents.append(sp)
        if KEY.match(line):
            key = KEY.match(line).group(2).strip()  # type: ignore
            if key.endswith(" "):
                issues.append(f"L{i}: trailing space in key")
            if line.rstrip().endswith(":"):
                pass
            # duplicate detection left shallow on purpose
    if not issues:
        issues.append("OK — no structural issues found (heuristic)")
    return issues


def main() -> int:
    p = argparse.ArgumentParser(description="Heuristic YAML lint (no PyYAML)")
    p.add_argument("file", type=Path, nargs="?", help="File (else stdin)")
    args = p.parse_args()
    text = args.file.read_text(encoding="utf-8") if args.file else sys.stdin.read()
    issues = lint(text)
    fatal = [x for x in issues if not x.startswith("OK")]
    for x in issues:
        print(x)
    return 1 if fatal else 0


if __name__ == "__main__":
    sys.exit(main())
