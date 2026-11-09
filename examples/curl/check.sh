#!/usr/bin/env bash
# XPROXY_URL must be a generated URI including http:// or socks5h://.
set -euo pipefail

: "${XPROXY_URL:?Set XPROXY_URL to your generated proxy URI first}"
target="${XPROXY_TEST_URL:-https://api.ipify.org?format=json}"
timeout="${XPROXY_TIMEOUT:-20}"

# --noproxy '' prevents NO_PROXY from silently bypassing this explicit proxy.
# Avoid --verbose / --trace when sharing terminal output: they can expose auth.
curl --silent --show-error --fail \
  --noproxy '' \
  --connect-timeout 10 --max-time "$timeout" \
  --proxy "$XPROXY_URL" \
  "$target"
printf '\n'
