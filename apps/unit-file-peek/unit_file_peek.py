#!/usr/bin/env python3
"""Summarize a systemd unit file: sections, Exec*, User, dangerous-looking flags."""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

ASSIGN = re.compile(r"^([A-Za-z][A-Za-z0-9]*)=(.*)$")


def main() -> int:
    p = argparse.ArgumentParser(description="Summarize systemd unit file")
    p.add_argument("unit", type=Path)
    args = p.parse_args()
    if not args.unit.is_file():
        print(f"error: {args.unit} not found", file=sys.stderr)
        return 2
    section = None
    data: dict[str, dict[str, list[str]]] = {}
    for line in args.unit.read_text(encoding="utf-8", errors="replace").splitlines():
        s = line.strip()
        if not s or s.startswith("#") or s.startswith(";"):
            continue
        if s.startswith("[") and s.endswith("]"):
            section = s[1:-1]
            data.setdefault(section, {})
            continue
        m = ASSIGN.match(s)
        if not m or section is None:
            continue
        data[section].setdefault(m.group(1), []).append(m.group(2))

    print(f"unit: {args.unit.name}")
    print(f"sections: {', '.join(data) or '(none)'}")
    for key in ("Description", "Documentation", "User", "Group", "Type", "WantedBy", "RequiredBy"):
        for sec, kv in data.items():
            if key in kv:
                for v in kv[key]:
                    print(f"  {key}: {v}  [{sec}]")
    print("exec:")
    for sec, kv in data.items():
        for k, vs in kv.items():
            if k.startswith("Exec"):
                for v in vs:
                    print(f"  {k}={v}")
    hints = []
    for sec, kv in data.items():
        if kv.get("User") == ["root"] or (sec == "Service" and "User" not in kv and any(k.startswith("Exec") for k in kv)):
            if "User" not in kv:
                hints.append("Service has no User= (runs as root by default for system units)")
        if any(v.strip() == "/bin/true" or "chmod 777" in v for vs in kv.values() for v in vs):
            hints.append("suspicious Exec/command content")
        if kv.get("PrivateTmp") == ["false"]:
            hints.append("PrivateTmp=false")
        if "ProtectSystem" not in kv and sec == "Service":
            hints.append("Consider ProtectSystem= / ProtectHome= for hardening (advice only)")
    if hints:
        print("notes:")
        for h in dict.fromkeys(hints):
            print(f"  - {h}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
