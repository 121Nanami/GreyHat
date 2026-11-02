# Mirrorlist Filter

Filter an Arch `mirrorlist` by country header, HTTPS-only, and optionally uncomment matching servers.

## Run

```bash
python3 mirrorlist_filter.py /etc/pacman.d/mirrorlist --country Germany --https-only --servers-only
python3 mirrorlist_filter.py mirrorlist --https-only --enable > mirrorlist.https
```
