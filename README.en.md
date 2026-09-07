<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - MIT License (see LICENSE file) -->
<div align="center">
  <img src="docs/assets/omega-track.png" alt="Omega-Track" width="386">
</div>

# 🛰️ OMEGA-TRACK

**Digital identity profiling and network path observation**

> Developed by **kraynux** for **Omega-server**  
[https://kraynux.snake-mackarel.ts.net](https://kraynux.snake-mackarel.ts.net)

Official page: [OMEGA-TRACK](https://kraynux.snake-mackarel.ts.net/omega-track/) &nbsp; Preview: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-track/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

**Languages:**  
[Français](README.md) · [English](README.en.md) · [Español](README.es.md) · [Русский](README.ru.md) · [中文](README.zh-CN.md)

---

**Omega-track** is a TUI + CLI tool that builds, starting from an IP, IPv6, or domain, the most complete digital identity possible: who is behind this target, how to reach it, and with what confidence level each piece of information can be taken as fact. It is the sixth tool in the `omega-` suite (after `omega-fire`, `omega-stress`, `omega-scan`, `omega-check`, and `omega-deep`/`omega-fold`), structured according to Clean Architecture; see `docs/PRODUCT_SCOPE.md` and `docs/DATA_SOURCES.md` for the complete details.

## 1. Vision and scope

Omega-track answers two questions: "who is this target?" (identity via RDAP/DNS/certificates/reputation) and "how do you reach it?" (network path via NeoTrace, GeoIP, ASN). It complements `omega-check` (network exposure), `omega-scan` (HTTP/HTTPS hygiene), and `omega-deep` (bounded architecture analysis), without duplicating them.

### What Omega-track does

- Accepts an IP, IPv6, or domain target, registered and optionally pinned (durable authorization).
- Centralizes public, passive, or explicitly enabled information (RDAP, DNS, Certificate Transparency, Wayback archives, BGP announcements).
- Runs an enriched, NeoTrace-style traceroute (the only active network action in the core product).
- Enriches every relevant IP through a local GeoIP database (DB-IP Lite with no key, MaxMind GeoLite2 optional with a key).
- Queries, on a key supplied by the user, reputation sources (VirusTotal, HIBP), with systematic disclosure (quota, data sent) before any activation.
- Correlates observed data into a coherent profile, with an explicit confidence level on each piece of data.
- Keeps targets, runs, results, errors, and exports locally (SQLite, `./var/`).
- Provides a Textual TUI and a CLI that are strictly functionally equivalent.
- Produces HTML reports (5 themes, embedded Mermaid relation graph), JSON, Markdown, CSV, and standalone DOT and Mermaid graphs.

### What Omega-track does not do

| Function | Responsible tool |
|---|---|
| Port scanning, service and banner identification | OMEGA-CHECK |
| HTTP/HTTPS checks, headers, TLS, web hygiene | OMEGA-SCAN |
| Crawling, architecture traversal, descent into related targets | OMEGA-DEEP |
| Remote page-by-page crawling (links, files) | OMEGA-FOLD |
| Load testing | OMEGA-STRESS |
| Fuzzing and application robustness testing | OMEGA-FUZZ |

To avoid, even out of MVP scope: subdomain brute-forcing, port scanning, web crawling, intrusive personal-data collection, protection-bypass automation, fragile scraping of platforms requiring authentication, people/social-network/pastebin-leak search, periodic/recurring surveillance of a target (see `docs/PRODUCT_SCOPE.md` §7 "Deliberately deferred").

### Authorized-use warning

Omega-track is a network investigation tool intended for legitimate use: auditing your own infrastructure, incident response, monitoring a scope you are authorized to document. Collection remains almost entirely passive/public (RDAP, DNS, CT logs — data already publicly exposed by the target or its registrar), except for traceroute (active-light, always visible in the profile used).

**No observation starts on a non-pinned target without explicit confirmation** (`--authorize` in the CLI, confirmation in the TUI). You alone are responsible for verifying that your use complies with applicable laws and the terms of use of the third-party sources consulted.

## 2. Installation

### Prerequisites

- Python 3.10+
- Internet connection, for dependencies and passive sources queried
- `traceroute` or `tracepath` installed (NeoTrace module) — degrades gracefully in its absence, the rest of the tool works normally

### Installation

```bash
[ -d omega-track ] && echo "ℹ️ Already extracted here, step skipped." || tar -xzf omega-track.tar.gz
cd omega-track/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. Creates the `.venv` virtual environment if it does not already exist.
2. Installs dependencies (`pip install -e .`, `pyproject.toml` remains the single source of truth).
3. Makes `omega-track.sh` and `install.sh` executable.
4. Adds the `track` alias to `~/.bashrc` and `~/.zshrc` (no duplicate if already present).

### Dependencies

Declared in `pyproject.toml` (no separate `requirements.txt`):
- `omega-lib`: suite-shared library (`ConfidenceLevel`, themes, terminal detection)
- `textual`: TUI interface, themes, automatic terminal adaptation
- `dnspython`: forward and reverse DNS resolution
- `httpx`: RDAP/CT/archives/BGP/VirusTotal/HIBP probes
- `maxminddb`: reading local GeoIP databases (DB-IP Lite, MaxMind GeoLite2)
- `jinja2`: templating for HTML export
- Development dependencies (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-httpserver`, `ruff`, `mypy`, `import-linter`

## 3. Usage

### Interactive mode (TUI)

Recommended for daily use — launched with no argument:

```bash
./omega-track.sh
```
if you created the alias, just type `track` in the terminal:
```bash
track
```

Flow: splash screen (closes on any key or click) → main menu (Targets / Tracker / Results / History / Dashboard / GeoIP / Key sources / Settings / Help) → target entry or selection (explicit confirmation if not pinned) and collection module choice → observation (indeterminate gauge and live network operation log, cancellable) → detailed results by tab (Identity/DNS/Network-ASN/NeoTrace/Certificates/Archives/Relations/Diagnostics, export) → history/dashboard/settings from the main menu. Terminal adaptation (colors, size, structural degradation) is automatic.

#### Keyboard shortcuts

| Key | Action |
|---|---|
| `↑` / `↓` | Navigate between items on a screen |
| `Tab` / `Shift+Tab` | Navigate between fields of a form |
| `Escape` | Back to the previous screen (exit confirmation on the home screen) |
| `t` | Next theme (applied immediately, no confirmation) |
| `r` | Refresh terminal detection |
| `a` | Show help |
| `q` | Quit (with confirmation) |

### Scriptable mode (CLI)

Any subcommand triggers CLI mode:

```bash
# Targets
./omega-track.sh target add example.org --alias "showcase site" --tag prod
./omega-track.sh target list
./omega-track.sh target pin <target_id>

# Launch and follow an observation
./omega-track.sh track run <target_id> --module dns --module rdap --module neotrace --authorize
./omega-track.sh track status <run_id>
./omega-track.sh track show <run_id>
./omega-track.sh track replay <run_id> --authorize

# History
./omega-track.sh history list --target <target_id> --status completed --since 2026-01-01

# Export — 6 formats, 5 HTML themes
./omega-track.sh export <run_id> --format html --theme omega-neon --redact contacts_only

# GeoIP
./omega-track.sh geoip status
./omega-track.sh geoip update --provider dbip

# Key-based reputation sources (disclosure always shown before any key is saved)
./omega-track.sh source list
./omega-track.sh source info virustotal
./omega-track.sh source configure virustotal <api_key>

# Settings and cleanup
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
| `dns` | Active-light (direct resolution) | yes | no |
| `reverse_dns` | Active-light (PTR) | yes | no |
| `rdap` | Passive public | yes | no |
| `neotrace` | Active-light (traceroute/tracepath) | yes | no |
| `certificate_transparency` | Passive public (`crt.sh`) | no | no |
| `archives` | Passive public (Wayback Machine) | no | no |
| `bgp` | Passive public (RIPEstat) | no | no |
| `virustotal` | Key-based | no | yes (free) |
| `hibp` | Key-based | no | yes (**paid** since 2022) |

The first four modules form the MVP core (`dns`/`reverse_dns`/`rdap`/`neotrace`) and are checked by default in the launch form; the following five are optional and must be explicitly enabled. A source with no key configured never fails the observation: the corresponding module simply becomes `SKIPPED`. Per-source detail, quotas, and licenses: `docs/DATA_SOURCES.md`.

## 5. Architecture

Omega-track is structured as **Clean Architecture** (domain / application / infrastructure / interfaces / ports / core / app / plugins), aligned with the `omega-` suite template (see `omega-check`/`omega-fold`) and verified by `import-linter` on every change.

```text
src/omega_track/
├── domain/          Pure business logic (targets, TrackRun/ModuleRun, findings, relations, profiles...)
├── application/     Use cases (commands/queries/phase orchestrators/policies)
├── ports/           Contracts expected by the application (collectors, repositories, exporters...)
├── infrastructure/  Concrete implementations (dnspython/httpx/subprocess/maxminddb, SQLite, jinja2)
├── interfaces/      tui/ (Textual) and cli/ (scriptable), strict functional parity
├── app/             Wiring (DependencyContainer, bootstrap, lifecycle)
├── core/            Cross-cutting vocabulary (versions, omega-lib re-exports)
└── plugins/         Optional single-source modules (CT, archives, BGP, VirusTotal, HIBP)
```

Design rules:
- `domain/` never touches the network or does I/O; `infrastructure/` does the network and I/O, never judges.
- `interfaces/` displays, contains no business logic — CLI and TUI call strictly the same use cases.
- 1 collection module = 1 source = 1 status (`ModuleRun`): never two sources aggregated under one ambiguous status.
- A single missing field is never an error; only total source unavailability triggers `SKIPPED`/`FAILED`.

## 6. Data sources

| Source | Provider | Key | Mode |
|---|---|:---:|---|
| Forward/reverse DNS | System resolver | no | Active-light |
| RDAP | IANA bootstrap → RIR/registrar | no | Passive public |
| Certificate Transparency | `crt.sh` (Sectigo) | no | Passive public |
| Web archives | Wayback Machine (Internet Archive) | no | Passive public |
| BGP / network announcements | RIPEstat (RIPE NCC) | no | Passive public |
| GeoIP | DB-IP Lite (default) or MaxMind GeoLite2 | no / yes | Offline (local database) |
| NeoTrace | Local `traceroute`/`tracepath` | no | Active-light |
| Reputation | VirusTotal | yes (free) | Key-based |
| Reputation | Have I Been Pwned | yes (paid) | Key-based |

Exact quota, license, and fallback for each source: `docs/DATA_SOURCES.md`. No API key ever appears in logs, exports, or diagnostic screens.

## 7. Confidence policy

Every collected field carries one of the following levels (shared across the whole suite via `omega-lib`):

| Level | Meaning |
|---|---|
| `VERIFIED` | Protocol fact observed directly, not falsifiable by the target (e.g. direct DNS response, local traceroute measurement). |
| `DECLARED` | Value self-announced by the source in a field it fully controls (e.g. RDAP data displayed by the registrar) — plausible but freely falsifiable. |
| `CORROBORATED` | A `DECLARED` value confirmed by an independent clue (e.g. a domain observed by at least two distinct Certificate Transparency logs). |
| `INFERRED` | Deduced from a pattern/heuristic, with no explicit declaration (e.g. a shared ASN used to suggest a relation, never auto-promoted). |
| `UNKNOWN` | No usable clue, or actively hidden by the target. |

An observation's overall confidence score is a reading aid, never a security verdict.

## 8. Collection levels, authorization, and redaction

Every profile makes the nature of its actions explicit (`CollectionMode`):

- **Offline**: target validation, local GeoIP lookup, correlation on already-stored data, exports — no network.
- **Passive public**: RDAP, public DNS, CT logs, archives, BGP — only the queried target is transmitted to the third party, inherent to the protocol.
- **Active-light**: DNS resolution, reverse DNS, traceroute — the configured resolver and every intermediate router on the path see the request.
- **Key-based**: providers requiring a key or enforcing quotas, enabled only after explicit configuration and displayed disclosure (quota, data sent).

**Authorization gate**: no observation starts on a non-pinned target without explicit confirmation (`--authorize` in the CLI, checkbox in the TUI). Pinning a target authorizes it durably for its future observations.

**Export redaction**: every export accepts a policy (`none`/`contacts_only`/`sensitive_only`/`strict`) that masks sensitive fields (RDAP contacts in particular) in the exported output — local storage always keeps the full collected data. Details: `docs/PRIVACY.md`.

## 9. Terminal compatibility

The TUI (Textual) automatically detects terminal capabilities (emulator, size) and adapts its structural stylesheet accordingly (`complete`/`standard`/`reduced`/`mono`), with no manual flag. CLI mode always stays plain text, independent of the terminal. Policy shared across the whole `omega-` suite (`omega-lib`, `terminal/policies.py`).

### Profile by detected emulator

| Emulator | Initial profile |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, modern SSH | `reduced` |
| Linux TTY, legacy SSH | `mono` |
| Unrecognized emulator | `reduced` (default fallback) |

### Profile by terminal size

| Minimum size (columns × rows) | Profile ceiling |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| below | `mono` |

The final profile chosen is **the more restrictive of the two** (emulator and size). Refreshable live with the `r` key.

## 10. Exports

Reports are generated in `var/exports/` by default (runtime path anchored to the project directory, `$OMEGA_TRACK_VAR_DIR` to override it), or at the given path (`--output` in the CLI, dialog in the TUI). Timestamped, unique file name: `{timestamp}_{target}_{short_id}.{extension}`.

| Format | Content |
|---|---|
| `json` | Complete observation structure (`TrackRun` + findings + relations), source of truth, strictly JSON-serializable |
| `markdown` | Compact human-readable report, readable outside the terminal |
| `html` | Standalone web report, 5 selectable themes (`--theme`), Mermaid relation graph embedded inline |
| `csv` | One table per finding category |
| `dot` | Graphviz relation graph, standalone file |
| `mermaid` | Mermaid relation graph, standalone file |

## 11. History, cleanup, and replay

Every observation is persisted (SQLite, `var/db/omega-track.db`): browsable and filterable history (target/status/tag/period), summary dashboard (breakdown by status, per-module reliability, typology of the most recent findings), replay of an observation against the same target without re-entering data (`track replay`), and cleanup of old history with a systematic preview before any deletion (`cleanup preview` before `cleanup run --yes`).

## 12. Tests

```bash
source .venv/bin/activate
lint-imports        # checks the Dependency Rule
pytest -q           # 478 tests
ruff check .
mypy src
```

Structure: `tests/unit/` (domain and application, no real I/O), `tests/integration/` (real SQLite/files, fake HTTP server `pytest-httpserver`, headless TUI via Textual's `Pilot` API).

## 13. Out of scope

- Full WHOIS/DNS history, commercial passive DNS
- People search, social networks, pastebins/leaks
- Port scanning, service and banner identification (`omega-check`)
- HTTP/HTTPS checks, headers, TLS (`omega-scan`)
- Architecture crawling and traversal (`omega-deep`/`omega-fold`)
- Load testing (`omega-stress`), fuzzing (`omega-fuzz`)
- Interactive TUI map (reserved for the exported HTML report)
- Continuous, multi-probe, multi-vantage-point MTR
- Batch/periodic/recurring surveillance mode for a target — a `TrackRun` always remains an explicit manual action
- SQLite schema migration engine before v1.0 (additive schema, same practice as the rest of the suite)

---

> Omega-track — Observe, correlate, qualify, report.
> A digital identity with explicit confidence on every piece of data, never a certainty in disguise.
