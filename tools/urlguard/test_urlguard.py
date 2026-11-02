#!/usr/bin/env python3
"""Minimal self-tests for urlguard (stdlib unittest)."""

from __future__ import annotations

import unittest

from urlguard import analyze


class UrlguardTests(unittest.TestCase):
    def test_clean_https(self) -> None:
        report = analyze("https://example.com/about")
        self.assertEqual(report.verdict, "safe")
        self.assertLess(report.score, 20)

    def test_userinfo_phishing_pattern(self) -> None:
        report = analyze("https://user:pass@evil.example/login")
        self.assertEqual(report.verdict, "dangerous")
        self.assertTrue(any(f.code == "userinfo" for f in report.findings))

    def test_ip_host(self) -> None:
        report = analyze("http://203.0.113.10/verify")
        self.assertIn(report.verdict, {"suspicious", "dangerous"})
        self.assertTrue(any(f.code == "ip-host" for f in report.findings))

    def test_brand_lookalike(self) -> None:
        report = analyze("https://paypa1-secure.example/login")
        self.assertTrue(
            any(f.code in {"brand-lookalike", "credential-path"} for f in report.findings)
        )

    def test_scheme_optional(self) -> None:
        report = analyze("example.com")
        self.assertEqual(report.host, "example.com")
        self.assertEqual(report.verdict, "safe")


if __name__ == "__main__":
    unittest.main()
