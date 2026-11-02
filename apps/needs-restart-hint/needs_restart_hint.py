#!/usr/bin/env python3
"""Heuristic 'reboot advised?' hints for Arch-like systems (read-only)."""
from __future__ import annotations
import argparse
import os
import sys
from pathlib import Path


def main() -> int:
    p = argparse.ArgumentParser(description="Reboot-needed heuristics (advice only)")
    args = p.parse_args()
    hints = []
    boot_id = Path("/proc/sys/kernel/random/boot_id")
    if boot_id.is_file():
        hints.append(f"boot_id: {boot_id.read_text().strip()}")
    # kernel vs running
    uname = Path("/proc/version")
    if uname.is_file():
        hints.append(f"running: {uname.read_text().strip()[:120]}…")
    pkg_kernel = None
    for cand in Path("/usr/lib/modules").glob("*"):
        if cand.is_dir():
            pkg_kernel = cand.name
            break
    if pkg_kernel:
        hints.append(f"modules dir present: {pkg_kernel}")
        running = os.uname().release
        if pkg_kernel != running and Path("/usr/lib/modules", running).exists() is False:
            hints.append(f"NOTE: uname.release={running} may differ from newest modules tree {pkg_kernel}")
        elif pkg_kernel != running:
            # both exist — still useful
            hints.append(f"uname.release={running}; saw modules/{pkg_kernel}")
    # pacman marker used by some tools
    for marker in (Path("/var/run/reboot-required"), Path("/run/reboot-required")):
        if marker.exists():
            hints.append(f"found marker: {marker}")
    if Path("/usr/bin/needs-restarting").is_file():
        hints.append("needs-restarting binary present (rpm systems) — not invoked")
    print("Needs-restart hint (heuristic, non-authoritative)\n")
    if not hints:
        print("No signals found (maybe not Linux, or restricted /proc).")
        return 0
    for h in hints:
        print(f"· {h}")
    print("\nAdvice only — decide reboot based on changelog / admin policy.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
