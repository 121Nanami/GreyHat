'use strict';

/**
 * Headless smoke — no Electron window required.
 * Validates privacy/proxy/settings modules and prints sample CLI output.
 */

const assert = require('node:assert/strict');
const path = require('path');
const fs = require('fs');
const os = require('os');

const privacy = require('../main/privacy');
const proxy = require('../main/proxy');
const settings = require('../main/settings');

function section(title) {
  console.log('\n=== ' + title + ' ===');
}

section('defaults');
const s = settings.normalizeSettings({});
console.log(JSON.stringify({
  httpsOnly: s.httpsOnly,
  blockTrackers: s.blockTrackers,
  clearOnQuit: s.clearOnQuit,
  firstPartyIsolation: s.firstPartyIsolation,
  proxy: s.proxy,
}, null, 2));
assert.equal(s.httpsOnly, true);
assert.equal(s.blockTrackers, true);

section('proxy config');
const off = proxy.buildProxyConfig({ enabled: false });
const on = proxy.buildProxyConfig({ enabled: true, host: '127.0.0.1', port: 9050 });
console.log('disabled →', off);
console.log('tor mode →', on);
console.log('label →', proxy.proxyStatusLabel({ enabled: true }));
assert.equal(off.mode, 'direct');
assert.equal(on.proxyRules, 'socks5://127.0.0.1:9050');

section('tracker stub decisions');
const samples = [
  'https://example.com/',
  'https://www.google-analytics.com/g/collect',
  'http://example.com/login',
  'https://doubleclick.net/ad',
];
for (const url of samples) {
  const d = privacy.decideNavigation(url, s);
  console.log(url);
  console.log('  →', d);
}

assert.equal(privacy.decideNavigation('https://example.com/', s).cancel, false);
assert.equal(privacy.decideNavigation('https://www.google-analytics.com/x', s).cancel, true);
assert.equal(
  privacy.decideNavigation('http://example.com/', s).redirectURL,
  'https://example.com/',
);

section('first-party isolation keys');
console.log('news.example.com →', privacy.partitionForUrl('https://news.example.com/a'));
assert.match(privacy.partitionForUrl('https://news.example.com/a'), /persist:fp-example\.com/);

section('settings persist');
const tmp = path.join(os.tmpdir(), 'cove-smoke-' + process.pid + '.json');
settings.saveSettings(tmp, { ...s, proxy: { enabled: true, host: '127.0.0.1', port: 9050 } });
const loaded = settings.loadSettings(tmp);
assert.equal(loaded.proxy.enabled, true);
fs.unlinkSync(tmp);
console.log('wrote+loaded', tmp, 'ok');

section('package shape');
const pkg = require('../package.json');
assert.equal(pkg.main, 'main/main.js');
assert.ok(pkg.scripts.start);
assert.ok(pkg.scripts.smoke);
assert.ok(pkg.scripts.test);
['main/main.js', 'main/privacy.js', 'main/proxy.js', 'main/settings.js',
  'preload/preload.js', 'renderer/index.html', 'renderer/app.js', 'renderer/styles.css',
  'themes/cove-dark.css', 'README.md'].forEach((rel) => {
  const p = path.join(__dirname, '..', rel);
  assert.ok(fs.existsSync(p), 'missing ' + rel);
  console.log('ok', rel);
});

console.log('\ncove-browser smoke: PASS');
