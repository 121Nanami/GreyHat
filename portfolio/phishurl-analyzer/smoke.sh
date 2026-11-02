#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -m unittest discover -s tests -v
python3 -m phishurl --summary -f testdata/sample_urls.txt
python3 -m phishurl -j 'https://paypa1.tk/login' | head -n 5
echo "smoke ok"
