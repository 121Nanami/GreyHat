# ISO Checksum Verifier

Verify download integrity for ISOs and disk images (SHA-256 / SHA-512 / MD5 / SHA-1). Read-only — never mutates the image.

## Run

```bash
python3 iso_checksum_verifier.py spin.iso -e <hexdigest>
python3 iso_checksum_verifier.py spin.iso -c SHA256SUMS
python3 iso_checksum_verifier.py spin.iso -a sha512 --print-only -e 0
```

`--print-only` still requires `-e`/`-c`; use `-e 0` as a placeholder when you only want the computed digest.
