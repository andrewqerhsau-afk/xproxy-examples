/** Verify an exit IP with Undici ProxyAgent. HTTP(S) proxy endpoints only. */
import {Buffer} from 'node:buffer';
import {pathToFileURL} from 'node:url';
import {ProxyAgent, fetch} from 'undici';

export function getConfig(env = process.env) {
  const raw = env.XPROXY_URL?.trim();
  if (!raw || raw.includes('USERNAME:PASSWORD@HOST:PORT')) {
    throw new Error('Set XPROXY_URL to your generated HTTP proxy URI.');
  }
  let proxy;
  try { proxy = new URL(raw); } catch { throw new Error('XPROXY_URL must be a valid proxy URI.'); }
  if (!['http:', 'https:'].includes(proxy.protocol)) throw new Error('This Node example uses HTTP(S) proxies. Choose HTTP in Generate.');
  if (!proxy.hostname || (proxy.pathname && proxy.pathname !== '/') || proxy.search || proxy.hash) throw new Error('Use a proxy URI with a host and no path, query or fragment.');
  if (Boolean(proxy.username) !== Boolean(proxy.password)) throw new Error('Include both proxy username and password, or use IP-whitelist auth.');
  let target;
  try { target = new URL(env.XPROXY_TEST_URL || 'https://api.ipify.org?format=json'); } catch { throw new Error('XPROXY_TEST_URL must be an HTTP(S) URL.'); }
  if (!['http:', 'https:'].includes(target.protocol) || target.username || target.password) throw new Error('XPROXY_TEST_URL must be an HTTP(S) URL without embedded credentials.');
  const timeout = Number(env.XPROXY_TIMEOUT || 20);
  if (!Number.isFinite(timeout) || timeout <= 0 || timeout > 300) throw new Error('XPROXY_TIMEOUT must be between 0 and 300 seconds.');
  let token;
  try {
    if (proxy.username) token = `Basic ${Buffer.from(`${decodeURIComponent(proxy.username)}:${decodeURIComponent(proxy.password)}`).toString('base64')}`;
  } catch { throw new Error('Proxy credentials must use valid percent-encoding.'); }
  proxy.username = ''; proxy.password = '';
  return {proxyUri: proxy.origin, token, targetUrl: target.href, timeout};
}

export async function checkExit(config) {
  const dispatcher = new ProxyAgent({uri: config.proxyUri, token: config.token});
  try {
    const response = await fetch(config.targetUrl, {dispatcher, signal: AbortSignal.timeout(Math.ceil(config.timeout * 1000))});
    if (!response.ok) throw new Error('The endpoint returned an unsuccessful status.');
    return await response.json();
  } finally {
    await dispatcher.close();
  }
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  let config;
  try { config = getConfig(); }
  catch (error) { console.error(error.message); process.exitCode = 1; }
  if (config) {
    try { console.log(JSON.stringify(await checkExit(config), null, 2)); }
    catch { console.error('Connection failed. Check credentials, balance, protocol and timeout. See docs/troubleshooting.md.'); process.exitCode = 1; }
  }
}
