"""Shared configuration; never put credentials in console output."""
from dataclasses import dataclass
import json
import math
import os
from pathlib import Path
import sys
from urllib.parse import unquote, urlsplit

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]


class ConfigError(ValueError):
    """A configuration error whose message never includes credentials."""



@dataclass(frozen=True, repr=False)
class Config:
    proxy_url: str
    target_url: str
    timeout: float

    def __repr__(self):
        return "Config(proxy_url=<redacted>, target_url=<configured>, timeout=%r)" % self.timeout


def get_config(environ=None):
    if environ is None:
        load_dotenv(ROOT / ".env", override=False)
        environ = os.environ
    proxy = environ.get("XPROXY_URL", "").strip()
    if not proxy or "USERNAME:PASSWORD@HOST:PORT" in proxy:
        raise ConfigError("Set XPROXY_URL to a real proxy URI from Generate.")
    try:
        parsed = urlsplit(proxy)
        valid = parsed.hostname and parsed.port and 1 <= parsed.port <= 65535
    except ValueError:
        valid = False
        parsed = None
    if not valid or parsed.scheme not in {"http", "https", "socks5", "socks5h"}:
        raise ConfigError("XPROXY_URL must include a supported scheme, host and numeric port.")
    if parsed.path not in {"", "/"} or parsed.query or parsed.fragment:
        raise ConfigError("A proxy URI must not contain a path, query or fragment.")
    if (parsed.username is None) != (parsed.password is None):
        raise ConfigError("Include both proxy username and password, or use IP-whitelist auth.")
    target = environ.get("XPROXY_TEST_URL", "https://api.ipify.org?format=json")
    try:
        url = urlsplit(target)
        if url.scheme not in {"http", "https"} or not url.hostname or url.username or url.password:
            raise ValueError
    except ValueError:
        raise ConfigError("XPROXY_TEST_URL must be an HTTP(S) URL without embedded credentials.") from None
    try:
        timeout = float(environ.get("XPROXY_TIMEOUT", "20"))
        if not math.isfinite(timeout) or not 0 < timeout <= 300:
            raise ValueError
    except ValueError:
        raise ConfigError("XPROXY_TIMEOUT must be between 0 and 300 seconds.") from None
    return Config(proxy, target, timeout)


def playwright_proxy(config):
    url = urlsplit(config.proxy_url)
    if url.scheme.startswith("socks") and url.username is not None:
        raise ConfigError("Chromium does not support authenticated SOCKS5 here. Choose HTTP in Generate.")
    scheme = "socks5" if url.scheme == "socks5h" else url.scheme
    host = f"[{url.hostname}]" if ":" in url.hostname else url.hostname
    settings = {"server": f"{scheme}://{host}:{url.port}"}
    if url.username is not None:
        settings.update(username=unquote(url.username), password=unquote(url.password))
    return settings


def run_cli(fetch):
    try:
        result = fetch(get_config())
        print(json.dumps(result, indent=2))
        return 0
    except ConfigError as exc:
        print(str(exc), file=sys.stderr)
    except Exception:
        # Library exceptions can include a credential-bearing URI or API key.
        print("Connection failed. Check credentials, pool balance, protocol and timeout. See docs/troubleshooting.md.", file=sys.stderr)
    return 1
