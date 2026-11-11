<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - MIT License (see LICENSE file) -->
<div align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/assets/omega-track.png" alt="Omega-Track" width="512">
</div>

# 🛰️ OMEGA-TRACK

**Digital identity profiling and network path observation**

> Built by [kraynux](https://github.com/kraynux) for [Omega-Server](https://kraynux.snake-mackarel.ts.net)   

Official page: [OMEGA-TRACK](https://kraynux.snake-mackarel.ts.net/omega-track/) &nbsp; Preview: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-track/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 Interface and exported reports available in **17 languages** — see [Interface languages](#interface-languages).  
**Languages:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

---

**Omega-track** is a TUI + CLI tool that builds, from an IP, an IPv6 address or a domain, the most complete digital identity possible: who answers behind this target, how traffic gets there, and how much confidence each piece of information deserves. It is a tool of the `omega-` suite, built on Clean Architecture — see `docs/PRODUCT_SCOPE.md` and `docs/DATA_SOURCES.md` for the full details.

<p align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/en/omega-track/A.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/en/omega-track/B.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/en/omega-track/C.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/en/omega-track/D.png" width="24%" />
</p>

## 1. Vision and scope

Omega-track answers two questions: "who is this target?" (RDAP/DNS/certificate/reputation identity) and "how do we get there?" (NeoTrace network path, GeoIP, ASN). It complements `omega-check` (network exposure), `omega-scan` (HTTP/HTTPS hygiene) and `omega-deep` (bounded architecture analysis), without duplicating them.

### What Omega-track does

- Accepts an IP, IPv6 or domain name target, saved and optionally pinned (lasting authorization).
- Gathers public information, passive or explicitly enabled by the profile (RDAP, DNS, Certificate Transparency, Wayback archives, BGP announcements).
- Runs an enriched NeoTrace-style traceroute (the only active network action at the core of the product).
- Enriches each relevant IP with a local GeoIP database (keyless DB-IP Lite, optional MaxMind GeoLite2 with a key).
- Queries reputation sources (VirusTotal, HIBP) with a key supplied by the user, always disclosing quota and data sent before any activation.
- Correlates the observed data into a consistent profile, with an explicit confidence level on every piece of data.
- Keeps targets, runs, results, errors and exports locally (SQLite, `./var/`).
- Provides a Textual TUI and a CLI that are strictly equivalent in features.
- Produces HTML reports (5 themes, embedded Mermaid relationship graph), JSON, Markdown, CSV, and standalone DOT and Mermaid files.

### What Omega-track does not do

| Feature | Responsible tool |
|---|---|
| Port scanning, service and banner identification | OMEGA-CHECK |
| HTTP/HTTPS checks, headers, TLS, web hygiene | OMEGA-SCAN |
| Crawling, architecture traversal and descent into linked targets | OMEGA-DEEP |
| Remote page-by-page crawling (links, files) | OMEGA-FOLD |
| Load testing | OMEGA-STRESS |
| Fuzzing and application robustness testing | OMEGA-FUZZ |

To be avoided, including beyond the MVP: subdomain brute-forcing, port scanning, web crawling, intrusive collection of personal data, automated bypassing of protections, fragile scraping of platforms that require authentication, people/social network/pastebin-leak searches, periodic/recurring monitoring of a target (see `docs/PRODUCT_SCOPE.md` §7 "Deliberately deferred").

### Authorized use notice

Omega-track is a network investigation tool meant for legitimate use: auditing your own infrastructure, incident response, keeping watch over a scope you are authorized to document. Collection stays almost entirely passive/public (RDAP, DNS, CT logs — data the target or its registrar already exposes publicly), except for the traceroute (light active, always visible in the profile used).

**No observation starts on an unpinned target without explicit confirmation** (`--authorize` in the CLI, confirmation in the TUI). You alone are responsible for checking that your use complies with applicable law and with the terms of use of the third-party sources queried.

## 2. Installation

### Prerequisites

- Python 3.10+
- Internet connection, for the dependencies and the passive sources queried
- `traceroute` or `tracepath` installed (NeoTrace module) — degrades cleanly when missing, the rest of the tool works normally

### Installation

```bash
[ -d omega-track ] && echo "ℹ️ Already extracted here, step skipped." || tar -xzf omega-track.tar.gz
cd omega-track/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. Creates the `.venv` virtual environment if it does not exist yet.
2. Installs the dependencies (`pip install -e .`, `pyproject.toml` remains the single source of truth).
3. Makes `omega-track.sh` and `install.sh` executable.
4. Adds the `track` alias to `~/.bashrc` and `~/.zshrc` (no duplicate if already present).

### Dependencies

Declared in `pyproject.toml` (no separate `requirements.txt`):
- `omega-lib`: the suite's shared library (`ConfidenceLevel`, themes, terminal detection)
- `textual`: TUI, themes, automatic terminal adaptation
- `dnspython`: forward and reverse DNS resolution
- `httpx`: RDAP/CT/archives/BGP/VirusTotal/HIBP probes
- `maxminddb`: reading local GeoIP databases (DB-IP Lite, MaxMind GeoLite2)
- `jinja2`: templating for the HTML export
- Development dependencies (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-httpserver`, `ruff`, `mypy`, `import-linter`

## 3. Usage

### Interactive mode (TUI)

Recommended for everyday use — launched without arguments:

```bash
./omega-track.sh
```
if you created the alias, just type `track` in the terminal:
```bash
track
```

Flow: splash screen (closes on a key press or a click) → main menu (Targets / Tracker / Results / History / Dashboard / GeoIP / Key-based sources / Settings / Help) → entering or selecting the target (explicit confirmation if not pinned) and choosing the collection modules → observation (gauge and live sequence of operations, cancellable) → detailed results by tab (Identity/DNS/Network / ASN/NeoTrace/Certificates/Archives/Relations/Diagnostics, export) → history/dashboard/settings from the main menu. Terminal adaptation (colors, size, structural degradation) is automatic.

#### Keyboard shortcuts

| Key | Action |
|---|---|
| `↑` / `↓` | Move between the items of a screen |
| `Tab` / `Shift+Tab` | Move between the fields of a form |
| `Esc` | Back to the previous screen (exit confirmation on the home screen) |
| `t` | Next theme (applied immediately, no confirmation) |
| `r` | Refresh terminal detection |
| `a` | Show help |
| `q` | Quit (with confirmation) |

### Interface languages

The interface is available in 17 languages: French, English, Spanish, Portuguese (Brazil), Italian, German, Dutch, Polish, Russian, Simplified Chinese, Vietnamese, Thai, Indonesian, Japanese, Korean, Hindi and Arabic. The choice is made in Settings ("Langue / Language") and applies after the interface restarts; the `OMEGA_TRACK_LANG` variable (for example `OMEGA_TRACK_LANG=en ./omega-track.sh`) forces a language for one session. When launched from omega-suite, omega-track uses the suite's language. On a Linux text console (TTY), languages written in non-Latin scripts are shown in English for that session. The command line stays in French.

### Contact and support

Help (`a` key) offers a **Contact and support** screen: *Buy me a coffee* (the developer's PayPal page), *Contact support* (email address and the site's contact form, shown in plain text), *Declare myself as a user (anonymous)* and *Check for updates*. The declaration is voluntary, off by default and sent only once: it is used only to count users and, if you wish, their continent or country (closed lists, never free text). It sends a randomly drawn key, the software name (`omega-track`) and its version; never a name, a machine name, a setting, a target or a result. The IP address is not stored in the declarations, but, like any visit, it goes through the security checks and the log of the receiving server. You can withdraw at any time from the same screen (*Stop declaring me*). The update check only reads the list of versions published on the site, and never without a click.

### Scriptable mode (CLI)

Any subcommand triggers CLI mode:

```bash
# Targets
./omega-track.sh target add example.org --alias "showcase site" --tag prod
./omega-track.sh target list
./omega-track.sh target pin <target_id>

# Start and follow an observation
./omega-track.sh track run <target_id> --module dns --module rdap --module neotrace --authorize
./omega-track.sh track status <run_id>
./omega-track.sh track show <run_id>
./omega-track.sh track replay <run_id> --authorize

# History
./omega-track.sh history list --target <target_id> --status completed --since 2026-01-01

# Export — 6 formats, 5 themes for HTML
./omega-track.sh export <run_id> --format html --theme omega-neon --redact contacts_only

# GeoIP
./omega-track.sh geoip status
./omega-track.sh geoip update --provider dbip

# Key-based reputation sources (disclosure shown before anything is saved)
./omega-track.sh source list
./omega-track.sh source info virustotal
./omega-track.sh source configure virustotal <api_key>

# Settings and purge
./omega-track.sh config show
./omega-track.sh cleanup preview --older-than 30
./omega-track.sh cleanup run --older-than 30 --yes

# Local diagnostics (versions, capabilities, paths, GeoIP status)
./omega-track.sh diagnostics
```

Every subcommand accepts `--json` for strictly machine-readable output.

#### Exit codes

| Code | Meaning |
|---:|---|
| `0` | Success (observation finished, `COMPLETED`) |
| `1` | Validation error (invalid target, unknown export format, invalid state transition, missing API key...) |
| `2` | Target not authorized (neither pinned nor `--authorize`) |
| `3` | Resource not found or source unavailable (unknown target/run, GeoIP download failure) |
| `4` | Partial observation (`PARTIAL`) — not a failure, only some modules succeeded |
| `5` | Unexpected internal error |
| `130` | Interrupted by the user (`Ctrl+C`) |

### Accepted target formats

```text
192.168.1.10                IPv4
2001:db8::1                 IPv6
example.org                 Domain
```

## 4. Collection modules

| Module | Collection mode | Enabled by default | Key required |
|---|---|:---:|:---:|
| `dns` | Light active (forward resolution) | yes | no |
| `reverse_dns` | Light active (PTR) | yes | no |
| `rdap` | Public passive | yes | no |
| `neotrace` | Light active (traceroute/tracepath) | yes | no |
| `certificate_transparency` | Public passive (`crt.sh`) | no | no |
| `archives` | Public passive (Wayback Machine) | no | no |
| `bgp` | Public passive (RIPEstat) | no | no |
| `virustotal` | With user key | no | yes (free) |
| `hibp` | With user key | no | yes (**paid** since 2022) |

The first four modules form the MVP base (`dns`/`reverse_dns`/`rdap`/`neotrace`) and are ticked by default in the launch form; the next five are optional and must be enabled explicitly. A source with no configured key never fails the observation: the matching module simply goes `SKIPPED` ("not run"). Details per source, quotas and licenses: `docs/DATA_SOURCES.md`.

## 5. Architecture

Omega-track is built on **Clean Architecture** (domain / application / infrastructure / interfaces / ports / core / app / plugins), aligned with the `omega-` suite template (see `omega-check`/`omega-fold`) and checked by `import-linter` on every change.

```text
src/omega_track/
├── domain/          Pure business logic (targets, TrackRun/ModuleRun, findings, relations, profiles...)
├── application/     Use cases (commands/queries/phase orchestrators/policies)
├── ports/           Contracts expected by the application (collectors, repositories, exporters...)
├── infrastructure/  Concrete implementations (dnspython/httpx/subprocess/maxminddb, SQLite, jinja2)
├── interfaces/      tui/ (Textual) and cli/ (scriptable), with strict feature parity
├── app/             Wiring (DependencyContainer, bootstrap, lifecycle)
├── core/            Cross-cutting vocabulary (versions, omega-lib re-exports)
└── plugins/         Optional single-source modules (CT, archives, BGP, VirusTotal, HIBP)
```

Design rules:
- `domain/` never does networking or I/O; `infrastructure/` does networking and I/O, and never judges.
- `interfaces/` displays and contains no business logic — the CLI and TUI call strictly the same use cases.
- 1 collection module = 1 source = 1 status (`ModuleRun`): never two sources aggregated under a single ambiguous status.
- A single missing field is never an error; only the total unavailability of a source triggers `SKIPPED`/`FAILED`.

## 6. Data sources

| Source | Provider | Key | Mode |
|---|---|:---:|---|
| Forward/reverse DNS | System resolver | no | Light active |
| RDAP | IANA bootstrap → RIR/registrar | no | Public passive |
| Certificate Transparency | `crt.sh` (Sectigo) | no | Public passive |
| Web archives | Wayback Machine (Internet Archive) | no | Public passive |
| BGP / network announcements | RIPEstat (RIPE NCC) | no | Public passive |
| GeoIP | DB-IP Lite (default) or MaxMind GeoLite2 | no / yes | Offline (local database) |
| NeoTrace | Local `traceroute`/`tracepath` | no | Light active |
| Reputation | VirusTotal | yes (free) | With key |
| Reputation | Have I Been Pwned | yes (paid) | With key |

Exact quota, license and fallback for each source: `docs/DATA_SOURCES.md`. No API key ever appears in logs, exports or diagnostic screens.

## 7. Confidence policy

Each collected field carries one level among the following (shared with the whole suite through `omega-lib`):

| Level | Meaning |
|---|---|
| `VERIFIED` | Protocol fact observed directly, which the target cannot forge (e.g. a direct DNS answer, a local traceroute measurement). |
| `DECLARED` | Value self-reported by the source in a field it fully controls (e.g. RDAP data shown by the registrar) — plausible but forgeable at will. |
| `CORROBORATED` | A `DECLARED` value confirmed by an independent clue (e.g. a domain seen in at least two distinct Certificate Transparency logs). |
| `INFERRED` | Deduced from a pattern/heuristic, with no explicit declaration (e.g. a shared ASN used to suggest a relationship, never promoted automatically). |
| `UNKNOWN` | No usable clue, or actively hidden by the target. |

The overall confidence score of an observation is a reading aid, never a security verdict.

## 8. Collection levels, authorization and redaction

Each profile makes the nature of its actions explicit (`CollectionMode`):

- **Offline**: target validation, local GeoIP lookup, correlations on already stored data, exports — no networking.
- **Public passive**: RDAP, public DNS, CT logs, archives, BGP — only the queried target is sent to the third party, an inherent property of the protocol.
- **Light active**: DNS resolution, reverse DNS, traceroute — the resolver configured on the machine and every intermediate router on the path see the request.
- **With user key**: providers that require a key or enforce quotas, enabled only after explicit configuration and a displayed disclosure (quota, data sent).

**Authorization guard**: no observation starts on an unpinned target without explicit confirmation (`--authorize` in the CLI, checkbox in the TUI). Pinning a target authorizes it permanently for its future observations.

**Export redaction**: each export accepts a policy (`none`/`contacts_only`/`sensitive_only`/`strict`) that masks sensitive fields (RDAP contacts in particular) in the exported output — local storage always keeps the full collected data. Details: `docs/PRIVACY.md`.

## 9. Terminal compatibility

The TUI (Textual) automatically detects the terminal's capabilities (emulator, size) and adapts its structural stylesheet accordingly (`complete`/`standard`/`reduced`/`mono`), with no manual flag. CLI mode always stays plain text, independent of the terminal. This policy is shared by the whole `omega-` suite (`omega-lib`, `terminal/policies.py`).

### Profile by detected emulator

| Emulator | Initial profile |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, modern SSH | `reduced` |
| Linux TTY, legacy SSH | `mono` |
| Unrecognized emulator | `reduced` (default fallback) |

### Profile by terminal size

| Minimum size (columns × lines) | Profile ceiling |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| below | `mono` |

The final profile is **the more restrictive of the two** (emulator and size). It can be refreshed live with the `r` key.

## 10. Exports

Markdown and HTML reports are written in the language chosen in Settings ("Export language", by default the interface language); JSON, CSV, DOT and Mermaid remain data and are not translated. Reports are generated in `var/exports/` by default (runtime path anchored to the project folder, `$OMEGA_TRACK_VAR_DIR` to override it), or at the given path (`--output` in the CLI, dialog box in the TUI). Timestamped, unique file name: `{timestamp}_{target}_{short_id}.{extension}`.

| Format | Content |
|---|---|
| `json` | Full structure of the observation (`TrackRun` + findings + relations), source of truth, strictly JSON-serializable |
| `markdown` | Compact human-readable report, readable outside the terminal |
| `html` | Standalone web report, 5 themes to choose from (`--theme`), Mermaid relationship graph embedded inline |
| `csv` | One table per finding category |
| `dot` | Graphviz relationship graph, standalone file |
| `mermaid` | Mermaid relationship graph, standalone file |

## 11. History, purge and replay

Each observation is persisted (SQLite, `var/db/omega-track.db`): a history you can browse and filter (target/status/tag/period), a summary dashboard (breakdown by status, reliability per module, types of the latest findings), replay of an observation on the same target without re-entering it (`track replay`), and purge of old history with a systematic preview before any deletion (`cleanup preview` before `cleanup run --yes`).

## 12. Tests

```bash
source .venv/bin/activate
lint-imports        # checks the Dependency Rule
pytest -q           # 485 tests
ruff check .
mypy src
```

Layout: `tests/unit/` (domain and application, no real I/O), `tests/integration/` (real SQLite/files, fake HTTP server `pytest-httpserver`, headless TUI through Textual's `Pilot` API).

## 13. Out of scope

- Full WHOIS/DNS history, commercial passive DNS
- People, social network, pastebin/leak searches
- Port scanning, service and banner identification (`omega-check`)
- HTTP/HTTPS checks, headers, TLS (`omega-scan`)
- Crawling and architecture traversal (`omega-deep`/`omega-fold`)
- Load testing (`omega-stress`), fuzzing (`omega-fuzz`)
- Interactive TUI map (reserved for the exported HTML report)
- Continuous, multi-probe and multi-vantage-point MTR
- Batch/periodic mode or recurring monitoring of a target — a `TrackRun` always remains an explicit manual action
- SQLite schema migration engine (additive schema, same practice as the rest of the suite)

---

> Omega-track — Observe, correlate, qualify, report.
> A digital identity with explicit confidence on every piece of data, never a disguised certainty.
