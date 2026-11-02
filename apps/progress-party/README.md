# Progress Party

Pipe filter that shows a progress bar (known total) or spinner (unknown) on stderr while forwarding stdin → stdout.

## Run

```bash
seq 100 | ./progress_party.sh 100 >/dev/null
find . -type f | ./progress_party.sh >/tmp/files.txt
```
