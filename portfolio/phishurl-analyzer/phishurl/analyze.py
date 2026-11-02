"""Core offline URL analysis (expands urlguard-style heuristics)."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from urllib.parse import parse_qs, unquote, urlparse

from .heuristics import (
    BRAND_TOKENS,
    CREDENTIAL_PATH_HINTS,
    SHORTENER_HOSTS,
    SUSPICIOUS_TLDS,
    URL_IN_URL_RE,
    brand_lookalike,
    free_host_match,
    looks_like_ip,
    normalize_host,
)

SEVERITY_WEIGHT = {"info": 0, "low": 6, "medium": 15, "high": 35}


@dataclass
class Finding:
    severity: str
    code: str
    message: str
    weight: int = 0


@dataclass
class Report:
    url: str
    host: str
    verdict: str
    score: int
    scheme: str = ""
    findings: list[Finding] = field(default_factory=list)
    allowlisted: bool = False
    blocklisted: bool = False

    def add(self, severity: str, code: str, message: str, weight: int | None = None) -> None:
        w = SEVERITY_WEIGHT.get(severity, 10) if weight is None else weight
        self.findings.append(Finding(severity, code, message, w))
        self.score = min(100, self.score + w)

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "host": self.host,
            "scheme": self.scheme,
            "verdict": self.verdict,
            "score": self.score,
            "allowlisted": self.allowlisted,
            "blocklisted": self.blocklisted,
            "findings": [asdict(f) for f in self.findings],
        }


def _finalize(report: Report) -> Report:
    if report.blocklisted:
        report.verdict = "dangerous"
        report.score = max(report.score, 90)
        return report
    if report.allowlisted and report.score < 50:
        report.verdict = "safe"
        if not any(f.code == "allowlist" for f in report.findings):
            report.findings.insert(
                0,
                Finding("info", "allowlist", "Host matched local allowlist", 0),
            )
        return report
    if report.score >= 50:
        report.verdict = "dangerous"
    elif report.score >= 20:
        report.verdict = "suspicious"
    else:
        report.verdict = "safe"
        if not report.findings:
            report.add("info", "clean", "No suspicious patterns detected by local heuristics", 0)
    return report


def analyze(
    url: str,
    *,
    allowlist: set[str] | None = None,
    blocklist: set[str] | None = None,
) -> Report:
    """Analyze a single URL with offline heuristics.

    Defensive only: never fetches the remote host, never follows live redirects.
    Optional local allow/block lists are host suffixes the operator supplies.
    """
    raw = url.strip()
    allowlist = allowlist or set()
    blocklist = blocklist or set()

    if not raw:
        report = Report(url=url, host="", verdict="invalid", score=100)
        report.add("high", "empty", "URL is empty")
        return report

    display = raw
    if "://" not in raw:
        raw = "https://" + raw

    parsed = urlparse(raw)
    host = normalize_host(parsed.hostname or "")
    report = Report(url=display, host=host, verdict="safe", score=0, scheme=parsed.scheme or "")

    if not host:
        report.add("high", "no-host", "URL has no hostname")
        report.verdict = "dangerous"
        return report

    for entry in blocklist:
        if host == entry or host.endswith("." + entry):
            report.blocklisted = True
            report.add("high", "blocklist", f"Host matched local blocklist entry '{entry}'", 50)
            break

    for entry in allowlist:
        if host == entry or host.endswith("." + entry):
            report.allowlisted = True
            break

    if parsed.username or parsed.password:
        report.add(
            "high",
            "userinfo",
            "URL embeds username/password (classic phishing pattern)",
        )

    if looks_like_ip(host):
        report.add("high", "ip-host", "Hostname is a raw IP address")

    if host.startswith("xn--") or any(p.startswith("xn--") for p in host.split(".")):
        report.add(
            "medium",
            "punycode",
            "Internationalized (punycode) hostname — verify the real unicode domain",
        )

    if re.search(r"[^\x00-\x7f]", host):
        report.add("medium", "non-ascii", "Hostname contains non-ASCII characters")

    labels = host.split(".")
    if any(len(label) > 40 for label in labels):
        report.add("medium", "long-label", "Unusually long DNS label")

    if host.count(".") >= 4:
        report.add("low", "deep-subdomains", "Many subdomain levels")

    tld = labels[-1] if labels else ""
    if tld in SUSPICIOUS_TLDS:
        report.add("medium", "tld", f"TLD '.{tld}' is frequently abused")

    lookalike = brand_lookalike(host)
    if lookalike:
        report.add("high", "brand-lookalike", lookalike)

    # Brand token as subdomain of unrelated apex (paypal.evil.tld)
    apexish = ".".join(labels[-2:]) if len(labels) >= 2 else host
    for label in labels[:-2]:
        folded = label
        if folded in BRAND_TOKENS and not any(
            apexish.startswith(b) or b in apexish for b in BRAND_TOKENS
        ):
            report.add(
                "high",
                "brand-subdomain",
                f"Brand token '{folded}' used as subdomain of '{apexish}'",
            )
            break

    if host in SHORTENER_HOSTS or any(host.endswith("." + s) for s in SHORTENER_HOSTS):
        report.add(
            "medium",
            "shortener",
            "URL shortener host — expand carefully before trusting the destination",
            18,
        )

    free = free_host_match(host)
    if free:
        report.add(
            "low",
            "free-host",
            f"Hosted on disposable/free platform suffix '{free}' — verify legitimacy",
            8,
        )

    path_q = unquote((parsed.path or "") + "?" + (parsed.query or "")).lower()
    hits = sorted({hint for hint in CREDENTIAL_PATH_HINTS if hint in path_q})
    if hits:
        report.add(
            "medium",
            "credential-path",
            "Path/query suggests credential harvesting: " + ", ".join(hits[:6]),
            12 + min(12, 3 * len(hits)),
        )

    if URL_IN_URL_RE.search(path_q) or URL_IN_URL_RE.search(unquote(parsed.query or "")):
        report.add(
            "high",
            "url-in-url",
            "Nested/encoded URL inside path or query (common redirect lure)",
            30,
        )

    qs = parse_qs(parsed.query or "", keep_blank_values=True)
    redirect_keys = {"url", "redirect", "redir", "next", "return", "continue", "dest", "destination", "goto"}
    for key in qs:
        if key.lower() in redirect_keys:
            report.add(
                "medium",
                "open-redirect-param",
                f"Query parameter '{key}' often used in open-redirect / phishing chains",
                14,
            )
            break

    if parsed.port and parsed.port not in {80, 443, 8080, 8443}:
        report.add("low", "odd-port", f"Unusual port {parsed.port}")

    if display.count("%") >= 8:
        report.add("low", "heavy-encoding", "Heavy percent-encoding in URL")

    authority = display.split("://", 1)[-1].split("/", 1)[0]
    if "@" in authority and not any(f.code == "userinfo" for f in report.findings):
        report.add("high", "at-sign", "Authority contains '@' (credential phishing trick)")

    if parsed.scheme == "http":
        report.add("low", "plain-http", "Uses plaintext HTTP (credentials would not be encrypted)")

    return _finalize(report)
