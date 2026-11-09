import assert from 'node:assert/strict';
import test from 'node:test';
import {getConfig} from '../examples/node/fetch.mjs';

test('proxy credentials are decoded and passed separately from the URI', () => {
  const c = getConfig({XPROXY_URL:'http://demo:p%40ss%3Aword@host:1234'});
  assert.equal(c.proxyUri,'http://host:1234');
  assert.equal(c.token,`Basic ${Buffer.from('demo:p@ss:word').toString('base64')}`);
});

test('IP-whitelist URI does not add proxy authentication', () => {
  assert.equal(getConfig({XPROXY_URL:'http://host:1234'}).token, undefined);
});

test('configuration errors do not echo credentials', () => {
  for(const uri of ['socks5://demo:PRIVATE@host:1234','http://demo:PRIVATE@host:bad','http://demo:PRIVATE@host:1234/path']) {
    assert.throws(()=>getConfig({XPROXY_URL:uri}),error=>!error.message.includes('PRIVATE'));
  }
});

test('non-finite and non-positive timeouts are rejected', () => {
  for(const timeout of ['NaN','Infinity','0','-1','301']) assert.throws(()=>getConfig({XPROXY_URL:'http://host:1234',XPROXY_TIMEOUT:timeout}));
});
