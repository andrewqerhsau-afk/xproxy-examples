# Proxy formats and sessions

The examples use **one full proxy URI** through `XPROXY_URL`:

```text
http://USER:PASS@HOST:PORT
```

Choose `protocol_auth_host_port` in Generate to obtain this form directly.

| Generator format | Shape | How to use it here |
|---|---|---|
| `auth_host_port` | `USER:PASS@HOST:PORT` | Prepend the protocol chosen in Generate, such as `http://` |
| `ip_port_user_pass` | `HOST:PORT:USER:PASS` | Put the same values into `http://USER:PASS@HOST:PORT` |
| `protocol_auth_host_port` | `http://USER:PASS@HOST:PORT` | Paste it directly |
| `protocol_ip_port_user_pass` | `http://HOST:PORT:USER:PASS` | Rearrange to `http://USER:PASS@HOST:PORT` |

The last format is a client-specific import format. It is not a standard URL. A host can be a gateway hostname or a direct IP; copy the address and port from the generator.

For IP-whitelist authentication, a URI may have no username or password. Whitelist the **public IP of the machine running the example** in the dashboard.

## HTTPS targets through an HTTP proxy

An `https://` destination can use an `http://` proxy endpoint:

```bash
curl --proxy "$XPROXY_URL" 'https://api.ipify.org?format=json'
```

The scheme at the start of `XPROXY_URL` describes the connection to the proxy, not the destination website. Use the protocol supplied by Generate. TLS verification remains enabled in all examples.

## SOCKS

Requests and cURL distinguish `socks5://` (local DNS resolution) from `socks5h://` (proxy-side DNS). The Python requirements include their SOCKS dependencies. HTTPX uses its own SOCKS transport; consult its documentation for transport behavior rather than assuming Requests' DNS semantics.

The Node example deliberately uses HTTP(S) proxy configuration. Chromium supports SOCKS5 without proxy username/password here; use an HTTP proxy URI for authenticated Playwright sessions.

## Credentials with special characters

Use the generated URI as provided. If you construct a URI manually, percent-encode reserved characters in the username and password, not the entire URL:

```python
from urllib.parse import quote

user = quote("my-user", safe="")
password = quote("p@ss:word", safe="")
uri = f"http://{user}:{password}@HOST:PORT"
```

The Playwright and Node examples decode the user-info into the authentication fields expected by their clients. They do not print it.

## Sessions

Use the dashboard to choose rotating or sticky mode. Keep the full generated URI intact; pool-specific username suffixes can encode session settings. This repository does not invent a universal suffix syntax.

Datacenter addresses are direct exits. The official documentation specifies HTTP port **777** and SOCKS5 port **666** for that pool. Fetch the current list before use and switch addresses in your client to rotate. These ports and rotation rules do not apply to every other pool.

Sources: [XProxy API](https://xproxy.space/api-docs), [Datacenter](https://xproxy.space/proxies/datacenter), [Requests proxy documentation](https://requests.readthedocs.io/en/latest/user/advanced/#proxies), [HTTPX proxies](https://www.python-httpx.org/advanced/proxies/), [Playwright proxy documentation](https://playwright.dev/python/docs/network#http-proxy).
