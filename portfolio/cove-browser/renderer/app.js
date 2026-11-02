'use strict';

/** @typedef {{ id: string, title: string, url: string, webview: Electron.WebviewTag }} Tab */

/** @type {Tab[]} */
const tabs = [];
let activeId = null;
/** @type {any} */
let settings = null;

function $(id) {
  return document.getElementById(id);
}

function normalizeUrl(input) {
  const raw = String(input || '').trim();
  if (!raw) return settings?.homeUrl || 'https://example.com';
  if (/^[a-z][a-z0-9+.-]*:/i.test(raw)) return raw;
  if (raw.includes(' ') || !raw.includes('.')) {
    return 'https://duckduckgo.com/html/?q=' + encodeURIComponent(raw);
  }
  return 'https://' + raw;
}

async function refreshChrome() {
  const data = await window.cove.getSettings();
  settings = data.settings;
  const badge = $('proxy-badge');
  badge.textContent = settings.proxy.enabled ? 'Tor' : 'Direct';
  badge.classList.toggle('tor', !!settings.proxy.enabled);
  badge.title = data.proxyLabel;
  $('block-badge').textContent = `${data.blockCount} blocked`;
  applyCustomCss(settings.customCss || '');
  renderPanels();
}

function applyCustomCss(css) {
  let el = document.getElementById('cove-user-css');
  if (!el) {
    el = document.createElement('style');
    el.id = 'cove-user-css';
    document.head.appendChild(el);
  }
  el.textContent = css;
}

function renderTabs() {
  const root = $('tabs');
  root.innerHTML = '';
  for (const tab of tabs) {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'tab' + (tab.id === activeId ? ' active' : '');
    btn.setAttribute('role', 'tab');
    btn.setAttribute('aria-selected', tab.id === activeId ? 'true' : 'false');

    const title = document.createElement('span');
    title.className = 'tab-title';
    title.textContent = tab.title;
    btn.appendChild(title);

    const close = document.createElement('button');
    close.type = 'button';
    close.className = 'tab-close';
    close.title = 'Close tab';
    close.textContent = '×';
    close.addEventListener('click', (e) => {
      e.stopPropagation();
      closeTab(tab.id);
    });
    btn.appendChild(close);

    btn.addEventListener('click', () => activateTab(tab.id));
    root.appendChild(btn);
  }
}

function activeTab() {
  return tabs.find((t) => t.id === activeId) || null;
}

async function createTab(url) {
  const id = 't' + Math.random().toString(36).slice(2, 9);
  const target = normalizeUrl(url);
  const partition = await window.cove.partitionFor(target);

  const webview = document.createElement('webview');
  webview.setAttribute('partition', partition);
  webview.setAttribute('allowpopups', 'false');
  webview.className = 'hidden';
  webview.src = target;

  /** @type {Tab} */
  const tab = { id, title: 'New tab', url: target, webview };
  tabs.push(tab);
  $('views').appendChild(webview);

  webview.addEventListener('page-title-updated', (e) => {
    tab.title = e.title || tab.url;
    renderTabs();
  });
  webview.addEventListener('did-navigate', (e) => {
    tab.url = e.url;
    if (tab.id === activeId) $('omnibox').value = e.url;
  });
  webview.addEventListener('did-navigate-in-page', (e) => {
    tab.url = e.url;
    if (tab.id === activeId) $('omnibox').value = e.url;
  });

  activateTab(id);
  return tab;
}

function activateTab(id) {
  activeId = id;
  for (const tab of tabs) {
    tab.webview.classList.toggle('hidden', tab.id !== id);
  }
  const tab = activeTab();
  if (tab) $('omnibox').value = tab.url;
  renderTabs();
}

function closeTab(id) {
  const idx = tabs.findIndex((t) => t.id === id);
  if (idx < 0) return;
  const [tab] = tabs.splice(idx, 1);
  tab.webview.remove();
  if (tabs.length === 0) {
    createTab(settings?.homeUrl);
    return;
  }
  if (activeId === id) {
    activateTab(tabs[Math.max(0, idx - 1)].id);
  } else {
    renderTabs();
  }
}

function navigate(raw) {
  const tab = activeTab();
  if (!tab) return;
  const url = normalizeUrl(raw);
  tab.url = url;
  tab.webview.src = url;
  $('omnibox').value = url;
}

function renderPanels() {
  const list = $('panel-list');
  list.innerHTML = '';
  const panels = settings?.sidebarPanels || [];
  panels.forEach((p, i) => {
    const chip = document.createElement('button');
    chip.type = 'button';
    chip.className = 'panel-chip' + (i === 0 ? ' active' : '');
    chip.textContent = p.title;
    chip.addEventListener('click', () => {
      list.querySelectorAll('.panel-chip').forEach((c) => c.classList.remove('active'));
      chip.classList.add('active');
      $('panel-view').src = p.url;
    });
    list.appendChild(chip);
  });
  if (panels[0]) $('panel-view').src = panels[0].url;
}

function fillSettingsForm() {
  $('set-tor').checked = !!settings.proxy.enabled;
  $('set-tor-host').value = settings.proxy.host;
  $('set-tor-port').value = String(settings.proxy.port);
  $('set-https').checked = !!settings.httpsOnly;
  $('set-trackers').checked = !!settings.blockTrackers;
  $('set-fpi').checked = !!settings.firstPartyIsolation;
  $('set-clear').checked = !!settings.clearOnQuit;
  $('set-home').value = settings.homeUrl;
  $('set-css').value = settings.customCss || '';
}

async function saveSettingsFromForm() {
  const partial = {
    proxy: {
      enabled: $('set-tor').checked,
      host: $('set-tor-host').value,
      port: Number($('set-tor-port').value),
    },
    httpsOnly: $('set-https').checked,
    upgradeHttp: true,
    blockTrackers: $('set-trackers').checked,
    firstPartyIsolation: $('set-fpi').checked,
    clearOnQuit: $('set-clear').checked,
    homeUrl: $('set-home').value,
    customCss: $('set-css').value,
  };
  const data = await window.cove.setSettings(partial);
  settings = data.settings;
  $('settings-status').textContent = 'Saved.';
  await refreshChrome();
}

function wireUi() {
  $('btn-new-tab').addEventListener('click', () => createTab(settings.homeUrl));
  $('btn-back').addEventListener('click', () => activeTab()?.webview.goBack());
  $('btn-forward').addEventListener('click', () => activeTab()?.webview.goForward());
  $('btn-reload').addEventListener('click', () => activeTab()?.webview.reload());
  $('btn-home').addEventListener('click', () => navigate(settings.homeUrl));
  $('nav-form').addEventListener('submit', (e) => {
    e.preventDefault();
    navigate($('omnibox').value);
  });

  $('btn-sidebar').addEventListener('click', () => {
    $('sidebar').classList.toggle('hidden');
  });
  $('btn-settings').addEventListener('click', () => {
    fillSettingsForm();
    $('settings').classList.remove('hidden');
  });
  $('btn-close-settings').addEventListener('click', () => {
    $('settings').classList.add('hidden');
  });
  $('btn-save-settings').addEventListener('click', () => {
    saveSettingsFromForm().catch((err) => {
      $('settings-status').textContent = String(err);
    });
  });

  window.cove.onBlocked((payload) => {
    $('block-badge').textContent = `${payload.total} blocked`;
  });
}

async function boot() {
  wireUi();
  await refreshChrome();
  await createTab(settings.homeUrl);
}

boot().catch((err) => {
  console.error(err);
  document.body.innerHTML = '<pre style="padding:24px;color:#c45c5c">Cove failed to start:\n' +
    String(err) + '</pre>';
});
