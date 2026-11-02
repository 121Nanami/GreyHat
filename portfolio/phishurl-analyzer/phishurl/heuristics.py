"""Heuristic tables and helpers for offline URL analysis."""

from __future__ import annotations

import ipaddress
import re

SUSPICIOUS_TLDS = frozenset(
    {
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
        "buzz",
        "icu",
        "cam",
        "monster",
    }
)

BRAND_TOKENS = frozenset(
    {
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
        "linkedin",
        "dropbox",
        "docusign",
        "adobe",
    }
)

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
    "reset",
    "unlock",
    "session",
)

SHORTENER_HOSTS = frozenset(
    {
        "bit.ly",
        "tinyurl.com",
        "t.co",
        "goo.gl",
        "ow.ly",
        "is.gd",
        "buff.ly",
        "rebrand.ly",
        "cutt.ly",
        "shorturl.at",
    }
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

# Common free-hosting / disposable patterns often abused in phishing kits demos
FREE_HOST_SUFFIXES = (
    ".ngrok.io",
    ".ngrok-free.app",
    ".trycloudflare.com",
    ".loca.lt",
    ".github.io",  # informational only — legitimate but often cloned
    ".web.app",
    ".firebaseapp.com",
    ".pages.dev",
    ".netlify.app",
    ".vercel.app",
    ".herokuapp.com",
    ".glitch.me",
)

URL_IN_URL_RE = re.compile(
    r"(?:https?|hxxp)(?:%3a|:)(?:%2f|/)",
    re.IGNORECASE,
)


def normalize_host(host: str) -> str:
    host = host.strip(".").lower()
    if host.startswith("xn--") or ".xn--" in host:
        try:
            host = host.encode("ascii").decode("idna")
        except (UnicodeError, UnicodeDecodeError, UnicodeEncodeError):
            pass
    return host


def looks_like_ip(host: str) -> bool:
    try:
        ipaddress.ip_address(host.strip("[]"))
        return True
    except ValueError:
        return False


def almost_equal(a: str, b: str) -> bool:
    if a == b:
        return True
    if abs(len(a) - len(b)) > 1:
        return False
    if len(a) == len(b):
        return sum(x != y for x, y in zip(a, b)) == 1
    if len(a) > len(b):
        a, b = b, a
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


def brand_lookalike(host: str) -> str | None:
    labels = host.split(".")
    skip = {"com", "net", "org", "io", "co", "www", "uk", "us", "au"}
    candidates = [label for label in labels if label and label not in skip]
    for label in candidates:
        folded = label.translate(HOMOGLYPH_MAP)
        for brand in BRAND_TOKENS:
            if brand == label or brand == folded:
                continue
            if brand in folded and brand != folded:
                return f"hostname '{label}' resembles brand '{brand}'"
            if abs(len(folded) - len(brand)) <= 1 and almost_equal(folded, brand):
                return f"hostname '{label}' is a near lookalike of '{brand}'"
    return None


def free_host_match(host: str) -> str | None:
    for suffix in FREE_HOST_SUFFIXES:
        if host.endswith(suffix) or host == suffix.lstrip("."):
            return suffix.lstrip(".")
    return None
