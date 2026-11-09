"""Integration checks use loopback only; no paid proxy or external endpoint."""
import base64
from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import select
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from types import SimpleNamespace
from unittest.mock import patch

from examples.common import ConfigError, get_config, playwright_proxy, run_cli
from examples import requests_example, httpx_example, generate_proxy_list

ROOT = Path(__file__).resolve().parents[1]
RESULT = {"ip": "198.51.100.42", "country": "US"}
AUTH = "Basic " + base64.b64encode(b"demo:p@ss:word").decode()


class QuietHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *args):
        pass

    def result(self):
        body = json.dumps(RESULT).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class Origin(QuietHandler):
    def do_GET(self):
        self.result()


class Proxy(QuietHandler):
    def authorized(self):
        header = self.headers.get("Proxy-Authorization")
        self.server.observed.append((self.command, self.path, header))
        if header == AUTH:
            return True
        self.send_response(407)
        self.send_header("Proxy-Authenticate", 'Basic realm="local-test"')
        self.send_header("Content-Length", "0")
        self.end_headers()
        return False

    def do_GET(self):
        if self.authorized():
            self.result()

    def do_CONNECT(self):
        if not self.authorized():
            return
        # Tunnel to our local origin, never the requested external host.
        with socket.create_connection(("127.0.0.1", self.server.origin_port), timeout=5) as target:
            self.send_response(200, "Connection established")
            self.end_headers()
            self.wfile.flush()
            for _ in range(200):
                ready, _, _ = select.select([self.connection, target], [], [], .1)
                for source in ready:
                    data = source.recv(65536)
                    if not data:
                        return
                    (target if source is self.connection else self.connection).sendall(data)


class ConfigTests(unittest.TestCase):
    def test_bad_inputs_never_echo_credentials(self):
        for uri in ["", "http://secret:password@HOST:PORT", "ftp://secret:password@host:1234", "http://secret:password@host:0", "http://secret:password@host:1234/path"]:
            with self.subTest(uri=uri), self.assertRaises(ConfigError) as exc:
                get_config({"XPROXY_URL": uri})
            self.assertNotIn("secret", str(exc.exception))
            self.assertNotIn("password@", str(exc.exception))

    def test_timeout_is_finite_and_positive(self):
        for timeout in ["nan", "inf", "0", "-1", "301"]:
            with self.subTest(timeout=timeout), self.assertRaises(ConfigError):
                get_config({"XPROXY_URL": "http://host:1234", "XPROXY_TIMEOUT": timeout})

    def test_proxy_auth_is_decoded_for_playwright(self):
        c = get_config({"XPROXY_URL": "http://demo:p%40ss%3Aword@[::1]:1234"})
        self.assertEqual(playwright_proxy(c), {"server": "http://[::1]:1234", "username": "demo", "password": "p@ss:word"})
        self.assertNotIn("p%40ss", repr(c))

    def test_authenticated_socks_is_rejected_for_chromium(self):
        with self.assertRaises(ConfigError):
            playwright_proxy(get_config({"XPROXY_URL": "socks5://demo:secret@host:1234"}))

    def test_whitelist_auth_is_supported(self):
        self.assertEqual(playwright_proxy(get_config({"XPROXY_URL": "http://host:1234"})), {"server": "http://host:1234"})

    def test_network_error_is_redacted(self):
        private = "http://demo:DO-NOT-PRINT@host:1234"
        def fail(config):
            raise ValueError(private)
        output = io.StringIO()
        with patch.dict(os.environ, {"XPROXY_URL": "http://host:1234"}), redirect_stderr(output):
            self.assertEqual(run_cli(fail), 1)
        self.assertNotIn("DO-NOT-PRINT", output.getvalue())


class LocalProxyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.origin = ThreadingHTTPServer(("127.0.0.1", 0), Origin)
        cls.proxy = ThreadingHTTPServer(("127.0.0.1", 0), Proxy)
        cls.proxy.origin_port = cls.origin.server_port
        cls.proxy.observed = []
        for server in [cls.origin, cls.proxy]:
            server.daemon_threads = True
            threading.Thread(target=server.serve_forever, daemon=True).start()
        cls.url = f"http://demo:p%40ss%3Aword@127.0.0.1:{cls.proxy.server_port}"
        cls.env = {"XPROXY_URL": cls.url, "XPROXY_TEST_URL": "http://example.test/exit", "XPROXY_TIMEOUT": "5", "NO_PROXY": "*"}

    @classmethod
    def tearDownClass(cls):
        for server in [cls.proxy, cls.origin]:
            server.shutdown()
            server.server_close()

    def assert_used_proxy(self, offset):
        entries = self.proxy.observed[offset:]
        self.assertTrue(entries)
        self.assertTrue(any(auth == AUTH for _, _, auth in entries))

    def test_requests_routes_and_authenticates(self):
        before = len(self.proxy.observed)
        with patch.dict(os.environ, {"NO_PROXY": "*"}):
            self.assertEqual(requests_example.fetch(get_config(self.env)), RESULT)
        self.assert_used_proxy(before)

    def test_httpx_routes_and_authenticates(self):
        before = len(self.proxy.observed)
        self.assertEqual(httpx_example.fetch(get_config(self.env)), RESULT)
        self.assert_used_proxy(before)

    @unittest.skipUnless(shutil.which("curl"), "cURL is not installed")
    def test_curl_uses_proxy_even_with_no_proxy_star(self):
        before = len(self.proxy.observed)
        r = subprocess.run(["bash", "examples/curl/check.sh"], cwd=ROOT, env={**os.environ, **self.env}, capture_output=True, text=True, timeout=10)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout), RESULT)
        self.assert_used_proxy(before)

    @unittest.skipUnless(shutil.which("node") and (ROOT / "node_modules/undici").exists(), "Run npm ci for the Node integration check")
    def test_node_routes_and_authenticates(self):
        before = len(self.proxy.observed)
        r = subprocess.run(["node", "examples/node/fetch.mjs"], cwd=ROOT, env={**os.environ, **self.env}, capture_output=True, text=True, timeout=10)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(json.loads(r.stdout), RESULT)
        self.assert_used_proxy(before)

    @unittest.skipUnless(os.getenv("RUN_BROWSER_TESTS") == "1", "Set RUN_BROWSER_TESTS=1 after installing Chromium")
    def test_playwright_routes_and_authenticates(self):
        from examples.playwright_example import fetch
        before = len(self.proxy.observed)
        self.assertEqual(fetch(get_config(self.env)), RESULT)
        self.assert_used_proxy(before)


class ApiTests(unittest.TestCase):
    def test_api_saves_uris_without_logging_key_or_credentials(self):
        secret = "PRIVATE-API-KEY"
        uri = "http://demo:PRIVATE-PROXY-PASS@host:1234"
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / ".proxy-list.txt"
            output = io.StringIO()
            with patch.dict(os.environ, {"XPROXY_API_KEY": secret}), patch("examples.generate_proxy_list.requests.Session") as session, redirect_stdout(output):
                session.return_value.__enter__.return_value.get.return_value = SimpleNamespace(status_code=200, text=uri + "\n")
                self.assertEqual(generate_proxy_list.main(["--output", str(path)]), 0)
            self.assertEqual(path.read_text(), uri + "\n")
            self.assertNotIn(secret, output.getvalue())
            self.assertNotIn("PRIVATE-PROXY-PASS", output.getvalue())
            if os.name == "posix":
                self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_api_http_error_does_not_print_response_or_key(self):
        output = io.StringIO()
        with tempfile.TemporaryDirectory() as folder, patch.dict(os.environ, {"XPROXY_API_KEY": "PRIVATE-API-KEY"}), patch("examples.generate_proxy_list.requests.Session") as session, redirect_stderr(output):
            session.return_value.__enter__.return_value.get.return_value = SimpleNamespace(status_code=403, text="PRIVATE-API-KEY")
            self.assertEqual(generate_proxy_list.main(["--output", str(Path(folder) / "new.txt")]), 1)
        self.assertNotIn("PRIVATE-API-KEY", output.getvalue())


if __name__ == "__main__":
    unittest.main()
