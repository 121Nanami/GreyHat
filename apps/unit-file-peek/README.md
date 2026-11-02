# Unit File Peek

Summarize a systemd unit file (Description, User, Exec*, WantedBy) plus light hardening notes. Read-only.

## Run

```bash
python3 unit_file_peek.py /usr/lib/systemd/system/sshd.service
python3 unit_file_peek.py ./myapp.service
```
