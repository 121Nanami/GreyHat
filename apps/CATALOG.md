# GreyHatInc App Factory Catalog

**“Random” = useful tools with no required shared theme** — things people would actually run (CLI/scripts/small apps with a job). Not decorative demos, landing-page fluff, or essay filler.

Status: **shipped** = runnable under `docs/apps/<kebab-name>/` with README + how to run.

---

## Ellen Joe / BlackArch spin helpers

| Idea | Stack | Status |
|------|-------|--------|
| Ellen Checksum Desk — verify download digests | Python | **shipped** → [`apps/ellen-checksum-desk/`](apps/ellen-checksum-desk/) |
| ISO Checksum Verifier — ISO/image digest check | Python | **shipped** → [`apps/iso-checksum-verifier/`](apps/iso-checksum-verifier/) |
| Firewall Profile Switcher — preview-only profiles | HTML/JS | **shipped** → [`apps/firewall-profile-switcher/`](apps/firewall-profile-switcher/) |
| Harden Checklist — safer-defaults checklist | HTML/JS | **shipped** → [`apps/harden-checklist/`](apps/harden-checklist/) |
| Mirror Pulse — mirror latency HEAD probe | Python | **shipped** → [`apps/mirror-pulse/`](apps/mirror-pulse/) |
| Mirror Speed Tester — multi-round median probe | Python | **shipped** → [`apps/mirror-speed-tester/`](apps/mirror-speed-tester/) |
| Mirrorlist Filter — country / HTTPS / enable | Python | **shipped** → [`apps/mirrorlist-filter/`](apps/mirrorlist-filter/) |
| Firstboot Cove — first-boot wizard mock | HTML/JS | **shipped** → [`apps/firstboot-cove/`](apps/firstboot-cove/) |
| First-Boot Wizard — network/privacy/wallpaper mock | HTML/JS | **shipped** → [`apps/first-boot-wizard/`](apps/first-boot-wizard/) |
| Wallpaper Pack Manager — pack metadata stub | Python | **shipped** → [`apps/wallpaper-pack-manager/`](apps/wallpaper-pack-manager/) |
| Update Notifier Demo — fake pacman -Qu digest | Python | **shipped** → [`apps/update-notifier-demo/`](apps/update-notifier-demo/) |
| Locale Lighthouse — LANG/TZ suggestions | Python | **shipped** → [`apps/locale-lighthouse/`](apps/locale-lighthouse/) |
| Backup Beacon — 3-2-1 backup checklist | HTML/JS | **shipped** → [`apps/backup-beacon/`](apps/backup-beacon/) |
| Hosts Merge — merge hosts snippets safely | Python | **shipped** → [`apps/hosts-merge/`](apps/hosts-merge/) |
| Package Audit Checklist — pacman/spin review TUI | Python | **shipped** → [`apps/package-audit-checklist/`](apps/package-audit-checklist/) |
| Sysctl Hardening Recommender — read-only advice | Python | **shipped** → [`apps/sysctl-hardening-recommender/`](apps/sysctl-hardening-recommender/) |
| Kernel Cmdline Advisor — boot param notes | Python | **shipped** → [`apps/kernel-cmdline-advisor/`](apps/kernel-cmdline-advisor/) |
| PKGBUILD Linter — heuristic PKGBUILD checks | Python | **shipped** → [`apps/pkgbuild-linter/`](apps/pkgbuild-linter/) |
| Pacman Hook List — summarize alpm hooks | Python | **shipped** → [`apps/pacman-hook-list/`](apps/pacman-hook-list/) |
| Desktop Entry Lint — `.desktop` packaging checks | Python | **shipped** → [`apps/desktop-entry-lint/`](apps/desktop-entry-lint/) |
| SHA256SUMS Make — digests / PKGBUILD array | Python | **shipped** → [`apps/sha256sums-make/`](apps/sha256sums-make/) |
| Needs Restart Hint — reboot heuristics | Python | **shipped** → [`apps/needs-restart-hint/`](apps/needs-restart-hint/) |
| Unit File Peek — systemd unit summary | Python | **shipped** → [`apps/unit-file-peek/`](apps/unit-file-peek/) |
| Privacy Defaults Checklist | HTML/JS | **shipped** → [`apps/privacy-defaults-checklist/`](apps/privacy-defaults-checklist/) |
| Service Harden Checklist | HTML/JS | **shipped** → [`apps/service-harden-checklist/`](apps/service-harden-checklist/) |
| Secure Boot Status Reader | Shell | planned |
| Flatpak Permission Auditor | Python | planned |
| LUKS Reminder Card (pre-install) | HTML/JS | planned |

---

## File & disk utilities

