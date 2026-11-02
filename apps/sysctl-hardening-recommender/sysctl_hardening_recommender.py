#!/usr/bin/env python3
"""Read-only sysctl hardening advice for a desktop / spin install."""
from __future__ import annotations
import argparse
import sys

# Advice catalog — never writes /etc/sysctl.d
ADVICE = [
    {
        "key": "kernel.kptr_restrict",
        "want": "1 or 2",
        "why": "Hide kernel pointers from unprivileged users (mitigate local info leaks).",
        "risk": "Some diagnostics harder; prefer 1 on desktops, 2 on locked-down hosts.",
    },
    {
        "key": "kernel.dmesg_restrict",
        "want": "1",
        "why": "Restrict dmesg to CAP_SYSLOG — reduces kernel log mining.",
        "risk": "Normal users cannot read dmesg; admins still can.",
    },
    {
        "key": "kernel.unprivileged_bpf_disabled",
        "want": "1",
        "why": "Block unprivileged BPF (common exploit gadget surface).",
        "risk": "Breaks some sandboxes/tracing tools for non-root; root unaffected.",
    },
    {
        "key": "net.ipv4.conf.all.rp_filter",
        "want": "1 (or 2)",
        "why": "Reverse-path filtering reduces spoofed packet acceptance.",
        "risk": "Asymmetric routing setups may need 2 or per-iface exceptions.",
    },
    {
        "key": "net.ipv4.conf.all.accept_redirects",
        "want": "0",
        "why": "Ignore ICMP redirects that can poison routes on hostile networks.",
        "risk": "Rarely needed on single-homed desktops.",
    },
    {
        "key": "net.ipv4.conf.all.send_redirects",
        "want": "0",
        "why": "Do not act as a router sending redirects unless you are one.",
        "risk": "None on non-router hosts.",
    },
    {
        "key": "net.ipv6.conf.all.accept_ra",
        "want": "0 on servers; careful on dual-stack laptops",
        "why": "Router advertisements can rewrite routes on hostile links.",
        "risk": "Disabling may break SLAAC; use NetworkManager profiles instead if unsure.",
    },
    {
        "key": "fs.protected_hardlinks / fs.protected_symlinks",
        "want": "1",
        "why": "Classic /tmp link race protections (usually already default).",
        "risk": "Legacy broken software expecting unrestricted links.",
    },
    {
        "key": "kernel.yama.ptrace_scope",
        "want": "1+",
        "why": "Limit ptrace attach — harder debugger-based credential theft.",
        "risk": "Debugging your own processes may need echo 0 temporarily.",
    },
    {
        "key": "vm.mmap_min_addr",
        "want": "65536 (or distro default ≥)",
        "why": "Block mapping the zero page (NULL deref exploit class).",
        "risk": "Ancient binaries that mmap low addresses.",
    },
]


def main() -> int:
    p = argparse.ArgumentParser(description="Read-only sysctl hardening recommender")
    p.add_argument("--json", action="store_true", help="Emit JSON")
    p.add_argument("-q", "--quiet", action="store_true", help="Keys + want only")
    args = p.parse_args()
    if args.json:
        import json
        print(json.dumps(ADVICE, indent=2))
        return 0
    print("Sysctl hardening recommender — ADVICE ONLY (does not write sysctl)\n")
    for i, a in enumerate(ADVICE, 1):
        if args.quiet:
            print(f"{a['key']} → {a['want']}")
            continue
        print(f"{i:2d}. {a['key']}")
        print(f"    prefer: {a['want']}")
        print(f"    why:    {a['why']}")
        print(f"    risk:   {a['risk']}\n")
    print("Apply manually via /etc/sysctl.d/ after reviewing each key.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
