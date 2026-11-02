#!/usr/bin/env python3
"""Demo update notifier — fake pacman -Qu style digest for UI prototyping."""
from __future__ import annotations
import argparse
import random
import sys
from datetime import datetime, timezone

DEMO = [
    ("linux", "6.11.5.arch1-1", "6.11.6.arch1-1", "core"),
    ("firefox", "132.0-1", "132.0.1-1", "extra"),
    ("mesa", "1:24.2.5-1", "1:24.2.6-1", "extra"),
    ("openssl", "3.3.2-1", "3.3.3-1", "core"),
    ("greyhat-wallpapers", "0.1.0-1", "0.1.1-1", "spin"),
    ("urlguard", "0.2.0-1", "0.2.1-1", "spin"),
]


def main() -> int:
    p = argparse.ArgumentParser(description="Fake update notifier digest")
    p.add_argument("-n", type=int, default=4, help="How many demo updates to show")
    p.add_argument("--seed", type=int, default=None)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    rng = random.Random(args.seed)
    picks = rng.sample(DEMO, k=min(args.n, len(DEMO)))
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    if args.json:
        import json
        print(json.dumps({"checked_at": now, "updates": [
            {"name": n, "from": a, "to": b, "repo": r} for n, a, b, r in picks
        ]}, indent=2))
        return 0
    print(f"GreyHat Spin · update notifier demo · {now}")
    print(f"{len(picks)} package(s) pretend-upgradable:\n")
    for n, a, b, r in picks:
        print(f"  {n:22s} {a:18s} → {b:18s}  [{r}]")
    print("\n(demo only — did not query pacman)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
