#!/usr/bin/env python3
from __future__ import annotations

import stat
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from nethygiene.checks import run_audit  # noqa: E402


class ChecksTests(unittest.TestCase):
    def test_fixture_files(self) -> None:
        td = ROOT / "testdata"
        with tempfile.TemporaryDirectory() as tmp:
            ssh = Path(tmp) / ".ssh"
            ssh.mkdir()
            ssh.chmod(0o700)
            key = ssh / "id_ed25519"
            key.write_text("DEMO-NOT-A-REAL-KEY\n", encoding="utf-8")
            key.chmod(0o600)
            report = run_audit(
                resolv=td / "resolv.conf",
                hosts=td / "hosts",
                ssh_dir=ssh,
                skip_listen=True,
            )
        self.assertTrue(any(f.check == "hosts" and f.severity == "medium" for f in report.findings))
        self.assertTrue(any(f.check == "resolv" for f in report.findings))
        self.assertTrue(any(f.check == "ssh" and f.severity == "info" for f in report.findings))

    def test_world_writable_ssh(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            ssh = Path(tmp) / ".ssh"
            ssh.mkdir()
            ssh.chmod(0o777)
            report = run_audit(
                resolv=ROOT / "testdata" / "resolv.conf",
                hosts=ROOT / "testdata" / "hosts",
                ssh_dir=ssh,
                skip_listen=True,
            )
        self.assertTrue(any(f.check == "ssh" and f.severity == "high" for f in report.findings))
        self.assertTrue(stat.S_IMODE((ROOT / "testdata" / "hosts").stat().st_mode) >= 0)


if __name__ == "__main__":
    unittest.main()
