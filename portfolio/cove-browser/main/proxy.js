'use strict';

/**
 * Tor / SOCKS5 proxy helpers for Cove Browser.
 * Configures Electron session.setProxy — does not ship or start Tor.
 */

const DEFAULT_TOR = Object.freeze({
  host: '127.0.0.1',
  port: 9050,
  proxyType: 'socks5',
});

/**
 * @param {{ enabled: boolean, host?: string, port?: number }} opts
 * @returns {{ mode: string, proxyRules?: string, proxyBypassRules?: string }}
 */
function buildProxyConfig(opts) {
  if (!opts || !opts.enabled) {
    return { mode: 'direct' };
  }
  const host = String(opts.host || DEFAULT_TOR.host).trim() || DEFAULT_TOR.host;
  const port = Number(opts.port);
  const safePort = Number.isFinite(port) && port > 0 && port < 65536
    ? Math.trunc(port)
    : DEFAULT_TOR.port;

  // Electron: socks5://host:port routes TCP via SOCKS5 (Tor when local daemon listens).
  return {
    mode: 'fixed_servers',
    proxyRules: `socks5://${host}:${safePort}`,
    // Keep loopback out of the tunnel so local panels / about pages stay reachable.
    proxyBypassRules: '<-loopback>',
  };
}

/**
 * Human-readable status line for the chrome UI.
 * @param {{ enabled: boolean, host?: string, port?: number }} opts
 */
function proxyStatusLabel(opts) {
  if (!opts || !opts.enabled) return 'Direct (no Tor)';
  const cfg = buildProxyConfig(opts);
  return `Tor mode → ${cfg.proxyRules}`;
}

/**
 * Validate user-supplied proxy fields before persist.
 * @param {unknown} raw
 */
function normalizeProxySettings(raw) {
  const r = raw && typeof raw === 'object' ? raw : {};
  const enabled = !!r.enabled;
  const host = typeof r.host === 'string' && r.host.trim()
    ? r.host.trim()
    : DEFAULT_TOR.host;
  let port = Number(r.port);
  if (!Number.isFinite(port) || port <= 0 || port >= 65536) {
    port = DEFAULT_TOR.port;
  } else {
    port = Math.trunc(port);
  }
  return { enabled, host, port };
}

module.exports = {
  DEFAULT_TOR,
  buildProxyConfig,
  proxyStatusLabel,
  normalizeProxySettings,
};
