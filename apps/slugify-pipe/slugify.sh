#!/usr/bin/env bash
# stdin or args → URL-safe slugs
set -euo pipefail
slug() {
  printf '%s' "$1" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+//; s/-+$//; s/-+/-/g'
}
if [[ $# -gt 0 ]]; then
  for a in "$@"; do slug "$a"; printf '\n'; done
else
  while IFS= read -r line || [[ -n "$line" ]]; do
    slug "$line"; printf '\n'
  done
fi
