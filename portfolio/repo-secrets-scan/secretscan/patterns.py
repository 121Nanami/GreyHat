"""Known secret patterns (detection only — never generates credentials)."""

from __future__ import annotations

import re
from dataclasses import dataclass

SKIP_DIR_NAMES = frozenset(
    {
        ".git",
        ".hg",
        ".svn",
        "node_modules",
        "vendor",
        "__pycache__",
        ".venv",
        "venv",
        "dist",
        "build",
        ".tox",
        ".mypy_cache",
        ".pytest_cache",
    }
)

SKIP_SUFFIXES = frozenset(
    {
        ".png",
        ".jpg",
        ".jpeg",
        ".gif",
        ".webp",
        ".ico",
        ".pdf",
        ".zip",
        ".gz",
        ".tar",
        ".woff",
        ".woff2",
        ".mp4",
        ".mp3",
        ".pyc",
        ".so",
        ".dll",
        ".exe",
        ".bin",
    }
)

MAX_FILE_BYTES = 1_500_000


@dataclass(frozen=True)
class Rule:
    id: str
    description: str
    regex: re.Pattern[str]
    severity: str = "high"


def _compile(pattern: str, flags: int = 0) -> re.Pattern[str]:
    return re.compile(pattern, flags)


RULES: list[Rule] = [
    Rule(
        "aws-access-key",
        "AWS access key id",
        _compile(r"\b(AKIA[0-9A-Z]{16})\b"),
    ),
    Rule(
        "github-pat",
        "GitHub personal access token",
        _compile(r"\b(ghp_[A-Za-z0-9]{36})\b"),
    ),
    Rule(
        "github-oauth",
        "GitHub oauth token",
        _compile(r"\b(gho_[A-Za-z0-9]{36})\b"),
    ),
    Rule(
        "slack-token",
        "Slack token",
        _compile(r"\b(xox[baprs]-[A-Za-z0-9-]{10,})\b"),
    ),
    Rule(
        "google-api-key",
        "Google API key",
        _compile(r"\b(AIza[0-9A-Za-z\-_]{35})\b"),
    ),
    Rule(
        "stripe-key",
        "Stripe live secret key",
        # Underscores allowed so docs fixtures (sk_live_TEST_ONLY_…) match
        # without looking like a live Stripe secret to host push protection.
        _compile(r"\b(sk_live_[0-9A-Za-z_]{24,})\b"),
    ),
    Rule(
        "private-key-header",
        "PEM private key header",
        _compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    ),
    Rule(
        "jwt",
        "JWT-shaped token",
        _compile(r"\beyJ[A-Za-z0-9_-]+\.eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b"),
        severity="medium",
    ),
    Rule(
        "generic-secret-assign",
        "High-entropy value assigned to secret-like key",
        _compile(
            r"(?i)(api[_-]?key|secret|passwd|password|token|auth)[\"'\s:=]+([\"']?)([A-Za-z0-9/\+=_\-]{20,})\2"
        ),
        severity="medium",
    ),
]
