#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -m unittest discover -s tests -v
python3 -m rageval
python3 -m rageval -j | head -n 30
echo "smoke ok"
