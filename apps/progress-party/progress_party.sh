#!/usr/bin/env bash
# Animated progress for piped line counts or a known total
set -euo pipefail
TOTAL="${1:-0}"  # 0 = unknown (spinner + count)
count=0
cols=40
spin='|/-\'
si=0
while IFS= read -r line || [[ -n "$line" ]]; do
  count=$((count + 1))
  printf '%s\n' "$line"
  if [[ "$TOTAL" -gt 0 ]]; then
    pct=$((count * 100 / TOTAL))
    filled=$((count * cols / TOTAL)); [[ $filled -gt $cols ]] && filled=$cols
    bar=$(printf "%${filled}s" | tr ' ' '#')
    pad=$(printf "%$((cols - filled))s" | tr ' ' '.')
    printf '\r[%s%s] %3d%% (%d/%d)' "$bar" "$pad" "$pct" "$count" "$TOTAL" >&2
  else
    printf '\r%c %d lines' "${spin:si++%4:1}" "$count" >&2
  fi
done
printf '\n' >&2