| Idea | Stack | Status |
|------|-------|--------|
| Archive Peek — list zip/tar without extract | Python | **shipped** → [`apps/archive-peek/`](apps/archive-peek/) |
| DU Top — largest children of a directory | Python | **shipped** → [`apps/du-top/`](apps/du-top/) |
| Tree Size — recursive disk-usage tree | Python | **shipped** → [`apps/tree-size/`](apps/tree-size/) |
| Large Files — biggest files under a tree | Python | **shipped** → [`apps/large-files/`](apps/large-files/) |
| Find Dupes — size + SHA-256 duplicates | Python | **shipped** → [`apps/find-dupes/`](apps/find-dupes/) |
| MIME Guess — extension + magic bytes | Python | **shipped** → [`apps/mime-guess/`](apps/mime-guess/) |
| Symlink Report — list/broken symlinks | Python | **shipped** → [`apps/symlink-report/`](apps/symlink-report/) |
| Path Stat — friendly `stat` | Python | **shipped** → [`apps/path-stat/`](apps/path-stat/) |
| Disk Postcard — `df` with ASCII bars | Shell | **shipped** → [`apps/disk-postcard/`](apps/disk-postcard/) |
| Base64 File — encode/decode files | Python | **shipped** → [`apps/base64-file/`](apps/base64-file/) |
| Base64 Party — encode/decode text/files/urlsafe | Python | **shipped** → [`apps/base64-party/`](apps/base64-party/) |
| Hash Salad — multi-algo digests | Python | **shipped** → [`apps/hash-salad/`](apps/hash-salad/) |
| Replace In Files — bulk find/replace + dry-run | Python | **shipped** → [`apps/replace-in-files/`](apps/replace-in-files/) |
| Chmod Explain — octal/rwx → English | Python | **shipped** → [`apps/chmod-explain/`](apps/chmod-explain/) |

---

## Text / data / JSON / CSV

| Idea | Stack | Status |
|------|-------|--------|
| CSV Peek — column stats + sample | Python | **shipped** → [`apps/csv-peek/`](apps/csv-peek/) |
| CSV Select — column pick + `where` | Python | **shipped** → [`apps/csv-select/`](apps/csv-select/) |
| CSV to JSON | Python | **shipped** → [`apps/csv-to-json/`](apps/csv-to-json/) |
| JSON Diff Pretty — structural JSON Δ | Python | **shipped** → [`apps/json-diff-pretty/`](apps/json-diff-pretty/) |
| JSON Pretty CLI — format/compact JSON | Python | **shipped** → [`apps/json-pretty-cli/`](apps/json-pretty-cli/) |
| JSON Path Probe — dotted/`[index]` query | Python | **shipped** → [`apps/json-path-probe/`](apps/json-path-probe/) |
| YAML to JSON (zero-dep subset) | Python | **shipped** → [`apps/yaml-to-json/`](apps/yaml-to-json/) |
| YAML Lint Desk — structural YAML checks | Python | **shipped** → [`apps/yaml-lint-desk/`](apps/yaml-lint-desk/) |
| Diff Canvas — unified/ndiff line diff | Python | **shipped** → [`apps/diff-canvas/`](apps/diff-canvas/) |
| Line Freq — `uniq -c` / top-N | Python | **shipped** → [`apps/line-freq/`](apps/line-freq/) |
| Line Tally — LOC by extension | Python | **shipped** → [`apps/line-tally/`](apps/line-tally/) |
| TOC MD — Markdown table of contents | Python | **shipped** → [`apps/toc-md/`](apps/toc-md/) |
| URL Codec — encode/decode | Python | **shipped** → [`apps/url-codec/`](apps/url-codec/) |
| Slugify Pipe — stdin/args → kebab slugs | Shell | **shipped** → [`apps/slugify-pipe/`](apps/slugify-pipe/) |
| Regex Lab Bench — live regex tester | HTML/JS | **shipped** → [`apps/regex-lab-bench/`](apps/regex-lab-bench/) |
| JWT Peek — decode only (no verify) | HTML/JS | **shipped** → [`apps/jwt-peek/`](apps/jwt-peek/) |
| Markdown Slide — md → HTML deck | Node | **shipped** → [`apps/markdown-slide/`](apps/markdown-slide/) |
| Benford Check — leading-digit law | Python | **shipped** → [`apps/benford-check/`](apps/benford-check/) |
| Lorem Forge — themed fixture text | Node | **shipped** → [`apps/lorem-forge/`](apps/lorem-forge/) |

---

## Network / HTTP / TLS / ports

| Idea | Stack | Status |
|------|-------|--------|
| HTTP Echo Toy — local request echo | Node | **shipped** → [`apps/http-echo-toy/`](apps/http-echo-toy/) |
| HTTP Headers — print response headers | Python | **shipped** → [`apps/http-headers/`](apps/http-headers/) |
| HTTP Headers Peek — status + timing + headers | Python | **shipped** → [`apps/http-headers-peek/`](apps/http-headers-peek/) |
| SSL Expiry — cert notAfter checker | Python | **shipped** → [`apps/ssl-expiry/`](apps/ssl-expiry/) |
| Port Postcard — listening TCP via `ss`/`netstat` | Shell | **shipped** → [`apps/port-postcard/`](apps/port-postcard/) |
| Weather Fetch — Open-Meteo CLI | Shell | **shipped** → [`apps/weather-fetch/`](apps/weather-fetch/) |
| DNS Lookup Plain | Python | planned |

