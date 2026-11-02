# Line Freq

Frequency count for lines or a selected field (`sort | uniq -c` alternative with top-N).

## Run

```bash
./port_postcard.sh | python3 line_freq.py   # example pipe from another tool
printf 'a\nb\na\n' | python3 line_freq.py
python3 line_freq.py access.log -f 1 -n 20
```
