# Troubleshooting

## Missing or invalid XPROXY_URL

Copy `.env.example` to `.env`, replace the placeholder and run Python examples from the repository root. Use the standard form `http://USER:PASS@HOST:PORT`, including a numeric port. Node's `npm run example:node` loads the same `.env` file.

The cURL script reads exported environment variables; it does not source `.env` as shell code.

## HTTP 407 / authentication failure

Check your generated username/password, selected pool balance, or the current machine's public IP if you use IP-whitelist authentication. API keys and account login keys are not proxy credentials. Copy the entire generated URI, including any session suffixes.

## Timeout / connection refused

Confirm the protocol, host and port match Generate. Check the current pool and country availability, firewall access and balance. Fetch a fresh Datacenter list before use. Increase `XPROXY_TIMEOUT` only if a legitimate request needs more time.

## HTTPS target fails through the proxy

Keep the proxy scheme supplied by Generate. An HTTP proxy can tunnel requests to an HTTPS destination. Changing the proxy URI to `https://` just because the target is HTTPS can cause handshake failures.

TLS verification is enabled. If your network requires an organizational CA certificate, configure the client's documented CA trust settings; do not disable verification to conceal an error.

## Playwright / Chromium rejects SOCKS5 credentials

Use an authenticated **HTTP** proxy URI for this browser example. The code reports this limitation before launching Chromium. Configure credentials through Playwright's proxy `username` / `password` fields; `http_credentials` authenticates to websites and serves a different purpose.

If Chromium is missing, run `python -m playwright install chromium`. On Linux, Playwright may also require system dependencies; its [installation documentation](https://playwright.dev/python/docs/intro#installing-playwright) covers those.

## HTTPX reports an unexpected `proxies` argument

Use this repository's `httpx.Client(proxy=...)` example. Current HTTPX uses the singular `proxy` argument for this configuration.

## SOCKS dependency is missing

Install `requirements.txt`, which includes `requests[socks]` and `httpx[socks]`. This repository's Node example uses HTTP(S) proxies.

## Geolocation is different from the selection

Confirm country selection in Generate and that your client actually uses the proxy. Geolocation databases can disagree, especially at city level. `ipify` reports only an IP; use `XPROXY_TEST_URL=https://ipinfo.io/json` when you want that provider's location data. Provider rate limits can return errors independently of XProxy.

## What to include in a bug report

Include the example name, OS, runtime version, selected protocol and an error summary. Remove usernames, passwords, login keys, API keys, payment data and full credential-bearing URLs.

The examples intentionally keep network error messages generic because library tracebacks can include proxy credentials. For account, payment and live-pool issues, contact [XProxy support](https://t.me/XproxySUP).