---

## Shell / env / process helpers

| Idea | Stack | Status |
|------|-------|--------|
| Env Diff — compare `.env` (values masked) | Python | **shipped** → [`apps/env-diff/`](apps/env-diff/) |
| Env Redact — dump env with secrets masked | Python | **shipped** → [`apps/env-redact/`](apps/env-redact/) |
| PATH Dedupe — unique PATH entries | Python | **shipped** → [`apps/path-dedupe/`](apps/path-dedupe/) |
| Cron Human — cron → English | Python | **shipped** → [`apps/cron-human/`](apps/cron-human/) |
| Watch Cmd — mini `watch` | Python | **shipped** → [`apps/watch-cmd/`](apps/watch-cmd/) |
| Watch Run — re-run command on file change | Python | **shipped** → [`apps/watch-run/`](apps/watch-run/) |
| Progress Party — pipe progress / spinner | Shell | **shipped** → [`apps/progress-party/`](apps/progress-party/) |
| Timer Bell — countdown + bell | Shell | **shipped** → [`apps/timer-bell/`](apps/timer-bell/) |
| Git Spark — commit sparkline | Python | **shipped** → [`apps/git-spark/`](apps/git-spark/) |

---

## Identity / tokens / consumer crypto-adjacent

| Idea | Stack | Status |
|------|-------|--------|
| Password Garden — memorable passphrases | Python | **shipped** → [`apps/password-garden/`](apps/password-garden/) |
| UUID Mint | Python | **shipped** → [`apps/uuid-mint/`](apps/uuid-mint/) |
| UUID Bar — bulk uuid4 / uuid1 / nanoid | Python | **shipped** → [`apps/uuid-bar/`](apps/uuid-bar/) |
| QR Terminal — short-string QR in terminal | Node | **shipped** → [`apps/qr-terminal/`](apps/qr-terminal/) |
| Name Alchemist — project/host codenames | Python | **shipped** → [`apps/name-alchemist/`](apps/name-alchemist/) |

---

## Time / units

| Idea | Stack | Status |
|------|-------|--------|
| Epoch Convert — epoch ↔ ISO | Python | **shipped** → [`apps/epoch-convert/`](apps/epoch-convert/) |
| Unit Oracle — length/mass/temp | Python | **shipped** → [`apps/unit-oracle/`](apps/unit-oracle/) |
| Pomodoro Orb — focus timer | HTML/JS | **shipped** → [`apps/pomodoro-orb/`](apps/pomodoro-orb/) |

---

## Privacy / defensive consumer helpers

| Idea | Stack | Status |
|------|-------|--------|
| Phish Spotter Quiz | HTML/JS | **shipped** → [`apps/phish-spotter/`](apps/phish-spotter/) |
| Tracker Cookie Explainer | HTML/JS | planned |
| Extension Audit Card | HTML/JS | planned |

---

## Creative tools that still do a job

| Idea | Stack | Status |
|------|-------|--------|
| Color Alchemy — brew/lock/export palettes | HTML/JS | **shipped** → [`apps/color-alchemy/`](apps/color-alchemy/) |
| Gradient Weaver — CSS gradient + copy | HTML/JS | **shipped** → [`apps/gradient-weaver/`](apps/gradient-weaver/) |
| Pixel Paint — 16×16 pixel editor + PNG | HTML/JS | **shipped** → [`apps/pixel-paint/`](apps/pixel-paint/) |
| MIDI Pad — Web Audio drum/synth pad | HTML/JS | **shipped** → [`apps/midi-pad/`](apps/midi-pad/) |
| Spectrum Tuner — tone + spectrum | HTML/JS | **shipped** → [`apps/spectrum-tuner/`](apps/spectrum-tuner/) |

---

## Dropped (decorative / game demos — not utilities)

Removed after utility-first correction: `neon-snake`, `particle-constellation`, `kaleidoscope-lab`, `pendulum-wave`, `ink-blot`, `lorenz-attractor`, `word-waterfall`, `reaction-radar`, `maze-runner`, `typing-furnace`, `fortune-fractal`, `markov-haiku`, plus essay mocks `safe-defaults-card`, `firewall-plain`. Prefer real CLIs over eye-candy.

---

## Wave summary

- **Definition:** useful tools people would run; OS helpers for Ellen Joe / BlackArch spin welcome; no malware/offensive tools
- **Shipped on disk:** **87** apps under [`apps/`](apps/)
- **Wave two (this pass):** **45** new utility / OS-helper apps (checksums, sysctl, firewall preview, PKGBUILD/desktop/unit linters, mirror tools, env/cron/hash/diff/csv/json helpers, etc.)
- **Stacks:** mostly Python CLIs; some Shell, Node, and small HTML tools that perform a real task
- **Factory scratch:** [`internal/app-factory/`](../internal/app-factory/) (`build_wave2_os.py`, `build_wave2_utils.py`, `build_wave2_more.py`)
