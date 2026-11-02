#!/usr/bin/env python3
"""urlguard — consumer-grade defensive URL safety checker.

Offline-first heuristics for end users. No phishing, no exploits, no
unauthorized access — only analysis of URLs the user already has.
"""

from __future__ import annotations

import argparse
import ipaddress
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from urllib.parse import unquote, urlparse

VERSION = "0.1.0"

SUSPICIOUS_TLDS = {
    "zip",
    "mov",
    "tk",
    "ml",
    "ga",
    "cf",
    "gq",
    "top",
    "xyz",
    "click",
    "country",
    "stream",
    "download",
    "loan",
    "work",
    "rest",
    "fit",
}

BRAND_TOKENS = {
    "paypal",
    "apple",
    "microsoft",
    "google",
    "amazon",
    "netflix",
    "facebook",
    "instagram",
    "whatsapp",
    "bankofamerica",
    "wellsfargo",
    "chase",
    "coinbase",
    "binance",
    "metamask",
    "icloud",
    "office365",
    "outlook",
    "github",
    "steam",
}

CREDENTIAL_PATH_HINTS = (
    "login",
    "signin",
    "sign-in",
    "logon",
    "verify",
    "verification",
    "secure",
    "account",
    "update",
    "confirm",
    "wallet",
    "seed",
    "mnemonic",
    "password",
    "passwd",
    "credential",
    "oauth",
    "ssn",
    "banking",
)

HOMOGLYPH_MAP = str.maketrans(
    {
        "0": "o",
        "1": "l",
        "3": "e",
        "4": "a",
        "5": "s",
        "7": "t",
        "@": "a",
        "$": "s",
    }
)


@dataclass
class Finding:
    severity: str  # info | low | medium | high
    code: str
    message: str


@dataclass
class Report:
    url: str
    host: str
    verdict: str
    score: int
    findings: list[Finding] = field(default_factory=list)

    def add(self, severity: str, code: str, message: str) -> None:
        self.findings.append(Finding(severity, code, message))


def _normalize_host(host: str) -> str:
    host = host.strip(".").lower()
    if host.startswith("xn--") or ".xn--" in host:
        try:
            host = host.encode("ascii").decode("idna")
        except (UnicodeError, UnicodeDecodeError, UnicodeEncodeError):
            pass
    return host


def _looks_like_ip(host: str) -> bool:
    try:
        ipaddress.ip_address(host.strip("[]"))
        return True
    except ValueError:
        return False


def _brand_lookalike(host: str) -> str | None:
    labels = host.split(".")
    # Compare registrable-ish labels (skip common public suffixes roughly).
    candidates = [label for label in labels if label and label not in {"com", "net", "org", "io", "co", "www"}]
    for label in candidates:
        folded = label.translate(HOMOGLYPH_MAP)
        for brand in BRAND_TOKENS:
            if brand == label or brand == folded:
                # Exact brand as subdomain of a non-brand parent is still suspicious
                # only when the brand is not the apex-ish label alone on a known TLD.
                continue
            if brand in folded and brand != folded:
                return f"hostname '{label}' resembles brand '{brand}'"
            # compact distance for short typos: paypal vs paypa1 already covered by fold
            if abs(len(folded) - len(brand)) <= 1 and _almost_equal(folded, brand):
                return f"hostname '{label}' is a near lookalike of '{brand}'"
    return None


def _almost_equal(a: str, b: str) -> bool:
    if a == b:
        return True
    if abs(len(a) - len(b)) > 1:
        return False
    # one edit distance
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) == 1
    if len(a) > len(b):
        a, b = b, a
    # a shorter by 1
    i = j = diffs = 0
    while i < len(a) and j < len(b):
        if a[i] != b[j]:
            diffs += 1
            j += 1
            if diffs > 1:
                return False
            continue
        i += 1
        j += 1
    return True


