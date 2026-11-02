'use strict';

const { describe, it } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('fs');
const os = require('os');
const path = require('path');
const { normalizeSettings, loadSettings, saveSettings, DEFAULTS } = require('../main/settings');

describe('settings', () => {
  it('applies strict defaults', () => {
    const s = normalizeSettings({});
    assert.equal(s.httpsOnly, true);
    assert.equal(s.blockTrackers, true);
    assert.equal(s.clearOnQuit, true);
    assert.equal(s.proxy.enabled, false);
    assert.equal(s.homeUrl, DEFAULTS.homeUrl);
  });

  it('round-trips via disk', () => {
    const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'cove-settings-'));
    const file = path.join(dir, 'cove-settings.json');
    const saved = saveSettings(file, {
      proxy: { enabled: true, host: '127.0.0.1', port: 9050 },
      customCss: '.omnibox { font-size: 15px; }',
    });
    assert.equal(saved.proxy.enabled, true);
    const loaded = loadSettings(file);
    assert.equal(loaded.proxy.enabled, true);
    assert.equal(loaded.customCss, '.omnibox { font-size: 15px; }');
  });

  it('loadSettings returns defaults for missing file', () => {
    const s = loadSettings(path.join(os.tmpdir(), 'cove-missing-' + Date.now() + '.json'));
    assert.equal(s.httpsOnly, true);
  });
});
