#!/usr/bin/env python3
"""Show TLS certificate expiry for host:port."""
from __future__ import annotations
import argparse
import socket
import ssl
import sys
from datetime import datetime, timezone


def main() -> int:
    p = argparse.ArgumentParser(description="TLS certificate expiry checker")
    p.add_argument("host")
    p.add_argument("-p", "--port", type=int, default=443)
    p.add_argument("-t", "--timeout", type=float, default=8.0)
    args = p.parse_args()
    ctx = ssl.create_default_context()
    try:
        with socket.create_connection((args.host, args.port), timeout=args.timeout) as raw:
            with ctx.wrap_socket(raw, server_hostname=args.host) as sock:
                cert = sock.getpeercert()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    not_after = cert.get("notAfter")
    # e.g. 'Jun 15 12:00:00 2027 GMT'
    expires = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    days = (expires - now).days
    subject = dict(x[0] for x in cert.get("subject", ()))
    issuer = dict(x[0] for x in cert.get("issuer", ()))
    print(f"host:    {args.host}:{args.port}")
    print(f"cn:      {subject.get('commonName', '?')}")
    print(f"issuer:  {issuer.get('organizationName') or issuer.get('commonName', '?')}")
    print(f"expires: {expires.isoformat()}  ({days} days)")
    return 0 if days > 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
