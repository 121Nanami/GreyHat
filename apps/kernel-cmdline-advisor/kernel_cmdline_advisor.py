#!/usr/bin/env python3
"""Explain common kernel cmdline hardening flags (read-only advisor)."""
from __future__ import annotations
import argparse
import sys

FLAGS = {
    "mitigations=auto": "Default Spectre/Meltdown mitigation set (safe baseline).",
    "mitigations=off": "Disables CPU mitigations — faster, less safe. Avoid on hostile multi-user hosts.",
    "slab_nomerge": "Reduce heap overflow merging tricks; tiny memory cost.",
    "init_on_alloc=1": "Zero memory on alloc — mitigates some info leaks; CPU cost.",
    "init_on_free=1": "Zero on free — stronger, more CPU cost than alloc-only.",
    "page_alloc.shuffle=1": "Shuffle free lists — harder predictable placement.",
    "pti=on": "Force page-table isolation (usually already on).",
    "spectre_v2=on": "Force Spectre v2 mitigations.",
    "randomize_kstack_offset=on": "Kernel stack offset noise.",
    "vsyscall=none": "Disable vsyscall page (breaks ancient binaries).",
    "module.sig_enforce=1": "Load only signed modules (needs signed modules).",
    "quiet splash": "Cosmetic — hides boot logs; not a security control.",
}


def main() -> int:
    p = argparse.ArgumentParser(description="Kernel cmdline flag advisor")
    p.add_argument("flags", nargs="*", help="Flags to explain (default: catalog)")
    p.add_argument("--list", action="store_true", help="List known flags")
    args = p.parse_args()
    if args.list or not args.flags:
        for k, v in FLAGS.items():
            print(f"{k}\n  {v}\n")
        return 0
    rc = 0
    for raw in args.flags:
        key = raw
        if key in FLAGS:
            print(f"{key}\n  {FLAGS[key]}\n")
            continue
        # try prefix match before =
        base = raw.split("=", 1)[0]
        hits = [(k, v) for k, v in FLAGS.items() if k.startswith(base)]
        if hits:
            for k, v in hits:
                print(f"{k}\n  {v}\n")
        else:
            print(f"{raw}\n  (unknown to this advisor — research before applying)\n", file=sys.stderr)
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main())
