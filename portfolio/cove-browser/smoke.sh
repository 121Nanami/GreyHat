#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
node tests/smoke.js
node --test tests/*.test.js
echo "smoke.sh: all checks passed"
