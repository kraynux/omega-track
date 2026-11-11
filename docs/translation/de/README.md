<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - MIT-Lizenz (siehe Datei LICENSE) -->
<div align="center">
  <img src="../../assets/omega-track.png" alt="Omega-Track" width="386">
</div>

# 🛰️ OMEGA-TRACK

**Profiling digitaler Identitäten und Beobachtung von Netzwerkpfaden**

> Entwickelt von [kraynux](https://github.com/kraynux) für [Omega-Server](https://kraynux.snake-mackarel.ts.net)   

Offizielle Seite: [OMEGA-TRACK](https://kraynux.snake-mackarel.ts.net/omega-track/) &nbsp; Vorschau: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-track/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 Oberfläche und exportierte Berichte in **17 Sprachen** verfügbar — siehe [Sprachen der Oberfläche](#sprachen-der-oberfläche).  
**Sprachen:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

---

**Omega-track** ist ein TUI- + CLI-Werkzeug, das aus einer IP, einer IPv6-Adresse oder einer Domain die vollständigste mögliche digitale Identität aufbaut: wer hinter diesem Ziel antwortet, wie man dorthin gelangt und mit welchem Vertrauensniveau jede Information als gesichert gelten kann. Es ist ein Werkzeug der `omega-`-Suite, aufgebaut nach Clean Architecture — siehe `docs/PRODUCT_SCOPE.md` und `docs/DATA_SOURCES.md` für alle Einzelheiten.

<p align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/de/omega-track/A.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/de/omega-track/B.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/de/omega-track/C.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/de/omega-track/D.png" width="24%" />
</p>

## 1. Vision und Umfang

Omega-track beantwortet zwei Fragen: „Wer ist dieses Ziel?“ (Identität über RDAP/DNS/Zertifikate/Reputation) und „Wie gelangt man dorthin?“ (Netzwerkpfad NeoTrace, GeoIP, ASN). Es ergänzt `omega-check` (Netzwerkexposition), `omega-scan` (HTTP/HTTPS-Hygiene) und `omega-deep` (begrenzte Architekturanalyse), ohne sie zu duplizieren.

### Was Omega-track tut

- Akzeptiert ein Ziel als IP, IPv6 oder Domainname, gespeichert und optional angeheftet (dauerhafte Autorisierung).
- Bündelt öffentliche Informationen, passiv oder ausdrücklich durch das Profil aktiviert (RDAP, DNS, Certificate Transparency, Wayback-Archive, BGP-Ankündigungen).
- Führt ein angereichertes Traceroute im NeoTrace-Stil aus (die einzige aktive Netzwerkaktion im Kern des Produkts).
- Reichert jede relevante IP über eine lokale GeoIP-Datenbank an (DB-IP Lite ohne Schlüssel, optional MaxMind GeoLite2 mit Schlüssel).
- Fragt mit einem vom Benutzer bereitgestellten Schlüssel Reputationsquellen ab (VirusTotal, HIBP), mit systematischer Offenlegung (Kontingent, gesendete Daten) vor jeder Aktivierung.
- Setzt die beobachteten Daten in Beziehung, um ein stimmiges Profil zu bilden, mit einem ausdrücklichen Vertrauensniveau für jedes Datum.
- Speichert Ziele, Durchläufe, Ergebnisse, Fehler und Exporte lokal (SQLite, `./var/`).
- Bietet eine Textual-TUI und eine CLI, die funktional streng gleichwertig sind.
- Erzeugt HTML-Berichte (5 Themes, eingebetteter Mermaid-Beziehungsgraph), JSON, Markdown, CSV sowie eigenständige DOT- und Mermaid-Dateien.

### Was Omega-track nicht tut

| Funktion | Zuständiges Werkzeug |
|---|---|
| Portscan, Erkennung von Diensten und Bannern | OMEGA-CHECK |
| HTTP/HTTPS-Prüfungen, Header, TLS, Web-Hygiene | OMEGA-SCAN |
| Crawl, Durchlaufen der Architektur und Abstieg auf verknüpfte Ziele | OMEGA-DEEP |
| Entfernter Crawl Seite für Seite (Links, Dateien) | OMEGA-FOLD |
| Lasttests | OMEGA-STRESS |
| Fuzzing und Robustheitstests von Anwendungen | OMEGA-FUZZ |

Zu vermeiden, auch außerhalb des MVP: Brute-Force von Subdomains, Portscan, Web-Crawl, eingreifende Erhebung personenbezogener Daten, automatisiertes Umgehen von Schutzmaßnahmen, fragiles Scraping von Plattformen mit Authentifizierungspflicht, Suche nach Personen/sozialen Netzwerken/Pastebins-Leaks, periodische/wiederkehrende Überwachung eines Ziels (siehe `docs/PRODUCT_SCOPE.md` §7 "Bewusst zurückgestellt").

### Hinweis zur autorisierten Nutzung

Omega-track ist ein Werkzeug für Netzwerkuntersuchungen, das für eine legitime Nutzung gedacht ist: Audit der eigenen Infrastruktur, Reaktion auf Vorfälle, Beobachtung eines Bereichs, den Sie dokumentieren dürfen. Die Erhebung bleibt fast vollständig passiv/öffentlich (RDAP, DNS, CT-Logs — Daten, die das Ziel oder sein Registrar bereits öffentlich zugänglich macht), mit Ausnahme des Traceroute (leicht aktiv, im verwendeten Profil stets sichtbar).

**Keine Beobachtung startet auf einem nicht angehefteten Ziel ohne ausdrückliche Bestätigung** (`--authorize` in der CLI, Bestätigung in der TUI). Sie allein sind dafür verantwortlich zu prüfen, dass Ihre Nutzung den geltenden Gesetzen und den Nutzungsbedingungen der abgefragten Drittquellen entspricht.

## 2. Installation

### Voraussetzungen

- Python 3.10+
- Internetverbindung, für die Abhängigkeiten und die abgefragten passiven Quellen
- `traceroute` oder `tracepath` installiert (Modul NeoTrace) — fehlt es, wird sauber herabgestuft, der Rest des Werkzeugs funktioniert normal

### Installation

```bash
[ -d omega-track ] && echo "ℹ️ Bereits hier entpackt, Schritt übersprungen." || tar -xzf omega-track.tar.gz
cd omega-track/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. Legt die virtuelle Umgebung `.venv` an, falls sie noch nicht existiert.
2. Installiert die Abhängigkeiten (`pip install -e .`, `pyproject.toml` bleibt die einzige maßgebliche Quelle).
3. Macht `omega-track.sh` und `install.sh` ausführbar.
4. Fügt den Alias `track` zu `~/.bashrc` und `~/.zshrc` hinzu (ohne Duplikat, falls bereits vorhanden).

### Abhängigkeiten

Deklariert in `pyproject.toml` (keine separate `requirements.txt`):
- `omega-lib`: gemeinsame Bibliothek der Suite (`ConfidenceLevel`, Themes, Terminalerkennung)
- `textual`: TUI-Oberfläche, Themes, automatische Anpassung an das Terminal
- `dnspython`: direkte und inverse DNS-Auflösung
- `httpx`: Sonden für RDAP/CT/Archive/BGP/VirusTotal/HIBP
- `maxminddb`: Lesen der lokalen GeoIP-Datenbanken (DB-IP Lite, MaxMind GeoLite2)
- `jinja2`: Templating für den HTML-Export
- Entwicklungsabhängigkeiten (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-httpserver`, `ruff`, `mypy`, `import-linter`

## 3. Verwendung

### Interaktiver Modus (TUI)

Empfohlen für den täglichen Gebrauch — ohne Argument gestartet:

```bash
./omega-track.sh
```
wenn Sie den Alias angelegt haben, tippen Sie einfach `track` im Terminal:
```bash
track
```

Ablauf: Startbildschirm (schließt sich bei einem Tastendruck oder Klick) → Hauptmenü (Ziele / Tracker / Ergebnisse / Verlauf / Dashboard / GeoIP / Quellen mit Schlüssel / Einstellungen / Hilfe) → Eingabe oder Auswahl des Ziels (ausdrückliche Bestätigung, falls nicht angeheftet) und Wahl der Erhebungsmodule → Beobachtung (Anzeige und Ablauf der Vorgänge live, abbrechbar) → detaillierte Ergebnisse je Reiter (Identität/DNS/Netzwerk / ASN/NeoTrace/Zertifikate/Archive/Beziehungen/Diagnose, Export) → Verlauf/Dashboard/Einstellungen aus dem Hauptmenü. Die Anpassung an das Terminal (Farben, Größe, strukturelle Herabstufung) erfolgt automatisch.

#### Tastenkürzel

| Taste | Aktion |
|---|---|
| `↑` / `↓` | Zwischen den Elementen eines Bildschirms navigieren |
| `Tab` / `Umschalt+Tab` | Zwischen den Feldern eines Formulars navigieren |
| `Esc` | Zurück zum vorherigen Bildschirm (Beenden-Bestätigung auf dem Startbildschirm) |
| `t` | Nächstes Theme (sofort angewendet, ohne Bestätigung) |
| `r` | Terminalerkennung aktualisieren |
| `a` | Hilfe anzeigen |
| `q` | Beenden (mit Bestätigung) |

### Sprachen der Oberfläche

Die Oberfläche ist in 17 Sprachen verfügbar: Französisch, Englisch, Spanisch, Portugiesisch (Brasilien), Italienisch, Deutsch, Niederländisch, Polnisch, Russisch, vereinfachtes Chinesisch, Vietnamesisch, Thailändisch, Indonesisch, Japanisch, Koreanisch, Hindi und Arabisch. Die Auswahl erfolgt in den Einstellungen („Langue / Language“) und gilt nach einem Neustart der Oberfläche; die Variable `OMEGA_TRACK_LANG` (zum Beispiel `OMEGA_TRACK_LANG=de ./omega-track.sh`) erzwingt eine Sprache für eine Sitzung. Aus omega-suite gestartet, übernimmt omega-track die Sprache der Suite. Auf einer Linux-Textkonsole (TTY) werden Sprachen mit nicht-lateinischer Schrift für die Dauer der Sitzung auf Englisch angezeigt. Die Befehlszeile bleibt auf Französisch.

### Kontakt und Support

Die Hilfe (Taste `a`) bietet einen Bildschirm **Kontakt und Support**: *Einen Kaffee spendieren* (PayPal-Seite des Entwicklers), *Support kontaktieren* (E-Mail-Adresse und Kontaktformular der Website, im Klartext angezeigt), *Mich als Nutzer melden (anonym)* und *Updates prüfen*. Die Meldung ist freiwillig, standardmäßig deaktiviert und wird nur ein einziges Mal gesendet: Sie dient nur dazu, die Nutzer zu zählen und, wenn gewünscht, ihren Kontinent oder ihr Land (geschlossene Listen, nie Freitext). Gesendet werden ein zufällig gezogener Schlüssel, der Name der Software (`omega-track`) und ihre Version; nie ein Name, ein Rechnername, eine Einstellung, ein Ziel oder ein Ergebnis. Die IP-Adresse wird in den Meldungen nicht gespeichert, durchläuft aber wie jeder Besuch die Sicherheitsprüfungen und das Protokoll des Empfangsservers. Rückzug jederzeit über denselben Bildschirm (*Mich nicht mehr melden*). Die Update-Prüfung liest nur die Liste der auf der Website veröffentlichten Versionen, und nie ohne Klick.

### Skriptfähiger Modus (CLI)

Jeder Unterbefehl löst den CLI-Modus aus:

```bash
# Ziele
./omega-track.sh target add example.org --alias "Schaufenster-Website" --tag prod
./omega-track.sh target list
./omega-track.sh target pin <target_id>

# Eine Beobachtung starten und verfolgen
./omega-track.sh track run <target_id> --module dns --module rdap --module neotrace --authorize
./omega-track.sh track status <run_id>
./omega-track.sh track show <run_id>
./omega-track.sh track replay <run_id> --authorize

# Verlauf
./omega-track.sh history list --target <target_id> --status completed --since 2026-01-01

# Export — 6 Formate, 5 Themes für HTML
./omega-track.sh export <run_id> --format html --theme omega-neon --redact contacts_only

# GeoIP
./omega-track.sh geoip status
./omega-track.sh geoip update --provider dbip

# Reputationsquellen mit Schlüssel (Offenlegung vor jeder Speicherung angezeigt)
./omega-track.sh source list
./omega-track.sh source info virustotal
./omega-track.sh source configure virustotal <api_schluessel>

# Einstellungen und Bereinigung
./omega-track.sh config show
./omega-track.sh cleanup preview --older-than 30
./omega-track.sh cleanup run --older-than 30 --yes

# Lokale Diagnose (Versionen, Fähigkeiten, Pfade, GeoIP-Status)
./omega-track.sh diagnostics
```

Jeder Unterbefehl akzeptiert `--json` für eine streng maschinenlesbare Ausgabe.

#### Exit-Codes

| Code | Bedeutung |
|---:|---|
| `0` | Erfolg (Beobachtung abgeschlossen, `COMPLETED`) |
| `1` | Validierungsfehler (ungültiges Ziel, unbekanntes Exportformat, ungültiger Zustandsübergang, fehlender API-Schlüssel...) |
| `2` | Ziel nicht autorisiert (weder angeheftet noch `--authorize`) |
| `3` | Ressource nicht gefunden oder Quelle nicht verfügbar (unbekanntes Ziel/unbekannter Durchlauf, fehlgeschlagener GeoIP-Download) |
| `4` | Teilweise Beobachtung (`PARTIAL`) — kein Fehlschlag, nur einige Module waren erfolgreich |
| `5` | Unerwarteter interner Fehler |
| `130` | Vom Benutzer unterbrochen (`Ctrl+C`) |

### Akzeptierte Zielformate

```text
192.168.1.10                IPv4
2001:db8::1                 IPv6
example.org                 Domain
```

## 4. Erhebungsmodule

| Modul | Erhebungsmodus | Standardmäßig aktiv | Schlüssel erforderlich |
|---|---|:---:|:---:|
| `dns` | Leicht aktiv (direkte Auflösung) | ja | nein |
| `reverse_dns` | Leicht aktiv (PTR) | ja | nein |
| `rdap` | Öffentlich passiv | ja | nein |
| `neotrace` | Leicht aktiv (traceroute/tracepath) | ja | nein |
| `certificate_transparency` | Öffentlich passiv (`crt.sh`) | nein | nein |
| `archives` | Öffentlich passiv (Wayback Machine) | nein | nein |
| `bgp` | Öffentlich passiv (RIPEstat) | nein | nein |
| `virustotal` | Mit Benutzerschlüssel | nein | ja (kostenlos) |
| `hibp` | Mit Benutzerschlüssel | nein | ja (seit 2022 **kostenpflichtig**) |

Die ersten vier Module bilden die MVP-Basis (`dns`/`reverse_dns`/`rdap`/`neotrace`) und sind im Startformular standardmäßig angehakt; die fünf folgenden sind optional und müssen ausdrücklich aktiviert werden. Eine Quelle ohne konfigurierten Schlüssel lässt die Beobachtung nie fehlschlagen: Das zugehörige Modul wechselt einfach auf `SKIPPED` („nicht ausgeführt“). Einzelheiten je Quelle, Kontingente und Lizenzen: `docs/DATA_SOURCES.md`.

## 5. Architektur

Omega-track ist nach **Clean Architecture** aufgebaut (domain / application / infrastructure / interfaces / ports / core / app / plugins), an der Vorlage der `omega-`-Suite ausgerichtet (siehe `omega-check`/`omega-fold`) und bei jeder Änderung durch `import-linter` geprüft.

```text
src/omega_track/
├── domain/          Reine Geschäftslogik (Ziele, TrackRun/ModuleRun, Findings, Beziehungen, Profile...)
├── application/     Anwendungsfälle (commands/queries/Phasen-Orchestratoren/Richtlinien)
├── ports/           Von der Anwendung erwartete Verträge (Sammler, Repositories, Exporter...)
├── infrastructure/  Konkrete Implementierungen (dnspython/httpx/subprocess/maxminddb, SQLite, jinja2)
├── interfaces/      tui/ (Textual) und cli/ (skriptfähig), in strenger funktionaler Parität
├── app/             Zusammensetzung (DependencyContainer, Bootstrap, Lebenszyklus)
├── core/            Übergreifendes Vokabular (Versionen, Re-Exporte aus omega-lib)
└── plugins/         Optionale Module mit einer einzigen Quelle (CT, Archive, BGP, VirusTotal, HIBP)
```

Entwurfsregeln:
- `domain/` macht nie Netzwerk oder I/O; `infrastructure/` macht Netzwerk und I/O, urteilt aber nie.
- `interfaces/` zeigt an und enthält keine Geschäftslogik — CLI und TUI rufen streng dieselben Anwendungsfälle auf.
- 1 Erhebungsmodul = 1 Quelle = 1 Status (`ModuleRun`): nie zwei Quellen unter einem einzigen mehrdeutigen Status zusammengefasst.
- Das Fehlen eines einzelnen Feldes ist nie ein Fehler; nur die vollständige Nichtverfügbarkeit einer Quelle löst `SKIPPED`/`FAILED` aus.

## 6. Datenquellen

| Quelle | Anbieter | Schlüssel | Modus |
|---|---|:---:|---|
| DNS direkt/invers | System-Resolver | nein | Leicht aktiv |
| RDAP | IANA-Bootstrap → RIR/Registrar | nein | Öffentlich passiv |
| Certificate Transparency | `crt.sh` (Sectigo) | nein | Öffentlich passiv |
| Web-Archive | Wayback Machine (Internet Archive) | nein | Öffentlich passiv |
| BGP / Netzwerkankündigungen | RIPEstat (RIPE NCC) | nein | Öffentlich passiv |
| GeoIP | DB-IP Lite (Standard) oder MaxMind GeoLite2 | nein / ja | Offline (lokale Datenbank) |
| NeoTrace | Lokales `traceroute`/`tracepath` | nein | Leicht aktiv |
| Reputation | VirusTotal | ja (kostenlos) | Mit Schlüssel |
| Reputation | Have I Been Pwned | ja (kostenpflichtig) | Mit Schlüssel |

Genaues Kontingent, Lizenz und Rückfallebene je Quelle: `docs/DATA_SOURCES.md`. Kein API-Schlüssel erscheint jemals in Logs, Exporten oder Diagnosebildschirmen.

## 7. Vertrauensrichtlinie

Jedes erhobene Feld trägt eine der folgenden Stufen (mit der ganzen Suite über `omega-lib` geteilt):

| Stufe | Bedeutung |
|---|---|
| `VERIFIED` | Direkt beobachtete Protokolltatsache, die das Ziel nicht fälschen kann (z. B. direkte DNS-Antwort, lokale Traceroute-Messung). |
| `DECLARED` | Von der Quelle selbst angegebener Wert in einem Feld, das sie vollständig kontrolliert (z. B. vom Registrar angezeigte RDAP-Daten) — plausibel, aber beliebig fälschbar. |
| `CORROBORATED` | Ein `DECLARED`-Wert, der durch ein unabhängiges Indiz bestätigt wird (z. B. eine Domain, die in mindestens zwei verschiedenen Certificate-Transparency-Logs beobachtet wurde). |
| `INFERRED` | Aus einem Muster/einer Heuristik abgeleitet, ohne ausdrückliche Angabe (z. B. gemeinsames ASN, das eine Beziehung nahelegt, nie automatisch hochgestuft). |
| `UNKNOWN` | Kein verwertbares Indiz, oder vom Ziel aktiv verborgen. |

Der globale Vertrauenswert einer Beobachtung ist eine Lesehilfe, nie ein Sicherheitsurteil.

## 8. Erhebungsstufen, Autorisierung und Schwärzung

Jedes Profil macht die Art seiner Aktionen ausdrücklich (`CollectionMode`):

- **Offline**: Zielvalidierung, lokales GeoIP-Lesen, Korrelationen auf bereits gespeicherten Daten, Exporte — kein Netzwerk.
- **Öffentlich passiv**: RDAP, öffentliches DNS, CT-Logs, Archive, BGP — nur das abgefragte Ziel wird an den Dritten übermittelt, eine dem Protokoll innewohnende Eigenschaft.
- **Leicht aktiv**: DNS-Auflösung, Reverse-DNS, Traceroute — der auf dem Rechner konfigurierte Resolver und jeder Zwischenrouter auf dem Pfad sehen die Anfrage.
- **Mit Benutzerschlüssel**: Anbieter, die einen Schlüssel verlangen oder Kontingente anwenden, nur nach ausdrücklicher Konfiguration und angezeigter Offenlegung (Kontingent, gesendete Daten) aktiviert.

**Autorisierungsschutz**: Keine Beobachtung startet auf einem nicht angehefteten Ziel ohne ausdrückliche Bestätigung (`--authorize` in der CLI, Kontrollkästchen in der TUI). Das Anheften eines Ziels autorisiert es dauerhaft für seine künftigen Beobachtungen.

**Schwärzung der Exporte**: Jeder Export akzeptiert eine Richtlinie (`none`/`contacts_only`/`sensitive_only`/`strict`), die sensible Felder (insbesondere RDAP-Kontakte) in der exportierten Ausgabe verbirgt — der lokale Speicher behält dagegen immer die vollständig erhobenen Daten. Einzelheiten: `docs/PRIVACY.md`.

## 9. Terminal-Kompatibilität

Die TUI (Textual) erkennt automatisch die Fähigkeiten des Terminals (Emulator, Größe) und passt ihr strukturelles Stylesheet entsprechend an (`complete`/`standard`/`reduced`/`mono`), ohne manuelles Flag. Der CLI-Modus bleibt immer einfacher Text, unabhängig vom Terminal. Diese Richtlinie wird von der gesamten `omega-`-Suite geteilt (`omega-lib`, `terminal/policies.py`).

### Profil nach erkanntem Emulator

| Emulator | Anfangsprofil |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, modernes SSH | `reduced` |
| Linux-TTY, älteres SSH | `mono` |
| Nicht erkannter Emulator | `reduced` (Standard-Rückfall) |

### Profil nach Terminalgröße

| Mindestgröße (Spalten × Zeilen) | Profil-Obergrenze |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| darunter | `mono` |

Das endgültig gewählte Profil ist **das restriktivere der beiden** (Emulator und Größe). Es lässt sich live mit der Taste `r` aktualisieren.

## 10. Exporte

Markdown- und HTML-Berichte werden in der in den Einstellungen gewählten Sprache verfasst („Sprache der Exporte“, standardmäßig die der Oberfläche); JSON, CSV, DOT und Mermaid bleiben Daten und werden nicht übersetzt. Die Berichte werden standardmäßig in `var/exports/` erzeugt (Laufzeitpfad, verankert im Projektordner, `$OMEGA_TRACK_VAR_DIR` zum Überschreiben), oder unter dem angegebenen Pfad (`--output` in der CLI, Dialogfeld in der TUI). Eindeutiger Dateiname mit Zeitstempel: `{zeitstempel}_{ziel}_{kurz_id}.{erweiterung}`.

| Format | Inhalt |
|---|---|
| `json` | Vollständige Struktur der Beobachtung (`TrackRun` + Findings + Beziehungen), maßgebliche Quelle, streng JSON-serialisierbar |
| `markdown` | Kompakter, menschenlesbarer Bericht, außerhalb des Terminals lesbar |
| `html` | Eigenständiger Web-Bericht, 5 Themes zur Auswahl (`--theme`), Mermaid-Beziehungsgraph inline eingebettet |
| `csv` | Eine Tabelle pro Finding-Kategorie |
| `dot` | Graphviz-Beziehungsgraph, eigenständige Datei |
| `mermaid` | Mermaid-Beziehungsgraph, eigenständige Datei |

## 11. Verlauf, Bereinigung und Wiederholung

Jede Beobachtung wird gespeichert (SQLite, `var/db/omega-track.db`): durchsuchbarer und filterbarer Verlauf (Ziel/Status/Tag/Zeitraum), zusammenfassendes Dashboard (Verteilung nach Status, Zuverlässigkeit je Modul, Typologie der letzten Findings), Wiederholung einer Beobachtung auf demselben Ziel ohne erneute Eingabe (`track replay`) und Bereinigung des alten Verlaufs mit systematischer Vorschau vor jeder Löschung (`cleanup preview` vor `cleanup run --yes`).

## 12. Tests

```bash
source .venv/bin/activate
lint-imports        # prüft die Dependency Rule
pytest -q           # 485 Tests
ruff check .
mypy src
```

Aufbau: `tests/unit/` (Domäne und Anwendung, ohne echtes I/O), `tests/integration/` (echtes SQLite/echte Dateien, Fake-HTTP-Server `pytest-httpserver`, Headless-TUI über die `Pilot`-API von Textual).

## 13. Außerhalb des Umfangs

- Vollständiger WHOIS/DNS-Verlauf, kommerzielles Passive DNS
- Suche nach Personen, sozialen Netzwerken, Pastebins/Leaks
- Portscan, Erkennung von Diensten und Bannern (`omega-check`)
- HTTP/HTTPS-Prüfungen, Header, TLS (`omega-scan`)
- Crawl und Durchlaufen der Architektur (`omega-deep`/`omega-fold`)
- Lasttests (`omega-stress`), Fuzzing (`omega-fuzz`)
- Interaktive TUI-Karte (dem exportierten HTML-Bericht vorbehalten)
- Kontinuierliches MTR, mehrere Sonden und mehrere Beobachtungspunkte
- Batch-/periodischer Modus oder wiederkehrende Überwachung eines Ziels — ein `TrackRun` bleibt immer eine ausdrückliche manuelle Aktion
- Migrations-Engine für das SQLite-Schema (additives Schema, gleiche Praxis wie im Rest der Suite)

---

> Omega-track — Beobachten, korrelieren, einordnen, berichten.
> Eine digitale Identität mit ausdrücklichem Vertrauen in jedes Datum, nie eine verkleidete Gewissheit.
