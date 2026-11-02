"""Read-only hygiene checks against local config and /proc (when present)."""

from __future__ import annotations

import os
import socket
import stat
from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass
class Finding:
    severity: str  # info | low | medium | high
    check: str
    message: str
    evidence: str = ""


@dataclass
class AuditReport:
    hostname: str
    findings: list[Finding] = field(default_factory=list)
    listening: list[dict] = field(default_factory=list)

    def add(self, severity: str, check: str, message: str, evidence: str = "") -> None:
        self.findings.append(Finding(severity, check, message, evidence))

    def to_dict(self) -> dict:
        return {
            "hostname": self.hostname,
            "listening": self.listening,
            "findings": [asdict(f) for f in self.findings],
            "summary": _summary(self.findings),
        }


def _summary(findings: list[Finding]) -> dict[str, int]:
    out: dict[str, int] = {}
    for f in findings:
        out[f.severity] = out.get(f.severity, 0) + 1
    return out


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def check_resolv(report: AuditReport, resolv: Path = Path("/etc/resolv.conf")) -> None:
    text = _read_text(resolv)
    if text is None:
        report.add("info", "resolv", f"Could not read {resolv} (skipped)")
        return
    nameservers = []
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("nameserver"):
            parts = line.split()
            if len(parts) >= 2:
                nameservers.append(parts[1])
    if not nameservers:
        report.add("medium", "resolv", "No nameserver entries in resolv.conf")
    for ns in nameservers:
        if ns in {"0.0.0.0", "127.0.0.1", "::1"}:
            report.add(
                "info",
                "resolv",
                "Local resolver in use (stub/DNS cache)",
                evidence=ns,
            )
        elif ns.startswith("8.8.") or ns.startswith("1.1.1.") or ns.startswith("9.9.9."):
            report.add(
                "info",
                "resolv",
                "Public recursive resolver configured",
                evidence=ns,
            )
        else:
            report.add("low", "resolv", "Custom nameserver — confirm it is trusted", evidence=ns)
    if "options edns0" not in text and "edns0" not in text:
        report.add("low", "resolv", "edns0 not explicitly enabled in resolv.conf")


def check_hosts(report: AuditReport, hosts: Path = Path("/etc/hosts")) -> None:
    text = _read_text(hosts)
    if text is None:
        report.add("info", "hosts", f"Could not read {hosts} (skipped)")
        return
    suspicious = 0
    for line in text.splitlines():
        raw = line.strip()
        if not raw or raw.startswith("#"):
            continue
        # Flag unexpected redirect-style mappings of popular brands (defensive awareness)
        lower = raw.lower()
        for brand in ("paypal", "apple.com", "microsoft", "google.com", "bank"):
            if brand in lower and not lower.startswith("127.") and "localhost" not in lower:
                # only flag if IP is not loopback-ish
                ip = raw.split()[0]
                if ip not in {"127.0.0.1", "::1"}:
                    suspicious += 1
                    report.add(
                        "medium",
                        "hosts",
                        f"Non-loopback hosts entry mentions '{brand}'",
                        evidence=raw[:120],
                    )
    if suspicious == 0:
        report.add("info", "hosts", "No suspicious brand redirects spotted in hosts file")


def _parse_proc_net(path: Path, ip_version: int) -> list[dict]:
    """Parse /proc/net/tcp{,6} listening sockets (state 0A)."""
    text = _read_text(path)
    if text is None:
        return []
    rows: list[dict] = []
    lines = text.strip().splitlines()
    if len(lines) < 2:
        return rows
    for line in lines[1:]:
        parts = line.split()
        if len(parts) < 4:
            continue
        local, state = parts[1], parts[3]
        if state != "0A":  # TCP_LISTEN
            continue
        ip_hex, port_hex = local.rsplit(":", 1)
        port = int(port_hex, 16)
        try:
            if ip_version == 4:
                raw = bytes.fromhex(ip_hex)
                # little-endian words on Linux
                ip = socket.inet_ntop(socket.AF_INET, raw[::-1])
            else:
                # IPv6: eight 32-bit little-endian words
                b = bytes.fromhex(ip_hex)
                words = [b[i : i + 4][::-1] for i in range(0, 16, 4)]
                ip = socket.inet_ntop(socket.AF_INET6, b"".join(words))
        except (ValueError, OSError):
            ip = ip_hex
        bind = "all" if ip in {"0.0.0.0", "::"} else "local" if ip in {"127.0.0.1", "::1"} else "iface"
        rows.append({"proto": f"tcp{ip_version}", "address": ip, "port": port, "bind": bind})
    return rows


