#!/usr/bin/env python3
"""Lint .desktop files for common spin packaging mistakes."""
from __future__ import annotations
import argparse
import sys
from pathlib import Path


def lint(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    issues = []
    if "[Desktop Entry]" not in text:
        issues.append("missing [Desktop Entry]")
    required = ["Type", "Name", "Exec"]
    for key in required:
        if not any(line.startswith(f"{key}=") for line in text.splitlines()):
            issues.append(f"missing {key}=")
    for line in text.splitlines():
        if line.startswith("Exec="):
            cmd = line.split("=", 1)[1]
            if cmd.strip().startswith("sudo "):
                issues.append("Exec= starts with sudo")
            if not cmd.strip():
                issues.append("empty Exec=")
        if line.startswith("Icon=") and line.split("=", 1)[1].startswith("/"):
            # absolute icon paths often break across installs
            issues.append("Icon= uses absolute path (prefer icon name)")
        if line.startswith("Terminal=") and line.split("=", 1)[1].strip() not in ("true", "false"):
            issues.append("Terminal= must be true|false")
    if "TryExec=" in text:
        pass
    return issues


def main() -> int:
    p = argparse.ArgumentParser(description="Lint .desktop entries")
    p.add_argument("files", nargs="+", type=Path)
    args = p.parse_args()
    rc = 0
    for f in args.files:
        if not f.is_file():
            print(f"{f}: not a file", file=sys.stderr)
            rc = 2
            continue
        issues = lint(f)
        if not issues:
            print(f"OK  {f}")
        else:
            rc = 1
            print(f"FAIL {f}")
            for i in issues:
                print(f"  - {i}")
    return rc


if __name__ == "__main__":
    sys.exit(main())
