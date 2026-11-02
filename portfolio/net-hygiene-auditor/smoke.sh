#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -m unittest discover -s tests -v
python3 -m nethygiene --resolv testdata/resolv.conf --hosts testdata/hosts --skip-listen || true
python3 -m nethygiene --resolv testdata/resolv.conf --hosts testdata/hosts --skip-listen -j | head -n 20
echo "smoke ok"
