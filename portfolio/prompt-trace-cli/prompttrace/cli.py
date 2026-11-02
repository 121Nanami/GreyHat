"""CLI for prompt-trace-cli."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from . import __version__
from .render import render_markdown, render_timeline
from .schema import Event
from .stats import diff_tool_sets, summarize
from .store import append_event, load_events


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="prompttrace",
        description=(
            "Notebook-style prompt / tool-call trace CLI. "
            "Record JSONL sessions, render timelines, summarize tool usage, diff traces."
        ),
    )
    p.add_argument("-V", "--version", action="version", version=f"prompttrace {__version__}")
    sub = p.add_subparsers(dest="cmd", required=True)

    show = sub.add_parser("show", help="Render a timeline from a JSONL trace")
    show.add_argument("trace", type=Path)
    show.add_argument("--md", action="store_true", help="Markdown instead of ASCII timeline")

    st = sub.add_parser("stats", help="Summarize event / tool counts")
    st.add_argument("trace", type=Path)
    st.add_argument("-j", "--json", action="store_true")

    diff = sub.add_parser("diff", help="Compare tool sets between two traces")
    diff.add_argument("trace_a", type=Path)
    diff.add_argument("trace_b", type=Path)
    diff.add_argument("-j", "--json", action="store_true")

    rec = sub.add_parser("record", help="Append a single event to a trace file")
    rec.add_argument("trace", type=Path)
    rec.add_argument("--type", required=True, dest="etype")
    rec.add_argument("--content", default="")
    rec.add_argument("--name", default="")
    rec.add_argument("--args-json", default="{}")

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.cmd == "show":
        events = load_events(args.trace)
        if args.md:
            print(render_markdown(events))
        else:
            print(render_timeline(events))
        return 0

    if args.cmd == "stats":
        events = load_events(args.trace)
        summary = summarize(events)
        if args.json:
            json.dump(summary, sys.stdout, indent=2)
            print()
        else:
            print(f"events={summary['events']} errors={summary['errors']}")
            print("by_type:", ", ".join(f"{k}={v}" for k, v in sorted(summary["by_type"].items())))
            if summary["tool_calls"]:
                print(
                    "tools:",
                    ", ".join(f"{k}={v}" for k, v in sorted(summary["tool_calls"].items())),
                )
            print(f"chars user={summary['user_chars']} assistant={summary['assistant_chars']}")
        return 0

    if args.cmd == "diff":
        a = load_events(args.trace_a)
        b = load_events(args.trace_b)
        d = diff_tool_sets(a, b)
        if args.json:
            json.dump(d, sys.stdout, indent=2)
            print()
        else:
            print("only_a:", ", ".join(d["only_a"]) or "-")
            print("only_b:", ", ".join(d["only_b"]) or "-")
            print("both:", ", ".join(d["both"]) or "-")
        return 0

    if args.cmd == "record":
        try:
            arg_obj = json.loads(args.args_json)
        except json.JSONDecodeError as exc:
            print(f"invalid --args-json: {exc}", file=sys.stderr)
            return 2
        ev = Event(type=args.etype, ts=_now(), content=args.content, name=args.name, args=arg_obj)
        try:
            ev.validate()
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        append_event(args.trace, ev)
        print(f"appended {ev.type} -> {args.trace}")
        return 0

    return 2


if __name__ == "__main__":
    sys.exit(main())
