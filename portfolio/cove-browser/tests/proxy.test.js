'use strict';

const { describe, it } = require('node:test');
const assert = require('node:assert/strict');
const {
  buildProxyConfig,
  proxyStatusLabel,
  normalizeProxySettings,
  DEFAULT_TOR,
} = require('../main/proxy');

describe('proxy', () => {
  it('returns direct mode when disabled', () => {
    assert.deepEqual(buildProxyConfig({ enabled: false }), { mode: 'direct' });
  });

  it('builds socks5 rules for Tor defaults', () => {
    const cfg = buildProxyConfig({ enabled: true });
    assert.equal(cfg.mode, 'fixed_servers');
    assert.equal(cfg.proxyRules, `socks5://${DEFAULT_TOR.host}:${DEFAULT_TOR.port}`);
    assert.equal(cfg.proxyBypassRules, '<-loopback>');
  });

  it('normalizes bad ports to default', () => {
    const n = normalizeProxySettings({ enabled: true, host: '127.0.0.1', port: 99999 });
    assert.equal(n.port, DEFAULT_TOR.port);
  });

  it('labels status for UI', () => {
    assert.match(proxyStatusLabel({ enabled: false }), /Direct/);
    assert.match(proxyStatusLabel({ enabled: true }), /Tor mode/);
  });
});
