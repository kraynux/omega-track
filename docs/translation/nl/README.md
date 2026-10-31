<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - MIT-licentie (zie bestand LICENSE) -->
<div align="center">
  <img src="../../assets/omega-track.png" alt="Omega-Track" width="386">
</div>

# 🛰️ OMEGA-TRACK

**Profilering van digitale identiteit en observatie van netwerkpaden**

> Ontwikkeld door [kraynux](https://github.com/kraynux) voor [Omega-Server](https://kraynux.snake-mackarel.ts.net)   

Officiële pagina: [OMEGA-TRACK](https://kraynux.snake-mackarel.ts.net/omega-track/) &nbsp; Voorbeeld: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-track/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 Interface en geëxporteerde rapporten beschikbaar in **17 talen** — zie [Talen van de interface](#talen-van-de-interface).  
**Talen:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

---

**Omega-track** is een TUI- + CLI-tool die op basis van een IP, een IPv6-adres of een domein de meest volledige digitale identiteit opbouwt: wie er achter dit doel antwoordt, hoe je er komt en met welk vertrouwensniveau elk gegeven als vaststaand mag gelden. Het is een tool van de `omega-`-suite, opgebouwd volgens Clean Architecture — zie `docs/PRODUCT_SCOPE.md` en `docs/DATA_SOURCES.md` voor alle details.

## 1. Visie en reikwijdte

Omega-track beantwoordt twee vragen: "wie is dit doel?" (identiteit via RDAP/DNS/certificaten/reputatie) en "hoe kom je er?" (netwerkpad NeoTrace, GeoIP, ASN). Het vult `omega-check` (netwerkblootstelling), `omega-scan` (HTTP/HTTPS-hygiëne) en `omega-deep` (begrensde architectuuranalyse) aan, zonder ze te dupliceren.

### Wat Omega-track doet

- Accepteert een doel als IP, IPv6 of domeinnaam, opgeslagen en eventueel vastgezet (blijvende autorisatie).
- Verzamelt openbare informatie, passief of expliciet ingeschakeld door het profiel (RDAP, DNS, Certificate Transparency, Wayback-archieven, BGP-aankondigingen).
- Voert een verrijkte traceroute in NeoTrace-stijl uit (de enige actieve netwerkactie in de kern van het product).
- Verrijkt elk relevant IP via een lokale GeoIP-database (DB-IP Lite zonder sleutel, MaxMind GeoLite2 optioneel met sleutel).
- Raadpleegt met een door de gebruiker verstrekte sleutel reputatiebronnen (VirusTotal, HIBP), met systematische openbaarmaking (quotum, verzonden gegevens) vóór elke activering.
- Brengt de waargenomen gegevens met elkaar in verband tot een samenhangend profiel, met een expliciet vertrouwensniveau voor elk gegeven.
- Bewaart doelen, uitvoeringen, resultaten, fouten en exports lokaal (SQLite, `./var/`).
- Biedt een Textual-TUI en een CLI die functioneel strikt gelijkwaardig zijn.
- Maakt HTML-rapporten (5 thema's, ingebedde Mermaid-relatiegraaf), JSON, Markdown, CSV, en zelfstandige DOT- en Mermaid-bestanden.

### Wat Omega-track niet doet

| Functie | Verantwoordelijke tool |
|---|---|
| Poortscan, herkenning van diensten en banners | OMEGA-CHECK |
| HTTP/HTTPS-controles, headers, TLS, webhygiëne | OMEGA-SCAN |
| Crawl, doorlopen van architectuur en afdalen naar gekoppelde doelen | OMEGA-DEEP |
| Externe crawl pagina per pagina (links, bestanden) | OMEGA-FOLD |
| Belastingtests | OMEGA-STRESS |
| Fuzzing en robuustheidstests van applicaties | OMEGA-FUZZ |

Te vermijden, ook buiten de MVP: brute-force van subdomeinen, poortscan, webcrawl, ingrijpende verzameling van persoonsgegevens, geautomatiseerd omzeilen van beveiligingen, fragiele scraping van platforms die authenticatie vereisen, zoeken naar personen/sociale netwerken/pastebins-lekken, periodieke/terugkerende bewaking van een doel (zie `docs/PRODUCT_SCOPE.md` §7 "Bewust uitgesteld").

### Waarschuwing voor geautoriseerd gebruik

Omega-track is een tool voor netwerkonderzoek bedoeld voor legitiem gebruik: audit van je eigen infrastructuur, incidentrespons, bewaking van een perimeter die je mag documenteren. De verzameling blijft bijna volledig passief/openbaar (RDAP, DNS, CT-logs — gegevens die het doel of zijn registrar al openbaar maakt), met uitzondering van de traceroute (licht actief, altijd zichtbaar in het gebruikte profiel).

**Geen enkele observatie start op een niet-vastgezet doel zonder expliciete bevestiging** (`--authorize` in de CLI, bevestiging in de TUI). Je bent als enige verantwoordelijk voor de controle dat je gebruik voldoet aan de toepasselijke wetgeving en aan de gebruiksvoorwaarden van de geraadpleegde externe bronnen.

## 2. Installatie

### Vereisten

- Python 3.10+
- Internetverbinding, voor de afhankelijkheden en de geraadpleegde passieve bronnen
- `traceroute` of `tracepath` geïnstalleerd (module NeoTrace) — ontbreekt het, dan wordt netjes teruggeschakeld en werkt de rest van de tool normaal

### Installatie

```bash
[ -d omega-track ] && echo "ℹ️ Hier al uitgepakt, stap overgeslagen." || tar -xzf omega-track.tar.gz
cd omega-track/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. Maakt de virtuele omgeving `.venv` aan als die nog niet bestaat.
2. Installeert de afhankelijkheden (`pip install -e .`, `pyproject.toml` blijft de enige bron van waarheid).
3. Maakt `omega-track.sh` en `install.sh` uitvoerbaar.
4. Voegt de alias `track` toe aan `~/.bashrc` en `~/.zshrc` (zonder duplicaat als die al bestaat).

### Afhankelijkheden

Gedeclareerd in `pyproject.toml` (geen aparte `requirements.txt`):
- `omega-lib`: gedeelde bibliotheek van de suite (`ConfidenceLevel`, thema's, terminaldetectie)
- `textual`: TUI-interface, thema's, automatische aanpassing aan de terminal
- `dnspython`: directe en omgekeerde DNS-resolutie
- `httpx`: probes voor RDAP/CT/archieven/BGP/VirusTotal/HIBP
- `maxminddb`: lezen van de lokale GeoIP-databases (DB-IP Lite, MaxMind GeoLite2)
- `jinja2`: templating voor de HTML-export
- Ontwikkelafhankelijkheden (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-httpserver`, `ruff`, `mypy`, `import-linter`

## 3. Gebruik

### Interactieve modus (TUI)

Aanbevolen voor dagelijks gebruik — gestart zonder argument:

```bash
./omega-track.sh
```
als je de alias hebt aangemaakt, typ dan gewoon `track` in de terminal:
```bash
track
```

Verloop: startscherm (sluit bij een toets of klik) → hoofdmenu (Doelen / Tracker / Resultaten / Geschiedenis / Dashboard / GeoIP / Bronnen met sleutel / Instellingen / Help) → invoer of selectie van het doel (expliciete bevestiging als het niet is vastgezet) en keuze van de verzamelmodules → observatie (meter en verloop van de bewerkingen live, annuleerbaar) → gedetailleerde resultaten per tabblad (Identiteit/DNS/Netwerk / ASN/NeoTrace/Certificaten/Archieven/Relaties/Diagnostiek, export) → geschiedenis/dashboard/instellingen vanuit het hoofdmenu. De aanpassing aan de terminal (kleuren, grootte, structurele terugschakeling) gebeurt automatisch.

#### Sneltoetsen

| Toets | Actie |
|---|---|
| `↑` / `↓` | Navigeren tussen de elementen van een scherm |
| `Tab` / `Shift+Tab` | Navigeren tussen de velden van een formulier |
| `Esc` | Terug naar het vorige scherm (bevestiging van afsluiten op het startscherm) |
| `t` | Volgend thema (meteen toegepast, zonder bevestiging) |
| `r` | Terminaldetectie vernieuwen |
| `a` | Help tonen |
| `q` | Afsluiten (met bevestiging) |

### Talen van de interface

De interface is beschikbaar in 17 talen: Frans, Engels, Spaans, Portugees (Brazilië), Italiaans, Duits, Nederlands, Pools, Russisch, vereenvoudigd Chinees, Vietnamees, Thai, Indonesisch, Japans, Koreaans, Hindi en Arabisch. De keuze wordt gemaakt in de Instellingen ("Langue / Language") en geldt na een herstart van de interface; de variabele `OMEGA_TRACK_LANG` (bijvoorbeeld `OMEGA_TRACK_LANG=nl ./omega-track.sh`) dwingt een taal af voor één sessie. Gestart vanuit omega-suite neemt omega-track de taal van de suite over. Op een Linux-tekstconsole (TTY) worden talen met een niet-Latijns schrift voor de duur van de sessie in het Engels getoond. De opdrachtregel blijft in het Frans.

### Scriptbare modus (CLI)

Elke subopdracht activeert de CLI-modus:

```bash
# Doelen
./omega-track.sh target add example.org --alias "etalagesite" --tag prod
./omega-track.sh target list
./omega-track.sh target pin <target_id>

# Een observatie starten en volgen
./omega-track.sh track run <target_id> --module dns --module rdap --module neotrace --authorize
./omega-track.sh track status <run_id>
./omega-track.sh track show <run_id>
./omega-track.sh track replay <run_id> --authorize

# Geschiedenis
./omega-track.sh history list --target <target_id> --status completed --since 2026-01-01

# Export — 6 formaten, 5 thema's voor HTML
./omega-track.sh export <run_id> --format html --theme omega-neon --redact contacts_only

# GeoIP
./omega-track.sh geoip status
./omega-track.sh geoip update --provider dbip

# Reputatiebronnen met sleutel (openbaarmaking getoond vóór elke opslag)
./omega-track.sh source list
./omega-track.sh source info virustotal
./omega-track.sh source configure virustotal <api_sleutel>

# Instellingen en opschonen
./omega-track.sh config show
./omega-track.sh cleanup preview --older-than 30
./omega-track.sh cleanup run --older-than 30 --yes

# Lokale diagnostiek (versies, mogelijkheden, paden, GeoIP-status)
./omega-track.sh diagnostics
```

Elke subopdracht accepteert `--json` voor strikt machineleesbare uitvoer.

#### Afsluitcodes

| Code | Betekenis |
|---:|---|
| `0` | Succes (observatie voltooid, `COMPLETED`) |
| `1` | Validatiefout (ongeldig doel, onbekend exportformaat, ongeldige statusovergang, ontbrekende API-sleutel...) |
| `2` | Doel niet geautoriseerd (niet vastgezet en geen `--authorize`) |
| `3` | Bron niet gevonden of niet beschikbaar (onbekend doel/onbekende uitvoering, mislukte GeoIP-download) |
| `4` | Gedeeltelijke observatie (`PARTIAL`) — geen mislukking, slechts enkele modules zijn geslaagd |
| `5` | Onverwachte interne fout |
| `130` | Onderbroken door de gebruiker (`Ctrl+C`) |

### Geaccepteerde doelformaten

```text
192.168.1.10                IPv4
2001:db8::1                 IPv6
example.org                 Domein
```

## 4. Verzamelmodules

| Module | Verzamelmodus | Standaard actief | Sleutel vereist |
|---|---|:---:|:---:|
| `dns` | Licht actief (directe resolutie) | ja | nee |
| `reverse_dns` | Licht actief (PTR) | ja | nee |
| `rdap` | Openbaar passief | ja | nee |
| `neotrace` | Licht actief (traceroute/tracepath) | ja | nee |
| `certificate_transparency` | Openbaar passief (`crt.sh`) | nee | nee |
| `archives` | Openbaar passief (Wayback Machine) | nee | nee |
| `bgp` | Openbaar passief (RIPEstat) | nee | nee |
| `virustotal` | Met gebruikerssleutel | nee | ja (gratis) |
| `hibp` | Met gebruikerssleutel | nee | ja (**betaald** sinds 2022) |

De eerste vier modules vormen de MVP-basis (`dns`/`reverse_dns`/`rdap`/`neotrace`) en zijn standaard aangevinkt in het startformulier; de vijf volgende zijn optioneel en moeten expliciet worden ingeschakeld. Een bron zonder geconfigureerde sleutel laat de observatie nooit mislukken: de bijbehorende module gaat gewoon naar `SKIPPED` ("niet uitgevoerd"). Details per bron, quota en licenties: `docs/DATA_SOURCES.md`.

## 5. Architectuur

Omega-track is opgebouwd volgens **Clean Architecture** (domain / application / infrastructure / interfaces / ports / core / app / plugins), afgestemd op het sjabloon van de `omega-`-suite (zie `omega-check`/`omega-fold`) en bij elke wijziging gecontroleerd door `import-linter`.

```text
src/omega_track/
├── domain/          Pure bedrijfslogica (doelen, TrackRun/ModuleRun, findings, relaties, profielen...)
├── application/     Use cases (commands/queries/fase-orchestrators/beleid)
├── ports/           Contracten die de applicatie verwacht (verzamelaars, repositories, exporters...)
├── infrastructure/  Concrete implementaties (dnspython/httpx/subprocess/maxminddb, SQLite, jinja2)
├── interfaces/      tui/ (Textual) en cli/ (scriptbaar), met strikte functionele pariteit
├── app/             Samenstelling (DependencyContainer, bootstrap, levenscyclus)
├── core/            Overkoepelende woordenschat (versies, her-exports uit omega-lib)
└── plugins/         Optionele modules met één bron (CT, archieven, BGP, VirusTotal, HIBP)
```

Ontwerpregels:
- `domain/` doet nooit netwerk of I/O; `infrastructure/` doet netwerk en I/O, en oordeelt nooit.
- `interfaces/` toont en bevat geen bedrijfslogica — CLI en TUI roepen strikt dezelfde use cases aan.
- 1 verzamelmodule = 1 bron = 1 status (`ModuleRun`): nooit twee bronnen samengevoegd onder één dubbelzinnige status.
- Het ontbreken van één afzonderlijk veld is nooit een fout; alleen de volledige onbeschikbaarheid van een bron leidt tot `SKIPPED`/`FAILED`.

## 6. Gegevensbronnen

| Bron | Leverancier | Sleutel | Modus |
|---|---|:---:|---|
| DNS direct/omgekeerd | Systeemresolver | nee | Licht actief |
| RDAP | IANA-bootstrap → RIR/registrar | nee | Openbaar passief |
| Certificate Transparency | `crt.sh` (Sectigo) | nee | Openbaar passief |
| Webarchieven | Wayback Machine (Internet Archive) | nee | Openbaar passief |
| BGP / netwerkaankondigingen | RIPEstat (RIPE NCC) | nee | Openbaar passief |
| GeoIP | DB-IP Lite (standaard) of MaxMind GeoLite2 | nee / ja | Offline (lokale database) |
| NeoTrace | Lokale `traceroute`/`tracepath` | nee | Licht actief |
| Reputatie | VirusTotal | ja (gratis) | Met sleutel |
| Reputatie | Have I Been Pwned | ja (betaald) | Met sleutel |

Exact quotum, licentie en terugvaloptie per bron: `docs/DATA_SOURCES.md`. Geen enkele API-sleutel verschijnt ooit in logs, exports of diagnoseschermen.

## 7. Vertrouwensbeleid

Elk verzameld veld draagt een van de volgende niveaus (gedeeld met de hele suite via `omega-lib`):

| Niveau | Betekenis |
|---|---|
| `VERIFIED` | Rechtstreeks waargenomen protocolfeit dat het doel niet kan vervalsen (bijv. direct DNS-antwoord, lokale traceroutemeting). |
| `DECLARED` | Waarde die de bron zelf opgeeft in een veld dat zij volledig beheert (bijv. RDAP-gegeven getoond door de registrar) — aannemelijk, maar naar believen te vervalsen. |
| `CORROBORATED` | Een `DECLARED`-waarde bevestigd door een onafhankelijke aanwijzing (bijv. een domein waargenomen in ten minste twee verschillende Certificate Transparency-logs). |
| `INFERRED` | Afgeleid uit een patroon/heuristiek, zonder expliciete verklaring (bijv. gemeenschappelijk ASN gebruikt om een relatie te suggereren, nooit automatisch opgewaardeerd). |
| `UNKNOWN` | Geen bruikbare aanwijzing, of actief verborgen door het doel. |

De algemene vertrouwensscore van een observatie is een leeshulp, nooit een beveiligingsoordeel.

## 8. Verzamelniveaus, autorisatie en redactie

Elk profiel maakt de aard van zijn acties expliciet (`CollectionMode`):

- **Offline**: validatie van het doel, lokaal GeoIP lezen, correlaties op reeds opgeslagen gegevens, exports — geen netwerk.
- **Openbaar passief**: RDAP, openbare DNS, CT-logs, archieven, BGP — alleen het geraadpleegde doel wordt aan de derde doorgegeven, een eigenschap die inherent is aan het protocol.
- **Licht actief**: DNS-resolutie, reverse DNS, traceroute — de op de machine geconfigureerde resolver en elke tussenliggende router op het pad zien het verzoek.
- **Met gebruikerssleutel**: leveranciers die een sleutel eisen of quota toepassen, alleen ingeschakeld na expliciete configuratie en getoonde openbaarmaking (quotum, verzonden gegevens).

**Autorisatiebewaking**: geen enkele observatie start op een niet-vastgezet doel zonder expliciete bevestiging (`--authorize` in de CLI, selectievakje in de TUI). Een doel vastzetten autoriseert het blijvend voor zijn toekomstige observaties.

**Redactie van exports**: elke export accepteert een beleid (`none`/`contacts_only`/`sensitive_only`/`strict`) dat gevoelige velden (met name RDAP-contacten) in de geëxporteerde uitvoer maskeert — de lokale opslag bewaart daarentegen altijd de volledige verzamelde gegevens. Details: `docs/PRIVACY.md`.

## 9. Terminalcompatibiliteit

De TUI (Textual) detecteert automatisch de mogelijkheden van de terminal (emulator, grootte) en past zijn structurele stylesheet daarop aan (`complete`/`standard`/`reduced`/`mono`), zonder handmatige vlag. De CLI-modus blijft altijd platte tekst, onafhankelijk van de terminal. Beleid gedeeld door de hele `omega-`-suite (`omega-lib`, `terminal/policies.py`).

### Profiel volgens gedetecteerde emulator

| Emulator | Beginprofiel |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, moderne SSH | `reduced` |
| Linux-TTY, oudere SSH | `mono` |
| Niet-herkende emulator | `reduced` (standaard terugval) |

### Profiel volgens terminalgrootte

| Minimale grootte (kolommen × regels) | Profielplafond |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| daaronder | `mono` |

Het uiteindelijk gekozen profiel is **het meest beperkende van de twee** (emulator en grootte). Het kan live worden vernieuwd met de toets `r`.

## 10. Exports

Markdown- en HTML-rapporten worden geschreven in de taal die in de Instellingen is gekozen ("Taal van de exports", standaard die van de interface); JSON, CSV, DOT en Mermaid blijven gegevens en worden niet vertaald. De rapporten worden standaard aangemaakt in `var/exports/` (runtimepad verankerd aan de projectmap, `$OMEGA_TRACK_VAR_DIR` om het te overschrijven), of op het opgegeven pad (`--output` in de CLI, dialoogvenster in de TUI). Unieke bestandsnaam met tijdstempel: `{tijdstempel}_{doel}_{korte_id}.{extensie}`.

| Formaat | Inhoud |
|---|---|
| `json` | Volledige structuur van de observatie (`TrackRun` + findings + relaties), bron van waarheid, strikt JSON-serialiseerbaar |
| `markdown` | Compact, menselijk leesbaar rapport, leesbaar buiten de terminal |
| `html` | Zelfstandig webrapport, 5 thema's naar keuze (`--theme`), Mermaid-relatiegraaf inline ingebed |
| `csv` | Eén tabel per findingcategorie |
| `dot` | Graphviz-relatiegraaf, zelfstandig bestand |
| `mermaid` | Mermaid-relatiegraaf, zelfstandig bestand |

## 11. Geschiedenis, opschonen en opnieuw afspelen

Elke observatie wordt opgeslagen (SQLite, `var/db/omega-track.db`): doorzoekbare en filterbare geschiedenis (doel/status/tag/periode), samenvattend dashboard (verdeling per status, betrouwbaarheid per module, typologie van de laatste findings), opnieuw afspelen van een observatie op hetzelfde doel zonder opnieuw invoeren (`track replay`), en opschonen van oude geschiedenis met een systematisch voorbeeld vóór elke verwijdering (`cleanup preview` vóór `cleanup run --yes`).

## 12. Tests

```bash
source .venv/bin/activate
lint-imports        # controleert de Dependency Rule
pytest -q           # 485 tests
ruff check .
mypy src
```

Structuur: `tests/unit/` (domein en applicatie, zonder echte I/O), `tests/integration/` (echte SQLite/bestanden, nep-HTTP-server `pytest-httpserver`, headless TUI via de `Pilot`-API van Textual).

## 13. Buiten de reikwijdte

- Volledige WHOIS/DNS-geschiedenis, commerciële passive DNS
- Zoeken naar personen, sociale netwerken, pastebins/lekken
- Poortscan, herkenning van diensten en banners (`omega-check`)
- HTTP/HTTPS-controles, headers, TLS (`omega-scan`)
- Crawl en doorlopen van architectuur (`omega-deep`/`omega-fold`)
- Belastingtests (`omega-stress`), fuzzing (`omega-fuzz`)
- Interactieve TUI-kaart (voorbehouden aan het geëxporteerde HTML-rapport)
- Continue MTR, met meerdere probes en meerdere meetpunten
- Batch-/periodieke modus of terugkerende bewaking van een doel — een `TrackRun` blijft altijd een expliciete handmatige actie
- Migratie-engine voor het SQLite-schema (additief schema, dezelfde praktijk als in de rest van de suite)

---

> Omega-track — Observeren, correleren, kwalificeren, rapporteren.
> Een digitale identiteit met expliciet vertrouwen in elk gegeven, nooit een vermomde zekerheid.
