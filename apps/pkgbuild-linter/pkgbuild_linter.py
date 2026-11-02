#!/usr/bin/env python3
"""Lightweight PKGBUILD hygiene linter (heuristic, not namcap)."""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

REQUIRED = ["pkgname", "pkgver", "pkgrel", "arch", "license"]


def lint(text: str, path: str) -> list[str]:
    issues: list[str] = []
    for key in REQUIRED:
        if not re.search(rf"^{key}=", text, re.M):
            issues.append(f"missing {key}=")
    if re.search(r"makedepends=\([^)]*\bbase-devel\b", text):
        issues.append("makedepends includes base-devel (usually unnecessary)")
    if "source=(" in text and "sha256sums=" not in text and "b2sums=" not in text and "sha512sums=" not in text:
        issues.append("source= present but no sha256sums=/b2sums=/sha512sums=")
    if re.search(r"\bcurl\b.*\|\s*(ba)?sh", text):
        issues.append("pipe-to-shell pattern detected — prefer verified tarballs")
    if re.search(r"depends=\([^)]*\bpython\b", text) and "python-" not in text:
        # soft hint only
        pass
    if not re.search(r"package\s*\(\)", text):
        issues.append("no package() function found")
    if re.search(r"^\s*sudo\b", text, re.M):
        issues.append("sudo inside PKGBUILD is almost always wrong")
    if "SKIP" in text and re.search(r"sha256sums=\([^)]*SKIP", text):
        issues.append("sha256sums contains SKIP — fine for VCS, risky for release tarballs")
    if not issues:
        issues.append(f"OK — no heuristic issues in {path}")
    return issues


def main() -> int:
    p = argparse.ArgumentParser(description="Heuristic PKGBUILD linter")
    p.add_argument("pkgbuild", type=Path, nargs="?", default=Path("PKGBUILD"))
    args = p.parse_args()
    if not args.pkgbuild.is_file():
        print(f"error: {args.pkgbuild} not found", file=sys.stderr)
        return 2
    text = args.pkgbuild.read_text(encoding="utf-8", errors="replace")
    issues = lint(text, str(args.pkgbuild))
    fatal = [i for i in issues if not i.startswith("OK")]
    for i in issues:
        print(("!" if not i.startswith("OK") else "·"), i)
    return 1 if fatal else 0


if __name__ == "__main__":
    sys.exit(main())
