"""Verify an exit IP with Requests; supports HTTP(S) and optional SOCKS."""
import requests

from .common import run_cli


def fetch(config):
    with requests.Session() as client:
        client.trust_env = False
        response = client.get(
            config.target_url,
            proxies={"http": config.proxy_url, "https": config.proxy_url},
            timeout=config.timeout,
        )
        response.raise_for_status()
        return response.json()


if __name__ == "__main__":
    raise SystemExit(run_cli(fetch))
