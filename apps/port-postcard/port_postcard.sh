#!/usr/bin/env bash
# Pretty list of listening TCP ports (ss or netstat)
set -euo pipefail
if command -v ss >/dev/null 2>&1; then
  echo "Listening TCP (ss -ltnp)"
  echo "------------------------"
  ss -ltnp 2>/dev/null | awk 'NR==1 || /LISTEN/'
elif command -v netstat >/dev/null 2>&1; then
  echo "Listening TCP (netstat -ltnp)"
  echo "-----------------------------"
  netstat -ltnp 2>/dev/null | awk 'NR==1 || /LISTEN/'
else
  echo "error: need ss or netstat" >&2
  exit 2
fi
