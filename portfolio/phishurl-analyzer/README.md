# phishurl-analyzer

Offline **phishing URL analyzer** for defensive / consumer-protection demos.
Expands urlguard-style heuristics into a small multi-module CLI with allow/block
lists, batch summaries, and structured JSON — without ever fetching remote hosts.

## Problem

End users and junior analysts paste suspicious links into search bars or click
shorteners. They need a **local, explainable** check that names *why* a URL looks
risky (userinfo, brand lookalike, nested redirect params) instead of a opaque
cloud score.

## Solution

`phishurl` scores a URL string with offline heuristics:

| Signal | Example |
|--------|---------|
| Embedded credentials | `https://user:pass@host/...` |
| Raw IP hostname | `http://203.0.113.10/verify` |
| Brand lookalike / brand-as-subdomain | `paypa1…`, `paypal.attacker.tld` |
| Nested URL / open-redirect params | `?redirect=https%3A%2F%2F…` |
| Shorteners, abused TLDs, free hosts | `bit.ly`, `.tk`, `*.ngrok-free.app` |
| Local allowlist / blocklist | operator-supplied host files |

**Non-goals:** no live crawling, no phishing kits, no malware, no scanning third-party systems the user did not supply.

## How to run

```bash
cd docs/portfolio/phishurl-analyzer
python3 -m phishurl 'https://paypa1-secure.tk/signin'
python3 -m phishurl --summary -f testdata/sample_urls.txt
python3 -m phishurl --allowlist testdata/allowlist.txt -j 'https://example.com/'
./smoke.sh
```

Exit codes: `0` safe, `1` suspicious, `2` dangerous/invalid (worst wins in a batch).

## Sample output

```
VERDICT      SCORE  URL
------------------------------------------------------------------------
SAFE             0  https://example.com/about
DANGEROUS       75  https://user:pass@evil.example/login
DANGEROUS       68  http://203.0.113.10/verify?account=1
DANGEROUS       77  https://paypa1-secure.tk/signin
SUSPICIOUS      18  https://bit.ly/3demo
DANGEROUS       70  https://paypal.attacker.example/secure/update
SUSPICIOUS      44  https://legit.example/path?redirect=https%3A%2F%2Fevil...
------------------------------------------------------------------------
counts: dangerous=4, safe=1, suspicious=2
```

## Layout

```
phishurl/          package (heuristics, analyze, cli, formatting)
testdata/          sample URLs + allowlist
tests/             unittest suite
smoke.sh           tests + demo run
LICENSE            MIT
```

## License

MIT
