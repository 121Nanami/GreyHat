#!/usr/bin/env python3
from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from prompttrace.render import render_timeline  # noqa: E402
from prompttrace.stats import diff_tool_sets, summarize  # noqa: E402
from prompttrace.store import append_event, load_events  # noqa: E402
from prompttrace.schema import Event  # noqa: E402


class PromptTraceTests(unittest.TestCase):
    def test_load_sample(self) -> None:
        events = load_events(ROOT / "testdata" / "sample_trace.jsonl")
        self.assertGreaterEqual(len(events), 10)
        summary = summarize(events)
        self.assertIn("tool_call", summary["by_type"])
        self.assertIn("phishurl.analyze", summary["tool_calls"])
        text = render_timeline(events)
        self.assertIn("prompttrace timeline", text)

    def test_diff(self) -> None:
        a = load_events(ROOT / "testdata" / "sample_trace.jsonl")
        b = load_events(ROOT / "testdata" / "alt_trace.jsonl")
        d = diff_tool_sets(a, b)
        self.assertIn("secretscan.scan_tree", d["only_a"])
        self.assertIn("nethygiene.run_audit", d["only_b"])
        self.assertIn("phishurl.analyze", d["both"])

    def test_record_roundtrip(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "t.jsonl"
            append_event(path, Event(type="note", ts="2026-01-01T00:00:00Z", content="hi"))
            evs = load_events(path)
            self.assertEqual(evs[0].content, "hi")


if __name__ == "__main__":
    unittest.main()
