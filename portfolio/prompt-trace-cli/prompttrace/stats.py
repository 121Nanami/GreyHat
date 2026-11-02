"""Aggregate stats over a trace."""

from __future__ import annotations

from collections import Counter

from .schema import Event


def summarize(events: list[Event]) -> dict:
    by_type = Counter(ev.type for ev in events)
    tools = Counter(ev.name for ev in events if ev.type == "tool_call" and ev.name)
    errors = sum(1 for ev in events if ev.type == "error")
    user_chars = sum(len(ev.content) for ev in events if ev.type == "user")
    assistant_chars = sum(len(ev.content) for ev in events if ev.type == "assistant")
    return {
        "events": len(events),
        "by_type": dict(by_type),
        "tool_calls": dict(tools),
        "errors": errors,
        "user_chars": user_chars,
        "assistant_chars": assistant_chars,
    }


def diff_tool_sets(a: list[Event], b: list[Event]) -> dict:
    ta = {ev.name for ev in a if ev.type == "tool_call" and ev.name}
    tb = {ev.name for ev in b if ev.type == "tool_call" and ev.name}
    return {
        "only_a": sorted(ta - tb),
        "only_b": sorted(tb - ta),
        "both": sorted(ta & tb),
    }
