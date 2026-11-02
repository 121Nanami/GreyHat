#!/usr/bin/env python3
"""Generate project / host / package codenames from syllable beds."""
from __future__ import annotations
import argparse
import random
import sys

PRE = "ash bay cob dun elm fen gry hex ink jor kel lum mir nok orb pyx quin rav sol tor umb vex wry xen yew zen".split()
MID = "a e i o u ae io ua".split()
SUF = "ara bel cor dale en fork gale helm iris jolt keen lark moss nest oak pike quay rift spur tide urn vale wink york zest".split()


def one(rng: random.Random) -> str:
    return f"{rng.choice(PRE)}{rng.choice(MID)}{rng.choice(SUF)}"


def main() -> int:
    p = argparse.ArgumentParser(description="Codename generator")
    p.add_argument("-n", type=int, default=10)
    p.add_argument("--seed", type=int)
    p.add_argument("--kebab", action="store_true", help="prefix greyhat-")
    args = p.parse_args()
    rng = random.Random(args.seed)
    for _ in range(args.n):
        name = one(rng)
        print(f"greyhat-{name}" if args.kebab else name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
