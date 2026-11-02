"""Walk a tree and report likely secrets (defensive detection)."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .entropy import looks_high_entropy
from .patterns import MAX_FILE_BYTES, RULES, SKIP_DIR_NAMES, SKIP_SUFFIXES

TOKEN_RE = re.compile(r"[A-Za-z0-9+/=_\-]{24,}")


@dataclass
class Hit:
    path: str
    line: int
    rule_id: str
    severity: str
    excerpt: str
    description: str


@dataclass
class ScanReport:
    root: str
    files_scanned: int = 0
    hits: list[Hit] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "root": self.root,
            "files_scanned": self.files_scanned,
            "hit_count": len(self.hits),
            "hits": [asdict(h) for h in self.hits],
        }


def _should_skip_dir(name: str) -> bool:
    return name in SKIP_DIR_NAMES


def _should_skip_file(path: Path) -> bool:
    if path.suffix.lower() in SKIP_SUFFIXES:
        return True
    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            return True
    except OSError:
        return True
    return False


def _redact(s: str, keep: int = 4) -> str:
    s = s.strip()
    if len(s) <= keep * 2:
        return "***"
    return s[:keep] + "…" + s[-keep:]


def _scan_line(path: Path, lineno: int, line: str, report: ScanReport) -> None:
    for rule in RULES:
        for match in rule.regex.finditer(line):
            excerpt = _redact(match.group(0))
            # Avoid flagging obvious placeholders
            low = match.group(0).lower()
            if any(x in low for x in ("example", "changeme", "your_", "xxx", "placeholder", "dummy")):
                continue
            report.hits.append(
                Hit(
                    path=str(path),
                    line=lineno,
                    rule_id=rule.id,
                    severity=rule.severity,
                    excerpt=excerpt,
                    description=rule.description,
                )
            )
    # Extra entropy pass for bare tokens not already caught
    for tok in TOKEN_RE.findall(line):
        if looks_high_entropy(tok) and not any(r.regex.search(tok) for r in RULES if r.id != "generic-secret-assign"):
            # only if nearby secret keyword
            if re.search(r"(?i)(secret|token|password|api[_-]?key|credential)", line):
                if any(x in tok.lower() for x in ("example", "changeme", "placeholder")):
                    continue
                report.hits.append(
                    Hit(
                        path=str(path),
                        line=lineno,
                        rule_id="high-entropy",
                        severity="medium",
                        excerpt=_redact(tok),
                        description="High-entropy token near secret keyword",
                    )
                )


def scan_tree(root: Path) -> ScanReport:
    root = root.resolve()
    report = ScanReport(root=str(root))
    for path in root.rglob("*"):
        if path.is_dir():
            continue
        # skip if any parent is excluded
        if any(_should_skip_dir(part) for part in path.parts):
            continue
        if _should_skip_file(path):
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        report.files_scanned += 1
        rel = path.relative_to(root)
        for i, line in enumerate(text.splitlines(), start=1):
            _scan_line(rel, i, line, report)
    # Deduplicate identical path/line/rule
    seen: set[tuple] = set()
    unique: list[Hit] = []
    for hit in report.hits:
        key = (hit.path, hit.line, hit.rule_id, hit.excerpt)
        if key in seen:
            continue
        seen.add(key)
        unique.append(hit)
    report.hits = unique
    return report
