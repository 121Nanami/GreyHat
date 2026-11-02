#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 -m unittest discover -s tests -v
python3 -m prompttrace show testdata/sample_trace.jsonl | head -n 25
python3 -m prompttrace stats testdata/sample_trace.jsonl
python3 -m prompttrace diff testdata/sample_trace.jsonl testdata/alt_trace.jsonl
echo "smoke ok"