def check_listening(report: AuditReport) -> None:
    rows = _parse_proc_net(Path("/proc/net/tcp"), 4) + _parse_proc_net(Path("/proc/net/tcp6"), 6)
    report.listening = rows
    if not rows:
        report.add(
            "info",
            "listen",
            "No listening TCP sockets parsed (no /proc or none listening)",
        )
        return
    public = [r for r in rows if r["bind"] == "all"]
    report.add("info", "listen", f"Found {len(rows)} listening TCP socket(s)", evidence=str(len(rows)))
    risky_ports = {21, 23, 69, 111, 135, 139, 445, 3389, 5900}
    for r in public:
        if r["port"] in risky_ports:
            report.add(
                "high",
                "listen",
                f"Historically sensitive port {r['port']} listening on all interfaces",
                evidence=f"{r['address']}:{r['port']}",
            )
        elif r["port"] < 1024:
            report.add(
                "low",
                "listen",
                f"Privileged port {r['port']} open on all interfaces",
                evidence=f"{r['address']}:{r['port']}",
            )
    if public and not any(f.check == "listen" and f.severity == "high" for f in report.findings):
        report.add(
            "info",
            "listen",
            f"{len(public)} socket(s) bound to all interfaces — review exposure",
            evidence=",".join(f"{r['port']}" for r in public[:12]),
        )


def check_ssh_dir(report: AuditReport, ssh_dir: Path | None = None) -> None:
    ssh_dir = ssh_dir or Path.home() / ".ssh"
    if not ssh_dir.exists():
        report.add("info", "ssh", f"No {ssh_dir} directory")
        return
    mode = ssh_dir.stat().st_mode
    if mode & (stat.S_IRWXG | stat.S_IRWXO):
        report.add(
            "high",
            "ssh",
            "~/.ssh is group/world accessible",
            evidence=oct(stat.S_IMODE(mode)),
        )
    else:
        report.add("info", "ssh", "~/.ssh permissions look restrictive", evidence=oct(stat.S_IMODE(mode)))
    for name in ("id_rsa", "id_ed25519", "id_ecdsa"):
        key = ssh_dir / name
        if not key.exists():
            continue
        km = key.stat().st_mode
        if km & (stat.S_IRGRP | stat.S_IROTH | stat.S_IWGRP | stat.S_IWOTH):
            report.add(
                "high",
                "ssh",
                f"Private key {name} is readable by group/others",
                evidence=oct(stat.S_IMODE(km)),
            )


def check_path_world_writable(report: AuditReport) -> None:
    path = os.environ.get("PATH", "")
    flagged = 0
    for entry in path.split(os.pathsep):
        if not entry:
            continue
        p = Path(entry)
        try:
            st = p.stat()
        except OSError:
            report.add("low", "path", f"PATH entry missing or unreadable: {entry}")
            continue
        if st.st_mode & stat.S_IWOTH:
            flagged += 1
            report.add("high", "path", "World-writable directory on PATH", evidence=entry)
    if flagged == 0:
        report.add("info", "path", "No world-writable PATH directories detected")


def run_audit(
    *,
    resolv: Path | None = None,
    hosts: Path | None = None,
    ssh_dir: Path | None = None,
    skip_listen: bool = False,
) -> AuditReport:
    report = AuditReport(hostname=socket.gethostname())
    check_resolv(report, resolv or Path("/etc/resolv.conf"))
    check_hosts(report, hosts or Path("/etc/hosts"))
    if not skip_listen:
        check_listening(report)
    check_ssh_dir(report, ssh_dir)
    check_path_world_writable(report)
    return report
