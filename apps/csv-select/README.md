# CSV Select

Select/reorder CSV columns by name or index; optional `col=value` filter.

## Run

```bash
python3 csv_select.py data.csv -c name,email
python3 csv_select.py data.csv -c 0,2 --where status=active
```
