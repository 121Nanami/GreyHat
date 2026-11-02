#!/usr/bin/env python3
"""Stub wallpaper pack manager for an Ellen Joe–themed spin (list/install/remove metadata)."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

PACKS = {
    "ellen-deep-sea": {
        "title": "Ellen Deep Sea",
        "count": 8,
        "res": "3840x2160",
        "note": "Abyssal blues, shark-tooth motifs, soft grain",
    },
    "neon-harbor": {
        "title": "Neon Harbor",
        "count": 6,
        "res": "2560x1440",
        "note": "Rain-slick docks, magenta sodium lamps",
    },
    "mono-terminal": {
        "title": "Mono Terminal",
        "count": 4,
        "res": "1920x1080",
        "note": "Minimal CRT green / phosphor black",
    },
}

DB = Path.home() / ".cache" / "greyhatinc-wallpaper-packs.json"


def load() -> dict:
    if DB.is_file():
        return json.loads(DB.read_text())
    return {"installed": []}


def save(state: dict) -> None:
    DB.parent.mkdir(parents=True, exist_ok=True)
    DB.write_text(json.dumps(state, indent=2) + "\n")


def main() -> int:
    p = argparse.ArgumentParser(description="Wallpaper pack manager stub (metadata only)")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list", help="List available packs")
    sub.add_parser("status", help="Show installed stubs")
    i = sub.add_parser("install", help="Mark pack installed (stub)")
    i.add_argument("pack")
    r = sub.add_parser("remove", help="Mark pack removed (stub)")
    r.add_argument("pack")
    args = p.parse_args()
    state = load()

    if args.cmd == "list":
        for pid, meta in PACKS.items():
            flag = "*" if pid in state["installed"] else " "
            print(f"[{flag}] {pid:20s} {meta['title']} · {meta['count']} imgs · {meta['res']}")
            print(f"     {meta['note']}")
        return 0
    if args.cmd == "status":
        print("installed:", ", ".join(state["installed"]) or "(none)")
        print(f"db: {DB}")
        return 0
    if args.cmd == "install":
        if args.pack not in PACKS:
            print("unknown pack", file=sys.stderr)
            return 1
        if args.pack not in state["installed"]:
            state["installed"].append(args.pack)
            save(state)
        print(f"stub-installed {args.pack} (no files copied)")
        return 0
    if args.cmd == "remove":
        state["installed"] = [x for x in state["installed"] if x != args.pack]
        save(state)
        print(f"stub-removed {args.pack}")
        return 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
