# Cove Browser

**Chromium privacy browser scaffold** for Windows (and any Electron host): Chrome-like tabs/omnibox, optional local Tor SOCKS5 mode, strict privacy defaults, and a Vivaldi-style sidebar web-panels stub.

Defensive / portfolio project — **not** a Tor Browser replacement, not anonymity marketing.

## Problem

People want a familiar Chromium UX with clearer privacy levers (proxy, HTTPS preference, tracker blocking, clear-on-quit, light customization) without jumping straight into a full hardened distribution. Building that as a small Electron shell makes the architecture inspectable for interviews and experiments.

## What this is

| Layer | Choice |
|-------|--------|
| Shell | Electron (Chromium + Node main process) |
| UI | Custom chrome: tabs, omnibox, nav, settings drawer, sidebar panels |
| Proxy | Optional `socks5://127.0.0.1:9050` (user-supplied Tor daemon) |
| Privacy stubs | Request interception blocklist, HTTPS upgrade, first-party `session` partitions, clear-on-quit |
| Theme | CSS variables + user custom CSS hook |

## Threat model (honest limits)

**Assumes:** you control the machine; you may run a local Tor SOCKS proxy; you want *better defaults* and inspectable code, not nation-state resistance.

**Helps with (best-effort stubs):**

- Accidental clearnet when you meant to prefer Tor *if* the local daemon is up and you enabled Tor mode
- Third-party tracker hosts on a small curated suffix list
- HTTP → HTTPS upgrades when HTTPS-only is on
- Session leftover reduction via clear-on-quit
- Rough first-party isolation via Electron partitions (not full Tor Browser first-party isolation)

**Does *not* claim:**

- Tor Browser parity (no Tor launcher, no Torbutton, no Firefox ESR patchset, no letterboxing, no full fingerprint resistance)
- Protection if Tor is down, misconfigured, or bypassed by WebRTC/UDP (not fully locked down here)
- Completeness vs EasyList / uBlock; the tracker list is a **stub**
- Safety against malware, phishing sites, or deanonymization research tooling
- Shipping or managing Tor itself

If you need real anonymity, use **Tor Browser** (or a maintained hardened browser) and read its design docs. Cove is a learning / portfolio scaffold with honest knobs.

## Architecture

```
main/main.js        Electron lifecycle, IPC, webRequest hooks, proxy apply
main/privacy.js     Pure Node: tracker classify, HTTPS-only, FPI keys
main/proxy.js       Pure Node: SOCKS5 config builder
main/settings.js    Persist strict defaults to userData
preload/preload.js  contextBridge API (no nodeIntegration)
renderer/*          Tabs + omnibox + settings + sidebar panels (webview)
themes/cove-dark.css  Theme tokens / customization hook
tests/*             node:test + headless smoke (no GUI required)
```

## How to run (Windows)

Prerequisites: **Node.js 18+**, npm. Optional: [Tor Expert Bundle](https://www.torproject.org/download/tor/) or any SOCKS5 listener on `127.0.0.1:9050` for Tor mode.

```powershell
cd portfolio\cove-browser
npm install
npm start
```

Headless checks (no window):

```powershell
npm run smoke
npm test
# or
.\smoke.ps1
```

Optional Electron init smoke (downloads Electron; exits immediately):

```powershell
npx electron . --smoke
```

Linux/macOS: `npm start` / `bash smoke.sh` the same way.

### Tor mode

1. Start a local Tor SOCKS proxy on `127.0.0.1:9050`.
2. Open **Settings** → enable **Tor proxy mode**.
3. Badge shows `Tor`; traffic for the default session uses `socks5://127.0.0.1:9050` with loopback bypass.

If Tor is not running, navigations will fail while Tor mode is on — that is intentional fail-closed behavior for the proxy setting, not a silent clearnet fallback.

## Sample CLI output

```text
=== defaults ===
{
  "httpsOnly": true,
  "blockTrackers": true,
  "clearOnQuit": true,
  "firstPartyIsolation": true,
  "proxy": {
    "enabled": false,
    "host": "127.0.0.1",
    "port": 9050
  }
}

=== proxy config ===
disabled → { mode: 'direct' }
tor mode → {
  mode: 'fixed_servers',
  proxyRules: 'socks5://127.0.0.1:9050',
  proxyBypassRules: '<-loopback>'
}

=== tracker stub decisions ===
https://example.com/
  → { cancel: false }
https://www.google-analytics.com/g/collect
  → { cancel: true, reason: 'tracker-stub', host: 'www.google-analytics.com' }
http://example.com/login
  → { cancel: false, redirectURL: 'https://example.com/login', reason: 'https-upgrade' }

cove-browser smoke: PASS
```

(Captured via `npm run smoke`. GUI screenshots: run `npm start`, open Settings / sidebar — chrome is the deliverable visual.)

## Settings surface

- Tor SOCKS5 toggle + host/port
- HTTPS-only preference (upgrade HTTP)
- Tracker host blocking (stub list)
- First-party isolation (partition naming)
- Clear cache & storage on quit
- Home URL
- Custom CSS for browser chrome
- Sidebar web panels (Vivaldi-like stub)

## Roadmap

- [ ] Expand blocklist import (EasyList subset) behind a local file
- [ ] Explicit WebRTC / UDP policy toggles when Electron APIs allow
- [ ] Per-tab proxy override + circuit identity labels (still not Tor Browser)
- [ ] Packaged Windows portable build (`electron-builder`)
- [ ] Panel presets (notes / reader / password manager *links only*)

## Non-goals

No malware, no exploit packs, no “deanonymize Tor users” features, no phishing kits, no silent telemetry.

## License

MIT
