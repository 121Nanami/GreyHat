# Replace In Files

Bulk find/replace across files with dry-run and optional regex.

## Run

```bash
python3 replace_in_files.py 'GreyHat' 'GreyHatInc' README.md -n
python3 replace_in_files.py -E 'foo[0-9]+' bar ./src/*.py
```
