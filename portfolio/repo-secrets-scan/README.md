# repo-secrets-scan

Defensive **secrets-in-repo scanner** for local trees. Flags AWS-style keys,
GitHub PATs, Stripe live keys, PEM headers, JWTs, and high-entropy tokens near
secret keywords — with redacted excerpts.

## Problem

Credentials leak into git history and sample configs. Before a demo or PR, you
want a fast local check that names *what* matched and *where*, without shipping
file contents to a SaaS.

## Solution

`secretscan` walks a directory (skipping `.git`, `node_modules`, binaries) and
applies:

1. Curated regex rules for well-known token shapes
2. Shannon-entropy pass for long tokens beside `password` / `api_key` / etc.
3. Placeholder filters (`EXAMPLE`, `changeme`, …)
4. Redacted CLI + JSON output

**Non-goals:** no credential stuffing, no cracking, no uploading findings, no
using discovered secrets.

## How to run

```bash
cd docs/portfolio/repo-secrets-scan
python3 -m secretscan testdata/fixture_repo
python3 -m secretscan -j .
./smoke.sh
```

Exit `1` if any hit is found (handy in CI smoke jobs).

## Sample output

```
secretscan — root=.../fixture_repo files=3 hits=4
HIGH    aws-access-key         leaky.env:2  AKIA…MPLE
HIGH    github-pat             leaky.env:3  ghp_…6789
HIGH    stripe-key             leaky.env:4  sk_l…uvwx
MEDIUM  jwt                    notes.md:3   eyJh…w5c
```

## License

MIT
