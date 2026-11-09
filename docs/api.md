# Proxy-list API

Run the API example with an API key from dashboard Settings:

```bash
python -m examples.generate_proxy_list \
  --pool lite --country US --protocol http --mode rotating --limit 1
```

API keys authenticate calls to `https://xproxy.space/proxylist/`. They are separate from your account login key and generated proxy username/password. The documented API authenticates via the `api_key` query parameter, so avoid sharing full request URLs.

The script requests `protocol_auth_host_port` output and writes the result to `.proxy-list.txt`, which is ignored by Git. POSIX systems create the file with owner-only permissions. On Windows, use your normal private user directory and file access controls.

The endpoint response is expected to contain proxy URIs, one per line. No returned credentials are printed by this script. It fails if the format is unexpected or the output file already exists.

## Options

| Option | Values / meaning |
|---|---|
| `--pool` | `lite`, `res`, `isp`, `dc`, `mobile`, `unlimited`, as documented by XProxy |
| `--country` | Two-letter country code, subject to pool availability |
| `--protocol` | `http`, `socks5`, `udp`; UDP documented for `lite` and `isp` |
| `--mode` | `rotating` or `sticky` |
| `--limit` | `1`–`1000`; `all` for Datacenter |
| `--output` | Output file; default `.proxy-list.txt` |

For rotating gateways, the API documentation says the generator returns one line. You can reuse that gateway URI for successive requests.

Datacenter's `rotating` mode shuffles the returned list; your client must still switch direct addresses. Session/time suffixes do not rotate a direct IP.

The script makes one API request and does not retry purchases, create payments or loop over endpoints. API results can depend on the account balance and active pool.

For advanced session parameters and the current contract, use the [official API reference](https://xproxy.space/api-docs).
