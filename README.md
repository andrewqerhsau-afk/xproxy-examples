<p align="center"><img src="assets/banner.svg" alt="XProxy — connect your stack" width="100%"></p>

<p align="center">
  <a href="https://github.com/andrewqerhsau-afk/xproxy-examples/actions/workflows/checks.yml"><img alt="Checks" src="https://github.com/andrewqerhsau-afk/xproxy-examples/actions/workflows/checks.yml/badge.svg"></a>
  <a href="LICENSE"><img alt="MIT license" src="https://img.shields.io/badge/license-MIT-A6C7AD?labelColor=18211F"></a>
  <img alt="Python 3.10+" src="https://img.shields.io/badge/Python-3.10%2B-A6C7AD?labelColor=18211F">
  <img alt="Node.js 22+" src="https://img.shields.io/badge/Node.js-22%2B-A6C7AD?labelColor=18211F">
</p>

# XProxy examples

Connect [XProxy](https://xproxy.space/) to **cURL, Python Requests, HTTPX, Playwright and Node.js**. Copy a proxy URI from your dashboard, run an example and check your exit IP.

[Create an account](https://xproxy.space/auth/register) · [API reference](https://xproxy.space/api-docs) · [Proxy formats](docs/proxy-formats.md) · [Troubleshooting](docs/troubleshooting.md)

## Start with one request

1. Create your XProxy account and save your login key.
2. Fund your wallet, choose a pool and buy traffic.
3. Open **Generate**. Choose your country, **HTTP**, and rotating or sticky mode.
4. Choose the `protocol_auth_host_port` output format and copy its URI.

```bash
export XPROXY_URL='http://USER:PASS@HOST:PORT'
curl --noproxy '' --proxy "$XPROXY_URL" \
  --connect-timeout 10 --max-time 20 \
  'https://api.ipify.org?format=json'
```

Replace every placeholder with the values from Generate. The result contains the **proxy's public exit IP**:

```json
{"ip": "198.51.100.42"}
```

That IP is an illustration from a documentation range. Your real response will differ.

## Choose an example

| Client | Run from the repository root | Proxy protocols in this example |
|---|---|---|
| [cURL](examples/curl/check.sh) | `bash examples/curl/check.sh` | HTTP(S), SOCKS5 / SOCKS5h |
| [Requests](examples/requests_example.py) | `python -m examples.requests_example` | HTTP(S), SOCKS5 / SOCKS5h |
| [HTTPX](examples/httpx_example.py) | `python -m examples.httpx_example` | HTTP(S), SOCKS5 / SOCKS5h |
| [Playwright](examples/playwright_example.py) | `python -m examples.playwright_example` | HTTP(S); unauthenticated SOCKS5 |
| [Node.js fetch](examples/node/fetch.mjs) | `npm run example:node` | HTTP(S) |

Protocol availability still depends on your selected XProxy pool. Chromium's authenticated SOCKS5 limitation is handled explicitly; choose HTTP for the browser example.

## Python setup

Python 3.10 or newer:

```bash
git clone https://github.com/andrewqerhsau-afk/xproxy-examples.git
cd xproxy-examples
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
```

On Windows PowerShell, activate with `.venv\Scripts\Activate.ps1` and copy with `Copy-Item .env.example .env`.

Edit `.env` and paste your actual URI into `XPROXY_URL`, then run:

```bash
python -m examples.requests_example
# or
python -m examples.httpx_example
```

Python examples load the root `.env` automatically. Existing environment variables take precedence. Both clients explicitly use the configured proxy instead of inheriting an unrelated system proxy.

For Playwright, install its package and browser:

```bash
python -m pip install -r requirements-playwright.txt
python -m playwright install chromium
python -m examples.playwright_example
```

## Node.js setup

Node.js 22 or newer. With your `.env` already configured:

```bash
npm ci
npm run example:node
```

The example uses Undici's `ProxyAgent` with explicit proxy authentication. To use already-exported environment variables instead of a `.env` file, run `node examples/node/fetch.mjs`.

## Configuration

| Variable | Purpose | Default |
|---|---|---|
| `XPROXY_URL` | Full generated proxy URI | Required |
| `XPROXY_TEST_URL` | HTTP(S) endpoint to request | `https://api.ipify.org?format=json` |
| `XPROXY_TIMEOUT` | Request timeout, seconds | `20` |
| `XPROXY_API_KEY` | Optional proxy-list API key | Used only by the API example |
| `XPROXY_BROWSER_PATH` | Optional existing Chromium executable | Playwright's installed browser |

To inspect location fields, set `XPROXY_TEST_URL=https://ipinfo.io/json`. Available fields, rate limits and geolocation accuracy are controlled by that endpoint. The examples print its actual JSON response; they do not manufacture a country or city.

Account login keys, API keys and proxy credentials have different purposes. Use the generated URI for these connection examples.

## Generate lists through the API

Set `XPROXY_API_KEY` in your ignored `.env` file, then:

```bash
python -m examples.generate_proxy_list --pool lite --country US --protocol http
```

The script saves returned URIs to an ignored `.proxy-list.txt` file instead of printing credentials. It refuses to overwrite an existing file. See [API usage](docs/api.md) for options and Datacenter behavior.

## Rotating, sticky and Datacenter

- **Rotating:** supported pools can change the exit IP between requests. One gateway URI can therefore return different IPs.
- **Sticky:** configure the session in Generate, then keep its generated credentials unchanged.
- **Datacenter:** fetch a fresh direct-IP list and switch addresses in your client. Username session suffixes do not rotate these addresses.

See [formats and sessions](docs/proxy-formats.md) before moving settings between pools.

## Watch the 38-second walkthrough

[![XProxy onboarding walkthrough](assets/walkthrough-cover.png)](assets/onboarding.mp4)

[Watch / download MP4](assets/onboarding.mp4). The video illustrates the workflow; its invoice, credentials and geolocation result are simulated.

## Checks

```bash
python -m unittest discover -s tests -v
npm test
```

The test suite uses a **local authenticated proxy fixture**. It checks Requests, HTTPX, cURL and Node.js routing, proxy authentication, browser configuration and credential-safe failures. Set `RUN_BROWSER_TESTS=1` after installing Chromium to include the Playwright browser smoke test. CI includes it.

These checks validate the examples' integration logic. They do not measure XProxy's live IP pool, success rates or latency.

## Help and contributions

- Setup issues: [troubleshooting](docs/troubleshooting.md) and [XProxy knowledge base](https://xproxy.space/knowledge-base).
- Accounts, payments or pool availability: [XProxy support](https://t.me/XproxySUP).
- Example bugs: [open an issue](https://github.com/andrewqerhsau-afk/xproxy-examples/issues/new/choose) with credentials removed.
- Improvements: see [CONTRIBUTING.md](CONTRIBUTING.md).

Code is released under the [MIT License](LICENSE). XProxy service access is provided separately through [xproxy.space](https://xproxy.space/).
