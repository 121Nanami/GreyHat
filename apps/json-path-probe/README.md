# JSON Path Probe

Query JSON with dotted paths and `[index]` segments. Stdlib only.

## Run

```bash
echo '{"users":[{"email":"a@b.c"}]}' | python3 json_path_probe.py '.users[0].email' -r
python3 json_path_probe.py '.packages[2].name' -f manifest.json
```
