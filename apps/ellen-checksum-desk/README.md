# Ellen Checksum Desk

Consumer download-trust helper: compute/verify SHA-256, SHA-512, or MD5.

Part of the Ellen Joe–themed BlackArch spin idea (safer defaults for verifying ISOs/packages).

## Run

```bash
python3 checksum_desk.py ./some.iso
python3 checksum_desk.py ./some.iso -a sha256 -e abcdef...
python3 checksum_desk.py ./some.iso -c SHA256SUMS
```
