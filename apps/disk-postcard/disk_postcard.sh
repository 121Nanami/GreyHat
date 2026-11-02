#!/usr/bin/env bash
# df with ASCII usage bars
set -euo pipefail
df -hP -x tmpfs -x devtmpfs -x squashfs 2>/dev/null | awk 'NR==1{next}
{
  use=$5; gsub(/%/,"",use);
  n=int(use/5); if(n>20)n=20;
  bar=""; for(i=0;i<n;i++) bar=bar"#"; for(;i<20;i++) bar=bar".";
  printf "%-20s %6s %6s %6s [%s] %3s%% %s\n", $1,$2,$3,$4,bar,use,$6
}'
