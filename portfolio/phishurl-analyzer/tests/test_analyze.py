#!/usr/bin/env python3
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from phishurl.analyze import analyze  # noqa: E402


class AnalyzeTests(unittest.TestCase):
    def test_clean(self) -> None:
        r = analyze("https://example.com/about")
        self.assertEqual(r.verdict, "safe")
        self.assertLess(r.score, 20)

    def test_userinfo(self) -> None:
        r = analyze("https://user:pass@evil.example/login")
        self.assertEqual(r.verdict, "dangerous")
        self.assertTrue(any(f.code == "userinfo" for f in r.findings))

    def test_ip_host(self) -> None:
        r = analyze("http://203.0.113.10/verify")
        self.assertIn(r.verdict, {"suspicious", "dangerous"})
        self.assertTrue(any(f.code == "ip-host" for f in r.findings))

    def test_brand_lookalike(self) -> None:
        r = analyze("https://paypa1-secure.example/login")
        self.assertTrue(
            any(f.code in {"brand-lookalike", "credential-path"} for f in r.findings)
        )

    def test_url_in_url(self) -> None:
        r = analyze("https://legit.example/go?next=https%3A%2F%2Fevil.example%2Fx")
        self.assertTrue(
            any(f.code in {"url-in-url", "open-redirect-param"} for f in r.findings)
        )

    def test_shortener(self) -> None:
        r = analyze("https://bit.ly/abc")
        self.assertTrue(any(f.code == "shortener" for f in r.findings))

    def test_blocklist(self) -> None:
        r = analyze("https://bad.example/x", blocklist={"bad.example"})
        self.assertTrue(r.blocklisted)
        self.assertEqual(r.verdict, "dangerous")

    def test_allowlist_keeps_clean_safe(self) -> None:
        r = analyze("https://example.com/", allowlist={"example.com"})
        self.assertTrue(r.allowlisted)
        self.assertEqual(r.verdict, "safe")


if __name__ == "__main__":
    unittest.main()
