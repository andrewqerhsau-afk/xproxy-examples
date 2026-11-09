"""Fetch a proxy list from the official API and save it to an ignored file."""
import argparse
import os
from pathlib import Path
import sys

from dotenv import load_dotenv
import requests

from .common import ROOT


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pool", choices=["lite", "res", "isp", "dc", "mobile", "unlimited"], default="lite")
    parser.add_argument("--protocol", choices=["http", "socks5", "udp"], default="http")
    parser.add_argument("--country", default="US")
    parser.add_argument("--mode", choices=["rotating", "sticky"], default="rotating")
    parser.add_argument("--limit", default="1")
    parser.add_argument("--output", type=Path, default=ROOT / ".proxy-list.txt")
    args = parser.parse_args(argv)
    if args.protocol == "udp" and args.pool not in {"lite", "isp"}:
        parser.error("UDP is documented only for LoRes (lite) and Shared ISP (isp).")
    if args.limit == "all":
        if args.pool != "dc":
            parser.error("--limit all is documented only for Datacenter.")
    elif not args.limit.isdecimal() or not 1 <= int(args.limit) <= 1000:
        parser.error("--limit must be 1–1000, or all for Datacenter.")
    if len(args.country) != 2 or not args.country.isalpha():
        parser.error("--country must be a two-letter country code.")
    if args.output.exists():
        print("Output already exists. Choose a new file to avoid overwriting it.", file=sys.stderr)
        return 1
    load_dotenv(ROOT / ".env", override=False)
    key = os.getenv("XPROXY_API_KEY", "").strip()
    if not key or key == "YOUR_API_KEY":
        print("Set XPROXY_API_KEY in .env or your environment.", file=sys.stderr)
        return 1
    params = dict(api_key=key, type=args.pool, protocol=args.protocol, country=args.country.upper(), mode=args.mode, limit=args.limit, output="protocol_auth_host_port")
    try:
        with requests.Session() as client:
            # Retain the machine's normal HTTPS/proxy configuration for the control API.
            response = client.get("https://xproxy.space/proxylist/", params=params, timeout=30, allow_redirects=False)
            if response.status_code != 200:
                print(f"API returned HTTP {response.status_code}. Check your API key, balance and parameters.", file=sys.stderr)
                return 1
            rows = [line.strip() for line in response.text.splitlines() if line.strip()]
            allowed_prefix = args.protocol + "://"
            if not rows or any(not row.startswith(allowed_prefix) for row in rows):
                print("The API did not return the requested proxy URI format. Check the dashboard and docs.", file=sys.stderr)
                return 1
            fd = os.open(args.output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "w", encoding="utf-8") as output:
                output.write("\n".join(rows) + "\n")
    except (requests.RequestException, OSError):
        print("Could not fetch or save the list. No credentials were printed.", file=sys.stderr)
        return 1
    print(f"Saved {len(rows)} proxy URI(s) to {args.output}. Keep this file private.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
