#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -m unittest discover -s tests -v
python3 -m secretscan testdata/fixture_repo || true
python3 -m secretscan -j testdata/fixture_repo | head -n 25
echo "smoke ok"