def analyze(url: str) -> Report:
    raw = url.strip()
    if not raw:
        report = Report(url=url, host="", verdict="invalid", score=100)
        report.add("high", "empty", "URL is empty")
        return report

    if "://" not in raw:
        raw = "https://" + raw

    parsed = urlparse(raw)
    host = _normalize_host(parsed.hostname or "")
    report = Report(url=url, host=host, verdict="safe", score=0)

    if not host:
        report.add("high", "no-host", "URL has no hostname")
        report.score = 100
        report.verdict = "dangerous"
        return report

    if parsed.username or parsed.password:
        report.add(
            "high",
            "userinfo",
            "URL embeds username/password (classic phishing pattern)",
        )
        report.score += 40

    if _looks_like_ip(host):
        report.add("high", "ip-host", "Hostname is a raw IP address")
        report.score += 35

    if host.startswith("xn--") or any(p.startswith("xn--") for p in host.split(".")):
        report.add(
            "medium",
            "punycode",
            "Internationalized (punycode) hostname — verify the real unicode domain",
        )
        report.score += 20

    if re.search(r"[^\x00-\x7f]", host):
        report.add("medium", "non-ascii", "Hostname contains non-ASCII characters")
        report.score += 15

    labels = host.split(".")
    if any(len(label) > 40 for label in labels):
        report.add("medium", "long-label", "Unusually long DNS label")
        report.score += 15

    if host.count(".") >= 4:
        report.add("low", "deep-subdomains", "Many subdomain levels")
        report.score += 8

    tld = labels[-1] if labels else ""
    if tld in SUSPICIOUS_TLDS:
        report.add("medium", "tld", f"TLD '.{tld}' is frequently abused")
        report.score += 15

    lookalike = _brand_lookalike(host)
    if lookalike:
        report.add("high", "brand-lookalike", lookalike)
        report.score += 35

    path_q = unquote((parsed.path or "") + "?" + (parsed.query or "")).lower()
    hits = sorted({hint for hint in CREDENTIAL_PATH_HINTS if hint in path_q})
    if hits:
        report.add(
            "medium",
            "credential-path",
            "Path/query suggests credential harvesting: " + ", ".join(hits[:6]),
        )
        report.score += 12 + min(12, 3 * len(hits))

    if parsed.port and parsed.port not in {80, 443, 8080, 8443}:
        report.add("low", "odd-port", f"Unusual port {parsed.port}")
        report.score += 8

    # Double-encoded or excessive percent encoding often used to obscure
    if raw.count("%") >= 8:
        report.add("low", "heavy-encoding", "Heavy percent-encoding in URL")
        report.score += 6

    if "@" in raw.split("://", 1)[-1].split("/", 1)[0]:
        # caught by userinfo usually; keep as belt-and-suspenders
        if not any(f.code == "userinfo" for f in report.findings):
            report.add("high", "at-sign", "Authority contains '@' (credential phishing trick)")
            report.score += 35

    report.score = min(100, report.score)
    if report.score >= 50:
        report.verdict = "dangerous"
    elif report.score >= 20:
        report.verdict = "suspicious"
    else:
        report.verdict = "safe"
        if not report.findings:
            report.add("info", "clean", "No suspicious patterns detected by local heuristics")

    return report


def _print_human(report: Report) -> None:
    badge = {
        "safe": "[SAFE]",
        "suspicious": "[SUSPICIOUS]",
        "dangerous": "[DANGEROUS]",
        "invalid": "[INVALID]",
    }.get(report.verdict, "[?]")
    print(f"{badge} score={report.score}  {report.url}")
    if report.host:
        print(f"  host: {report.host}")
    for finding in report.findings:
        print(f"  - ({finding.severity}) {finding.code}: {finding.message}")


def _iter_urls(args: argparse.Namespace) -> list[str]:
    urls: list[str] = []
    urls.extend(args.urls or [])
    if args.file:
        with open(args.file, encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line and not line.startswith("#"):
                    urls.append(line)
    if args.stdin or (not urls and not sys.stdin.isatty()):
        for line in sys.stdin:
            line = line.strip()
            if line and not line.startswith("#"):
                urls.append(line)
    return urls


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="urlguard",
        description=(
            "Consumer-grade defensive URL safety checker. "
            "Offline heuristics only — does not send your URLs anywhere."
        ),
    )
    parser.add_argument("urls", nargs="*", help="URL(s) to check")
    parser.add_argument("-f", "--file", help="Read URLs from a file (one per line)")
    parser.add_argument(
        "--stdin",
        action="store_true",
        help="Read URLs from stdin",
    )
    parser.add_argument(
        "-j",
        "--json",
        action="store_true",
        help="Emit JSON reports",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Only print verdict lines / JSON (no finding details in text mode)",
    )
    parser.add_argument("-V", "--version", action="version", version=f"urlguard {VERSION}")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    urls = _iter_urls(args)
    if not urls:
        parser.error("provide a URL, --file, or pipe URLs on stdin")

    reports = [analyze(url) for url in urls]
    worst = 0
    if args.json:
        payload = []
        for report in reports:
            payload.append(
                {
                    "url": report.url,
                    "host": report.host,
                    "verdict": report.verdict,
                    "score": report.score,
                    "findings": [asdict(f) for f in report.findings],
                }
            )
        json.dump(payload if len(payload) > 1 else payload[0], sys.stdout, indent=2)
        print()
    else:
        for report in reports:
            if args.quiet:
                print(f"{report.verdict.upper()}\t{report.score}\t{report.url}")
            else:
                _print_human(report)
                if len(reports) > 1:
                    print()
            if report.verdict == "dangerous":
                worst = max(worst, 2)
            elif report.verdict == "suspicious":
                worst = max(worst, 1)
            elif report.verdict == "invalid":
                worst = max(worst, 2)
    return worst


if __name__ == "__main__":
    sys.exit(main())
