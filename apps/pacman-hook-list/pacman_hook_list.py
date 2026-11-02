#!/usr/bin/env python3
"""List and summarize pacman hooks under /usr/share/libalpm/hooks (and custom dirs)."""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

DEFAULT_DIRS = [
    Path("/usr/share/libalpm/hooks"),
    Path("/etc/pacman.d/hooks"),
]


def parse_hook(path: Path) -> dict[str, list[str]]:
    data: dict[str, list[str]] = {}
    section = None
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith("[") and s.endswith("]"):
            section = s[1:-1]
            continue
        if "=" in s and section:
            k, v = s.split("=", 1)
            data.setdefault(f"{section}.{k.strip()}", []).append(v.strip())
    return data


def main() -> int:
    p = argparse.ArgumentParser(description="Summarize pacman hooks")
    p.add_argument("dirs", nargs="*", type=Path, default=DEFAULT_DIRS)
    args = p.parse_args()
    found = 0
    for d in args.dirs:
        if not d.is_dir():
            print(f"# skip missing {d}", file=sys.stderr)
            continue
        for path in sorted(d.glob("*.hook")):
            found += 1
            meta = parse_hook(path)
            desc = (meta.get("Trigger.Target") or meta.get("Action.Description") or
                    meta.get("Trigger.Type") or ["(no description)"])
            when = ",".join(meta.get("Trigger.Operation", []) ) or "?"
            typ = ",".join(meta.get("Trigger.Type", [])) or "?"
            print(f"{path.name:40s}  {when:12s}  {typ:10s}  {path}")
            for t in meta.get("Trigger.Target", [])[:5]:
                print(f"  target: {t}")
            for dline in meta.get("Action.Description", []):
                print(f"  desc: {dline}")
            print()
    if found == 0:
        print("No .hook files found (dirs may be empty on non-Arch hosts).", file=sys.stderr)
        return 1
    print(f"# {found} hook(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
