# urlguard

Consumer-grade, **defensive** URL safety checker for end users.

`urlguard` analyzes a URL with offline heuristics and prints a clear verdict:
`safe`, `suspicious`, or `dangerous`. It never sends your URLs to a third party.

## What it checks

- Embedded credentials (`user:pass@host`) — classic phishing trick
- Raw IP hostnames
- Punycode / non-ASCII hostnames
- Abused TLDs
- Brand lookalikes (homoglyph / near-typo)
- Credential-harvesting path/query keywords
- Unusual ports and heavy percent-encoding

## Non-goals

- No phishing kits, credential capture, or attack automation
- No malware droppers or exploit code
- No scanning of third-party systems without the user supplying the URL

## Usage

```bash
urlguard 'https://example.com/login'
urlguard -f urls.txt
echo 'http://203.0.113.10/verify' | urlguard --stdin
urlguard -j 'https://paypa1.example/secure'
```

Exit codes: `0` safe, `1` suspicious, `2` dangerous/invalid (highest severity wins for batches).

## Install (from source)

```bash
install -Dm755 urlguard.py /usr/local/bin/urlguard
```

## BlackArch packaging

See the sibling `packages/urlguard/PKGBUILD` in this contribution bundle.

## License

MIT
