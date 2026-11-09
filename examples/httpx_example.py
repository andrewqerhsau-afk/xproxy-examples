"""Verify an exit IP with HTTPX's current singular `proxy` argument."""
import httpx

from .common import run_cli


def fetch(config):
    with httpx.Client(proxy=config.proxy_url, timeout=config.timeout, trust_env=False) as client:
        response = client.get(config.target_url)
        response.raise_for_status()
        return response.json()


if __name__ == "__main__":
    raise SystemExit(run_cli(fetch))
