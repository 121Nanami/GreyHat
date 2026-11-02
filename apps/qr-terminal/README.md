# QR Terminal

Zero-dependency QR encoder for short strings — prints a scannable matrix in the terminal.

## Run

```bash
python3 qr.py "hello greyhat"
python3 qr.py https://example.com
```

Max payload ~50 bytes (QR versions 1–3, ECC L). A Node sketch `qr.js` remains as an experiment; prefer `qr.py`.
