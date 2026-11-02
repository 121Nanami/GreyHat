"""Shannon entropy helpers for high-entropy string detection."""

from __future__ import annotations

import math
from collections import Counter


def shannon_entropy(s: str) -> float:
    if not s:
        return 0.0
    counts = Counter(s)
    length = len(s)
    return -sum((c / length) * math.log2(c / length) for c in counts.values())


def looks_high_entropy(token: str, *, min_len: int = 24, threshold: float = 4.2) -> bool:
    if len(token) < min_len:
        return False
    # Prefer base64/hex-ish alphabets
    allowed = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=_-")
    if any(ch not in allowed for ch in token):
        return False
    return shannon_entropy(token) >= threshold
