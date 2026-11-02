# Benford Check

Compare leading digits of a numeric column (or one number per line) to Benford’s law.

## Run

```bash
seq 1 5000 | awk '{print $1*97}' | python3 benford_check.py
python3 benford_check.py data.csv -c amount --csv
```
