"""Trace event schema (JSONL-friendly)."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


ALLOWED_TYPES = frozenset(
    {
        "session_start",
        "system",
        "user",
        "assistant",
        "tool_call",
        "tool_result",
        "error",
        "session_end",
        "note",
    }
)


@dataclass
class Event:
    type: str
    ts: str
    content: str = ""
    name: str = ""
    args: dict[str, Any] = field(default_factory=dict)
    meta: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if self.type not in ALLOWED_TYPES:
            raise ValueError(f"unknown event type: {self.type}")

    def to_dict(self) -> dict[str, Any]:
        self.validate()
        d = asdict(self)
        # drop empty optional noise for compact JSONL
        if not d["name"]:
            del d["name"]
        if not d["args"]:
            del d["args"]
        if not d["meta"]:
            del d["meta"]
        if not d["content"] and d["type"] not in {"session_start", "session_end"}:
            pass
        return d


def event_from_dict(data: dict[str, Any]) -> Event:
    ev = Event(
        type=str(data.get("type", "")),
        ts=str(data.get("ts", "")),
        content=str(data.get("content", "")),
        name=str(data.get("name", "")),
        args=dict(data.get("args") or {}),
        meta=dict(data.get("meta") or {}),
    )
    ev.validate()
    return ev
