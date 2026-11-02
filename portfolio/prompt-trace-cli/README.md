# prompt-trace-cli

Notebook-style **prompt / tool-call tracing CLI** for agent and LLM apps.
Record JSONL sessions, render ASCII or Markdown timelines, summarize tool usage,
and diff which tools two runs invoked.

## Problem

Agent bugs hide in invisible tool loops. Without a durable trace format and a
readable replay, “it called the wrong tool” is hard to show in interviews or
postmortems.

## Solution

`prompttrace` treats a session as JSONL events:

`session_start` → `system` / `user` / `assistant` → `tool_call` / `tool_result` → `session_end`

Commands:

| Command | Purpose |
|---------|---------|
| `show` | ASCII timeline or `--md` notebook dump |
| `stats` | Event counts, tool histogram, char volume |
| `diff` | Tool-set difference between two traces |
| `record` | Append one validated event (for wiring from apps) |

Works offline; no model API required to demo the tooling.

## How to run

```bash
cd docs/portfolio/prompt-trace-cli
python3 -m prompttrace show testdata/sample_trace.jsonl
python3 -m prompttrace stats testdata/sample_trace.jsonl
python3 -m prompttrace diff testdata/sample_trace.jsonl testdata/alt_trace.jsonl
python3 -m prompttrace record /tmp/demo.jsonl --type note --content 'checkpoint'
./smoke.sh
```

## Sample output

```
========================================================================
prompttrace timeline
========================================================================
[01] ▶ session_start  2026-11-02T01:00:00Z
------------------------------------------------------------------------
[05] → tool_call      2026-11-02T01:00:02Z
      tool=phishurl.analyze  args={'url': 'https://paypa1.tk/login'}
------------------------------------------------------------------------
[06] ← tool_result    2026-11-02T01:00:02Z
      tool=phishurl.analyze  result={"verdict": "dangerous", "score": 65, ...}
```

```
events=12 errors=0
by_type: assistant=3, session_end=1, session_start=1, system=1, tool_call=2, tool_result=2, user=2
tools: phishurl.analyze=1, secretscan.scan_tree=1
```

## License

MIT
