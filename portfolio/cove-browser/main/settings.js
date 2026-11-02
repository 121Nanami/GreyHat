'use strict';

const fs = require('fs');
const path = require('path');
const { normalizeProxySettings, DEFAULT_TOR } = require('./proxy');

const DEFAULTS = Object.freeze({
  proxy: { enabled: false, host: DEFAULT_TOR.host, port: DEFAULT_TOR.port },
  httpsOnly: true,
  upgradeHttp: true,
  blockTrackers: true,
  firstPartyIsolation: true,
  clearOnQuit: true,
  homeUrl: 'https://example.com',
  themeCssPath: 'themes/cove-dark.css',
  sidebarPanels: [
    { id: 'notes', title: 'Notes', url: 'about:blank' },
    { id: 'search', title: 'Search', url: 'https://duckduckgo.com/html/' },
  ],
  customCss: '',
});

/**
 * @param {unknown} raw
 */
function normalizeSettings(raw) {
  const r = raw && typeof raw === 'object' ? raw : {};
  const sidebar = Array.isArray(r.sidebarPanels)
    ? r.sidebarPanels
      .filter((p) => p && typeof p === 'object')
      .map((p, i) => ({
        id: String(p.id || `panel-${i}`),
        title: String(p.title || 'Panel'),
        url: String(p.url || 'about:blank'),
      }))
      .slice(0, 8)
    : DEFAULTS.sidebarPanels.map((p) => ({ ...p }));

  return {
    proxy: normalizeProxySettings(r.proxy),
    httpsOnly: r.httpsOnly !== false,
    upgradeHttp: r.upgradeHttp !== false,
    blockTrackers: r.blockTrackers !== false,
    firstPartyIsolation: r.firstPartyIsolation !== false,
    clearOnQuit: r.clearOnQuit !== false,
    homeUrl: typeof r.homeUrl === 'string' && r.homeUrl.trim()
      ? r.homeUrl.trim()
      : DEFAULTS.homeUrl,
    themeCssPath: typeof r.themeCssPath === 'string' && r.themeCssPath.trim()
      ? r.themeCssPath.trim()
      : DEFAULTS.themeCssPath,
    sidebarPanels: sidebar,
    customCss: typeof r.customCss === 'string' ? r.customCss : '',
  };
}

/**
 * @param {string} filePath
 */
function loadSettings(filePath) {
  try {
    if (!fs.existsSync(filePath)) return normalizeSettings(DEFAULTS);
    const text = fs.readFileSync(filePath, 'utf8');
    return normalizeSettings(JSON.parse(text));
  } catch {
    return normalizeSettings(DEFAULTS);
  }
}

/**
 * @param {string} filePath
 * @param {object} settings
 */
function saveSettings(filePath, settings) {
  const normalized = normalizeSettings(settings);
  const dir = path.dirname(filePath);
  fs.mkdirSync(dir, { recursive: true });
  fs.writeFileSync(filePath, JSON.stringify(normalized, null, 2) + '\n', 'utf8');
  return normalized;
}

function defaultSettingsPath(userDataDir) {
  return path.join(userDataDir, 'cove-settings.json');
}

module.exports = {
  DEFAULTS,
  normalizeSettings,
  loadSettings,
  saveSettings,
  defaultSettingsPath,
};
