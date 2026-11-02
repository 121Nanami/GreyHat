'use strict';

/**
 * Cove Browser — Electron main process.
 * Chromium shell with optional Tor SOCKS5, tracker stubs, clear-on-quit.
 */

const path = require('path');
const { app, BrowserWindow, session, ipcMain, Menu } = require('electron');
const { decideNavigation, partitionForUrl } = require('./privacy');
const { buildProxyConfig, proxyStatusLabel } = require('./proxy');
const {
  loadSettings,
  saveSettings,
  defaultSettingsPath,
  DEFAULTS,
} = require('./settings');

const SMOKE = process.argv.includes('--smoke');
const ROOT = path.join(__dirname, '..');

/** @type {import('./settings').normalizeSettings extends Function ? ReturnType<typeof import('./settings').normalizeSettings> : any} */
let settings = null;
let settingsPath = '';
/** @type {BrowserWindow | null} */
let mainWindow = null;
let blockCount = 0;

function attachPrivacyHandlers(ses) {
  ses.webRequest.onBeforeRequest({ urls: ['http://*/*', 'https://*/*'] }, (details, callback) => {
    const decision = decideNavigation(details.url, settings);
    if (decision.cancel) {
      blockCount += 1;
      if (mainWindow && !mainWindow.isDestroyed()) {
        mainWindow.webContents.send('privacy:blocked', {
          url: details.url,
          reason: decision.reason,
          total: blockCount,
        });
      }
      callback({ cancel: true });
      return;
    }
    if (decision.redirectURL) {
      callback({ redirectURL: decision.redirectURL });
      return;
    }
    callback({});
  });
}

async function applyProxy() {
  const cfg = buildProxyConfig(settings.proxy);
  await session.defaultSession.setProxy(cfg);
  // Also apply to common first-party partitions used by webviews.
  if (settings.firstPartyIsolation && settings.homeUrl) {
    const part = partitionForUrl(settings.homeUrl);
    const ses = session.fromPartition(part);
    await ses.setProxy(cfg);
    attachPrivacyHandlers(ses);
  }
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1280,
    height: 840,
    minWidth: 900,
    minHeight: 560,
    title: 'Cove Browser',
    backgroundColor: '#0f1419',
    webPreferences: {
      preload: path.join(ROOT, 'preload', 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
      webviewTag: true,
    },
  });

  Menu.setApplicationMenu(null);
  mainWindow.loadFile(path.join(ROOT, 'renderer', 'index.html'));

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

function registerIpc() {
  ipcMain.handle('settings:get', () => ({
    settings,
    proxyLabel: proxyStatusLabel(settings.proxy),
    blockCount,
    defaults: DEFAULTS,
  }));

  ipcMain.handle('settings:set', async (_evt, partial) => {
    settings = saveSettings(settingsPath, { ...settings, ...partial });
    await applyProxy();
    attachPrivacyHandlers(session.defaultSession);
    return {
      settings,
      proxyLabel: proxyStatusLabel(settings.proxy),
      blockCount,
    };
  });

  ipcMain.handle('privacy:partition', (_evt, url) => {
    if (!settings.firstPartyIsolation) return 'persist:cove-shared';
    return partitionForUrl(url || settings.homeUrl);
  });

  ipcMain.handle('app:paths', () => ({
    root: ROOT,
    theme: path.join(ROOT, settings.themeCssPath),
  }));
}

async function clearSessionData() {
  const ses = session.defaultSession;
  await ses.clearCache();
  await ses.clearStorageData();
}

app.whenReady().then(async () => {
  settingsPath = defaultSettingsPath(app.getPath('userData'));
  settings = loadSettings(settingsPath);
  registerIpc();
  attachPrivacyHandlers(session.defaultSession);
  await applyProxy();

  if (SMOKE) {
    // Headless-ish init check for CI / Windows CLI smoke without a lasting GUI.
    console.log('cove-smoke: settings ok');
    console.log('cove-smoke: proxy', proxyStatusLabel(settings.proxy));
    console.log('cove-smoke: httpsOnly', settings.httpsOnly);
    console.log('cove-smoke: blockTrackers', settings.blockTrackers);
    app.exit(0);
    return;
  }

  createWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('before-quit', async (e) => {
  if (!settings || !settings.clearOnQuit) return;
  e.preventDefault();
  try {
    await clearSessionData();
  } finally {
    settings.clearOnQuit = false; // avoid re-entry
    app.exit(0);
  }
});
