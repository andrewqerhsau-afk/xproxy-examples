"""Open the exit-IP endpoint in a proxied Chromium browser."""
import json
import os

from playwright.sync_api import sync_playwright

from .common import playwright_proxy, run_cli


def fetch(config):
    settings = playwright_proxy(config)
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            proxy=settings,
            executable_path=os.getenv("XPROXY_BROWSER_PATH") or None,
        )
        try:
            page = browser.new_page()
            response = page.goto(config.target_url, wait_until="domcontentloaded", timeout=config.timeout * 1000)
            if response is None or response.status >= 400:
                raise RuntimeError("The endpoint returned an unsuccessful HTTP status.")
            return json.loads(page.locator("body").inner_text())
        finally:
            browser.close()


if __name__ == "__main__":
    raise SystemExit(run_cli(fetch))
