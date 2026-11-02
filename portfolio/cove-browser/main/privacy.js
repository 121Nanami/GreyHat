'use strict';

/**
 * Privacy helpers for Cove Browser.
 * Tracker blocking stubs + first-party URL helpers.
 * Pure Node — no Electron import — so unit tests and smoke stay headless.
 */

/** Curated stub blocklist (host suffixes). Not a full EasyList replacement. */
const TRACKER_HOST_SUFFIXES = Object.freeze([
  'doubleclick.net',
  'google-analytics.com',
  'googletagmanager.com',
  'facebook.net',
  'facebook.com',
  'scorecardresearch.com',
  'adservice.google.com',
  'adnxs.com',
  'adsrvr.org',
  'taboola.com',
  'outbrain.com',
  'hotjar.com',
  'mixpanel.com',
  'segment.io',
  'sentry.io',
]);

/**
 * @param {string} hostname
 * @param {string} suffix
 */
function hostMatchesSuffix(hostname, suffix) {
  const h = String(hostname || '').toLowerCase().replace(/\.$/, '');
  const s = String(suffix || '').toLowerCase();
  if (!h || !s) return false;
  return h === s || h.endsWith('.' + s);
}

/**
 * @param {string} urlString
 * @returns {{ blocked: boolean, reason?: string, host?: string }}
 */
function classifyRequest(urlString) {
  let host = '';
  try {
    host = new URL(urlString).hostname;
  } catch {
    return { blocked: false, reason: 'unparseable' };
  }
  for (const suffix of TRACKER_HOST_SUFFIXES) {
    if (hostMatchesSuffix(host, suffix)) {
      return { blocked: true, reason: 'tracker-stub', host };
    }
  }
  return { blocked: false, host };
}

/**
 * Registrable-ish first party key for isolation stubs.
 * Uses last two labels for dotted hosts; keeps localhost / IPs as-is.
 * @param {string} urlString
 */
function firstPartyKey(urlString) {
  let host = '';
  try {
    host = new URL(urlString).hostname.toLowerCase();
  } catch {
    return 'unknown';
  }
  if (!host || host === 'localhost' || /^\d+\.\d+\.\d+\.\d+$/.test(host)) {
    return host || 'unknown';
  }
  const parts = host.split('.').filter(Boolean);
  if (parts.length <= 2) return host;
  return parts.slice(-2).join('.');
}

/**
 * Session partition name for first-party isolation stub.
 * @param {string} urlString
 */
function partitionForUrl(urlString) {
  const key = firstPartyKey(urlString).replace(/[^a-z0-9.-]/gi, '_');
  return `persist:fp-${key}`;
}

/**
 * HTTPS-only preference: upgrade http→https when safe to try,
 * or mark as blocked when upgrade is disabled and policy is strict.
 * @param {string} urlString
 * @param {{ httpsOnly: boolean, upgradeHttp: boolean }} opts
 */
function applyHttpsOnly(urlString, opts) {
  const { httpsOnly, upgradeHttp } = opts;
  let u;
  try {
    u = new URL(urlString);
  } catch {
    return { action: 'allow', url: urlString };
  }
  if (u.protocol !== 'http:') {
    return { action: 'allow', url: urlString };
  }
  if (!httpsOnly) {
    return { action: 'allow', url: urlString };
  }
  if (upgradeHttp) {
    u.protocol = 'https:';
    return { action: 'upgrade', url: u.toString() };
  }
  return { action: 'block', url: urlString, reason: 'https-only' };
}

/**
 * Build a webRequest filter decision for Electron session.webRequest.
 * @param {string} urlString
 * @param {{ blockTrackers: boolean, httpsOnly: boolean, upgradeHttp: boolean }} settings
 */
function decideNavigation(urlString, settings) {
  const https = applyHttpsOnly(urlString, {
    httpsOnly: !!settings.httpsOnly,
    upgradeHttp: settings.upgradeHttp !== false,
  });
  if (https.action === 'block') {
    return { cancel: true, reason: https.reason };
  }
  if (https.action === 'upgrade') {
    return { cancel: false, redirectURL: https.url, reason: 'https-upgrade' };
  }
  if (settings.blockTrackers) {
    const c = classifyRequest(urlString);
    if (c.blocked) {
      return { cancel: true, reason: c.reason, host: c.host };
    }
  }
  return { cancel: false };
}

module.exports = {
  TRACKER_HOST_SUFFIXES,
  hostMatchesSuffix,
  classifyRequest,
  firstPartyKey,
  partitionForUrl,
  applyHttpsOnly,
  decideNavigation,
};
