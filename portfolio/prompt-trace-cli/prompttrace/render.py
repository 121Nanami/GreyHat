"""Notebook-style timeline rendering for traces."""

from __future__ import annotations

from .schema import Event

ICONS = {
    "session_start": "▶",
    "session_end": "■",
    "system": "⚙",
    "user": "U",
    "assistant": "A",
    "tool_call": "→",
    "tool_result": "←",
    "error": "!",
    "note": "·",
}


def _truncate(s: str, n: int = 160) -> str:
    s = s.replace("\n", " ").strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def render_timeline(events: list[Event], *, width: int = 88) -> str:
    lines: list[str] = []
    lines.append("=" * width)
    lines.append("prompttrace timeline")
    lines.append("=" * width)
    for i, ev in enumerate(events, start=1):
        icon = ICONS.get(ev.type, "?")
        header = f"[{i:02d}] {icon} {ev.type:<14} {ev.ts}"
        lines.append(header)
        if ev.type == "tool_call":
            lines.append(f"      tool={ev.name or '?'}  args={_truncate(str(ev.args), 120)}")
        elif ev.type == "tool_result":
            lines.append(f"      tool={ev.name or '?'}  result={_truncate(ev.content, 120)}")
        elif ev.content:
            prefix = "      "
            lines.append(prefix + _truncate(ev.content, width - len(prefix)))
        if ev.meta:
            lines.append(f"      meta={_truncate(str(ev.meta), 120)}")
        lines.append("-" * width)
    return "\n".join(lines)


def render_markdown(events: list[Event]) -> str:
    parts = ["# Prompt trace\n"]
    for i, ev in enumerate(events, start=1):
        title = ev.name or ev.type
        parts.append(f"## {i}. `{ev.type}` — {title}\n")
        parts.append(f"- **ts:** `{ev.ts}`\n")
        if ev.args:
            parts.append(f"- **args:** `{ev.args}`\n")
        if ev.content:
            parts.append("\n```\n" + ev.content.strip() + "\n```\n")
        parts.append("")
    return "\n".join(parts)
