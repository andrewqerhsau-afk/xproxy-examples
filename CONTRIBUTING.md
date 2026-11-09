# Contributing

Small, runnable integrations and clearer setup instructions are welcome. Keep examples focused on connecting to a proxy and checking the result.

1. Fork the repository and create a branch.
2. Use placeholder credentials and local test fixtures.
3. Run `python -m unittest discover -s tests -v` and `npm test`.
4. Open a pull request describing what changed and how you checked it.

For browser checks, install `requirements-playwright.txt` and Chromium, then set `RUN_BROWSER_TESTS=1`. Local checks should not require a paid account or use someone else's endpoints for repeated requests.

Keep generated proxy lists and `.env` files out of commits. Use services and data sources according to their terms and XProxy's acceptable-use rules.
