# net-hygiene-auditor

**Read-only** local network hygiene auditor for desktops and lab VMs.
It inspects DNS config, hosts file oddities, listening TCP sockets (via `/proc`),
SSH key permissions, and world-writable `PATH` entries — then explains findings.

## Problem

“Is this machine in a sane baseline state?” is a common internship / SOC-lite
question. Many checklists are tribal knowledge; a small auditor that prints
evidence helps interviews and personal hardening reviews.

## Solution

`nethygiene` runs **local, non-mutating** checks:

- `/etc/resolv.conf` — nameservers, edns0 hint
- `/etc/hosts` — non-loopback brand-like redirects
- `/proc/net/tcp{,6}` — listening sockets and risky ports on `0.0.0.0` / `::`
- `~/.ssh` — directory and private-key modes
- `$PATH` — world-writable directories

**Non-goals:** no port scanning of remote hosts, no exploit probes, no firewall
changes, no packet capture.

## How to run

```bash
cd docs/portfolio/net-hygiene-auditor
python3 -m nethygiene
python3 -m nethygiene --resolv testdata/resolv.conf --hosts testdata/hosts --skip-listen
python3 -m nethygiene -j
./smoke.sh
```

Exit code `1` if any **high** severity finding is present.

## Sample output

```
net-hygiene audit — host=demo
Findings:
  (info) resolv: Public recursive resolver configured [1.1.1.1]
  (low) resolv: edns0 not explicitly enabled in resolv.conf
  (medium) hosts: Non-loopback hosts entry mentions 'paypal' [203.0.113.50 paypal...]
  (info) ssh: ~/.ssh permissions look restrictive [0o700]
  (info) path: No world-writable PATH directories detected
```

## License

MIT
