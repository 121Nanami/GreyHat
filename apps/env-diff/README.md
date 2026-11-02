# Env Diff

Compare two `.env` files. Keys-only / length-masked by default so secrets stay out of scrollback.

## Run

```bash
python3 env_diff.py .env .env.example
python3 env_diff.py a.env b.env --show-values   # careful
```
