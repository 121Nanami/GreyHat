# Hosts Merge

Merge hosts snippets; last hostname mapping wins. Dry-run unless `--apply`.

```bash
python3 hosts_merge.py a.hosts b.hosts
python3 hosts_merge.py a.hosts b.hosts -o merged.hosts --apply
```
