# GreyHatInc portfolio showcases

Semi-usable, interview-credible projects for **ethical hacking / defensive security** and **AI engineering** roles. Each project is multi-file, MIT-licensed, has tests + `smoke.sh`, and ships a README with problem / solution / how-to-run / sample output.

All work is **defensive or evaluative only** — no malware, exploits, phishing kits, or unauthorized access tooling.

## Projects

| # | Project | Track | One-liner |
|---|---------|-------|-----------|
| 1 | [phishurl-analyzer](./phishurl-analyzer/) | Defensive | Offline phishing URL heuristics (urlguard-expanded): lookalikes, nested redirects, allow/block lists |
| 2 | [net-hygiene-auditor](./net-hygiene-auditor/) | Defensive | Read-only local hygiene: DNS/hosts, `/proc` listeners, SSH perms, PATH writability |
| 3 | [repo-secrets-scan](./repo-secrets-scan/) | Defensive | Secrets-in-repo scanner with redaction, entropy pass, fixture suite |
| 4 | [rag-eval-harness](./rag-eval-harness/) | AI eng | Stdlib TF-IDF RAG eval: Hit@K / MRR / nDCG on a labeled mini corpus |
| 5 | [prompt-trace-cli](./prompt-trace-cli/) | AI eng | JSONL prompt/tool-call traces with timeline, stats, and tool-set diff |

## Quick smoke (all)

From this directory:

```bash
for d in phishurl-analyzer net-hygiene-auditor repo-secrets-scan rag-eval-harness prompt-trace-cli; do
  echo "=== $d ==="
  (cd "$d" && bash smoke.sh)
done
```

From the repo root:

```bash
for d in phishurl-analyzer net-hygiene-auditor repo-secrets-scan rag-eval-harness prompt-trace-cli; do
  echo "=== $d ==="
  (cd "portfolio/$d" && bash smoke.sh)
done
```

## Suggested LinkedIn / GitHub blurb

**Short (LinkedIn About / Featured):**

> Building defensive security + AI eng tools: offline phishing URL analysis, local network hygiene audits, secrets-in-repo scanning, RAG retrieval eval (Hit@K/MRR/nDCG), and prompt/tool-call tracing. Consumer-protection focus — explainable heuristics, no offensive tooling.

**GitHub profile README snippet:**

```markdown
### Portfolio (GreyHatInc)

Defensive + AI engineering showcases — each with tests and a smoke script:

- **phishurl-analyzer** — offline phishing URL scoring (lookalikes, nested redirects)
- **net-hygiene-auditor** — read-only DNS/hosts/listener/SSH hygiene checks
- **repo-secrets-scan** — pattern + entropy secrets detection with redaction
- **rag-eval-harness** — TF-IDF RAG eval harness (Hit@K, MRR, nDCG)
- **prompt-trace-cli** — JSONL agent traces: timeline, stats, tool-set diff

Philosophy: semi-usable CLIs you can demo in an interview, not toy one-liners.
```

**Pinned-repo description ideas (≤350 chars):**

- phishurl: `Offline phishing URL analyzer — brand lookalikes, nested redirects, allow/block lists. Defensive heuristics only.`
- nethygiene: `Read-only local network hygiene auditor (/proc listeners, resolv/hosts, SSH perms). No remote scanning.`
- secretscan: `Secrets-in-repo scanner with curated patterns, entropy pass, and redacted output for CI/demo use.`
- rageval: `Stdlib RAG retrieval eval harness — labeled corpus, TF-IDF baseline, Hit@K / MRR / nDCG.`
- prompttrace: `Notebook-style prompt & tool-call trace CLI — JSONL sessions, timelines, stats, diffs.`

## How these map to job talks

| Interview prompt | Demo |
|------------------|------|
| “Show me a phishing defense idea” | `phishurl --summary -f testdata/sample_urls.txt` |
| “How would you harden a laptop baseline?” | `nethygiene` on fixtures + live `/proc` |
| “Catch secrets before they ship” | `secretscan testdata/fixture_repo` |
| “How do you know RAG got better?” | `rageval` metrics table |
| “Debug an agent that called the wrong tool” | `prompttrace show` + `diff` |
