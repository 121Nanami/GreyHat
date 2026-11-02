# Watch Run

Poll files/dirs and re-run a command when anything changes. No extra deps.

## Run

```bash
python3 watch_run.py -p ./src -p ./tests -- python3 -m pytest -q
python3 watch_run.py -p PKGBUILD -- python3 ../pkgbuild-linter/pkgbuild_linter.py PKGBUILD
```
