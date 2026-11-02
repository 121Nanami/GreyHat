#!/usr/bin/env python3
"""Interactive TUI checklist for auditing packages on a custom Arch/BlackArch spin."""
from __future__ import annotations
import json
import sys
from pathlib import Path

CHECKS = [
    ("orphans", "Review orphaned packages (pacman -Qdt)"),
    ("foreign", "List foreign / AUR packages (pacman -Qm)"),
    ("explicit", "Audit explicitly installed set (pacman -Qe)"),
    ("sigs", "Confirm SigLevel / keyring healthy"),
    ("mirrors", "Mirrorlist freshness + rankmirrors run"),
    ("blacklist", "No known-problem packages from spin denylist"),
    ("docs", "Tools ship README + license in /usr/share/doc"),
    ("desktop", "Desktop entries point at real binaries"),
    ("services", "No unexpected enabled systemd units"),
    ("perms", "World-writable files under /usr absent"),
]

STATE = Path.home() / ".cache" / "greyhatinc-package-audit.json"


def load() -> dict:
    if STATE.is_file():
        return json.loads(STATE.read_text())
    return {k: False for k, _ in CHECKS}


def save(state: dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(state, indent=2) + "\n")


def render(state: dict) -> None:
    done = sum(1 for k, _ in CHECKS if state.get(k))
    print("\n╔══════════════════════════════════════════════╗")
    print("║  Package Audit Checklist  (Arch / spin)      ║")
    print(f"║  Progress: {done}/{len(CHECKS)}                              ║"[:49] + "║")
    print("╚══════════════════════════════════════════════╝")
    for i, (key, label) in enumerate(CHECKS, 1):
        mark = "✔" if state.get(key) else "·"
        print(f"  [{mark}] {i:2d}. {label}")
    print("\n  Commands: <n> toggle · a all-done · r reset · q quit\n")


def main() -> int:
    state = load()
    while True:
        render(state)
        try:
            cmd = input("> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if cmd in ("q", "quit"):
            break
        if cmd == "a":
            for k, _ in CHECKS:
                state[k] = True
            save(state)
            continue
        if cmd == "r":
            state = {k: False for k, _ in CHECKS}
            save(state)
            continue
        if cmd.isdigit():
            i = int(cmd)
            if 1 <= i <= len(CHECKS):
                k = CHECKS[i - 1][0]
                state[k] = not state.get(k)
                save(state)
            continue
        print("  (unknown command)")
    save(state)
    print(f"Saved → {STATE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
