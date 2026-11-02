#!/usr/bin/env python3
"""Grow memorable passphrases from word beds."""
from __future__ import annotations
import argparse
import secrets
import sys

WORDS = """
amber anchor apricot aurora bamboo barley basil beaver birch blossom
boulder breeze canyon cedar celery cedar chestnut clover comet coral
crocus crystal daisy delta ember falcon fern fjord flint forest
galaxy glacier harbor hazel heron indigo iris jasper juniper kelp
lagoon lantern lava lotus maple meadow mercury moss nebula nectar
orchid otter pebble pine pollen prairie quartz raven river saffron
sage sapphire scarlet sierra spruce storm summit thistle thunder tide
timber topaz valley velvet violet willow zephyr
""".split()


def grow(n: int, sep: str, digits: bool, title: bool) -> str:
    picks = [secrets.choice(WORDS) for _ in range(n)]
    if title:
        picks = [w.capitalize() for w in picks]
    phrase = sep.join(picks)
    if digits:
        phrase += sep + str(secrets.randbelow(90) + 10)
    return phrase


def main() -> int:
    p = argparse.ArgumentParser(description="Memorable passphrase generator")
    p.add_argument("-n", "--words", type=int, default=4)
    p.add_argument("-c", "--count", type=int, default=5)
    p.add_argument("--sep", default="-")
    p.add_argument("--digits", action="store_true")
    p.add_argument("--title", action="store_true")
    args = p.parse_args()
    for _ in range(args.count):
        print(grow(args.words, args.sep, args.digits, args.title))
    return 0


if __name__ == "__main__":
    sys.exit(main())
