#!/usr/bin/env python3
"""Guess MIME type from extension + magic bytes."""
from __future__ import annotations
import argparse
import mimetypes
import sys
from pathlib import Path

MAGIC = [
    (b"\x89PNG\r\n\x1a\n", "image/png"),
    (b"\xff\xd8\xff", "image/jpeg"),
    (b"GIF87a", "image/gif"),
    (b"GIF89a", "image/gif"),
    (b"%PDF", "application/pdf"),
    (b"PK\x03\x04", "application/zip"),
    (b"\x1f\x8b\x08", "application/gzip"),
    (b"#!/", "text/x-shellscript"),
    (b"{\n", "application/json"),
    (b"[", "application/json"),
]


def main() -> int:
    p = argparse.ArgumentParser(description="Guess MIME type")
    p.add_argument("paths", nargs="+", type=Path)
    args = p.parse_args()
    mimetypes.init()
    for path in args.paths:
        if not path.is_file():
            print(f"{path}: missing", file=sys.stderr)
            continue
        by_ext = mimetypes.guess_type(path.name)[0]
        head = path.read_bytes()[:64]
        by_magic = None
        for sig, mime in MAGIC:
            if head.startswith(sig):
                by_magic = mime
                break
        mime = by_magic or by_ext or "application/octet-stream"
        src = "magic" if by_magic else ("ext" if by_ext else "fallback")
        print(f"{mime}  ({src})  {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
