'use strict';

const { describe, it } = require('node:test');
const assert = require('node:assert/strict');
const {
  classifyRequest,
  firstPartyKey,
  partitionForUrl,
  applyHttpsOnly,
  decideNavigation,
  hostMatchesSuffix,
} = require('../main/privacy');

describe('privacy', () => {
  it('matches tracker host suffixes', () => {
    assert.equal(hostMatchesSuffix('www.google-analytics.com', 'google-analytics.com'), true);
    assert.equal(hostMatchesSuffix('example.com', 'google-analytics.com'), false);
  });

  it('classifies stub trackers as blocked', () => {
    const hit = classifyRequest('https://www.google-analytics.com/g/collect');
    assert.equal(hit.blocked, true);
    assert.equal(hit.reason, 'tracker-stub');
  });

  it('allows first-party navigations', () => {
    const hit = classifyRequest('https://example.com/index.html');
    assert.equal(hit.blocked, false);
  });

  it('derives first-party keys', () => {
    assert.equal(firstPartyKey('https://news.example.com/a'), 'example.com');
    assert.equal(firstPartyKey('https://localhost:8080/'), 'localhost');
  });

  it('builds isolation partitions', () => {
    assert.match(partitionForUrl('https://shop.example.org/x'), /^persist:fp-example\.org$/);
  });

  it('upgrades http when https-only + upgrade', () => {
    const r = applyHttpsOnly('http://example.com/a', { httpsOnly: true, upgradeHttp: true });
    assert.equal(r.action, 'upgrade');
    assert.equal(r.url, 'https://example.com/a');
  });

  it('decideNavigation cancels trackers when enabled', () => {
    const d = decideNavigation('https://doubleclick.net/tag', {
      blockTrackers: true,
      httpsOnly: true,
      upgradeHttp: true,
    });
    assert.equal(d.cancel, true);
  });

  it('decideNavigation redirects http under https-only', () => {
    const d = decideNavigation('http://example.com/', {
      blockTrackers: true,
      httpsOnly: true,
      upgradeHttp: true,
    });
    assert.equal(d.cancel, false);
    assert.equal(d.redirectURL, 'https://example.com/');
  });
});
