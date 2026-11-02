#!/usr/bin/env bash
# Countdown timer with terminal bell
set -euo pipefail
secs="${1:-}"
if [[ -z "$secs" ]]; then
  echo "Usage: $0 <seconds>" >&2
  exit 1
fi
if ! [[ "$secs" =~ ^[0-9]+$ ]]; then
  echo "Seconds must be an integer" >&2
  exit 1
fi
remaining=$secs
while (( remaining > 0 )); do
  printf "\r⏱  %02d:%02d " $((remaining / 60)) $((remaining % 60))
  sleep 1
  remaining=$((remaining - 1))
done
printf "\r🔔 Done!          \n"
printf '\a'
