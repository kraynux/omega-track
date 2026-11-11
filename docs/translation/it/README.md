<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Licenza MIT (vedi file LICENSE) -->
<div align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/assets/omega-track.png" alt="Omega-Track" width="512">
</div>

# 🛰️ OMEGA-TRACK

**Profilazione dell'identità digitale e osservazione del percorso di rete**

> Realizzato da [kraynux](https://github.com/kraynux) per [Omega-Server](https://kraynux.snake-mackarel.ts.net)   

Pagina ufficiale: [OMEGA-TRACK](https://kraynux.snake-mackarel.ts.net/omega-track/) &nbsp; Anteprima: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-track/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 Interfaccia e report esportati disponibili in **17 lingue** — vedi [Lingue dell'interfaccia](#lingue-dellinterfaccia).  
**Lingue:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](../pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

---

**Omega-track** è uno strumento TUI + CLI che costruisce, a partire da un IP, un indirizzo IPv6 o un dominio, l'identità digitale più completa possibile: chi risponde dietro questo obiettivo, come ci si arriva e con quale livello di fiducia ogni informazione può essere considerata acquisita. È uno strumento della suite `omega-`, strutturato in Clean Architecture — vedi `docs/PRODUCT_SCOPE.md` e `docs/DATA_SOURCES.md` per il dettaglio completo.

<p align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/it/omega-track/A.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/it/omega-track/B.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/it/omega-track/C.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/it/omega-track/D.png" width="24%" />
</p>

## 1. Visione e perimetro

Omega-track risponde a due domande: «chi è questo obiettivo?» (identità RDAP/DNS/certificati/reputazione) e «come ci si arriva?» (percorso di rete NeoTrace, GeoIP, ASN). Completa `omega-check` (esposizione di rete), `omega-scan` (igiene HTTP/HTTPS) e `omega-deep` (analisi di architettura delimitata), senza duplicarli.

### Cosa fa Omega-track

- Accetta un obiettivo IP, IPv6 o nome di dominio, registrato ed eventualmente fissato (autorizzazione duratura).
- Centralizza informazioni pubbliche, passive o attivate esplicitamente dal profilo (RDAP, DNS, Certificate Transparency, archivi Wayback, annunci BGP).
- Esegue un traceroute arricchito di tipo NeoTrace (l'unica azione di rete attiva del cuore del prodotto).
- Arricchisce ogni IP rilevante tramite una base GeoIP locale (DB-IP Lite senza chiave, MaxMind GeoLite2 opzionale con chiave).
- Interroga, con una chiave fornita dall'utente, fonti di reputazione (VirusTotal, HIBP), con divulgazione sistematica (quota, dati inviati) prima di qualsiasi attivazione.
- Mette in relazione i dati osservati per formare un profilo coerente, con un livello di fiducia esplicito su ogni dato.
- Conserva obiettivi, esecuzioni, risultati, errori ed esportazioni in locale (SQLite, `./var/`).
- Fornisce una TUI Textual e una CLI rigorosamente equivalenti nelle funzioni.
- Produce report HTML (5 temi, grafo delle relazioni Mermaid incorporato), JSON, Markdown, CSV, e file DOT e Mermaid autonomi.

### Cosa non fa Omega-track

| Funzione | Strumento responsabile |
|---|---|
| Scansione delle porte, identificazione di servizi e banner | OMEGA-CHECK |
| Controlli HTTP/HTTPS, header, TLS, igiene web | OMEGA-SCAN |
| Crawl, attraversamento dell'architettura e discesa sugli obiettivi collegati | OMEGA-DEEP |
| Crawl remoto pagina per pagina (link, file) | OMEGA-FOLD |
| Test di carico | OMEGA-STRESS |
| Fuzzing e test di robustezza applicativa | OMEGA-FUZZ |

Da evitare, anche al di fuori dell'MVP: brute-force di sottodomini, scansione delle porte, crawl web, raccolta intrusiva di dati personali, automazione per aggirare le protezioni, scraping fragile di piattaforme che richiedono autenticazione, ricerca di persone/social network/pastebin-leak, sorveglianza periodica/ricorrente di un obiettivo (vedi `docs/PRODUCT_SCOPE.md` §7 "Rimandato volontariamente").

### Avvertenza sull'uso autorizzato

Omega-track è uno strumento di indagine di rete destinato a un uso legittimo: audit della propria infrastruttura, risposta agli incidenti, monitoraggio di un perimetro che si è autorizzati a documentare. La raccolta resta quasi interamente passiva/pubblica (RDAP, DNS, CT log — dati che l'obiettivo o il suo registrar espongono già pubblicamente), ad eccezione del traceroute (attivo leggero, sempre visibile nel profilo usato).

**Nessuna osservazione parte su un obiettivo non fissato senza conferma esplicita** (`--authorize` nella CLI, conferma nella TUI). Sei l'unico responsabile della verifica che il tuo uso rispetti le leggi applicabili e le condizioni d'uso delle fonti di terze parti consultate.

## 2. Installazione

### Prerequisiti

- Python 3.10+
- Connessione a Internet, per le dipendenze e le fonti passive interrogate
- `traceroute` o `tracepath` installato (modulo NeoTrace) — degrada in modo pulito se assente, il resto dello strumento funziona normalmente

### Installazione

```bash
[ -d omega-track ] && echo "ℹ️ Già estratto qui, passaggio saltato." || tar -xzf omega-track.tar.gz
cd omega-track/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. Crea l'ambiente virtuale `.venv` se non esiste ancora.
2. Installa le dipendenze (`pip install -e .`, `pyproject.toml` resta l'unica fonte di verità).
3. Rende eseguibili `omega-track.sh` e `install.sh`.
4. Aggiunge l'alias `track` a `~/.bashrc` e `~/.zshrc` (senza duplicati se già presente).

### Dipendenze

Dichiarate in `pyproject.toml` (nessun `requirements.txt` separato):
- `omega-lib`: libreria condivisa della suite (`ConfidenceLevel`, temi, rilevamento del terminale)
- `textual`: interfaccia TUI, temi, adattamento automatico al terminale
- `dnspython`: risoluzione DNS diretta e inversa
- `httpx`: sonde RDAP/CT/archivi/BGP/VirusTotal/HIBP
- `maxminddb`: lettura delle basi GeoIP locali (DB-IP Lite, MaxMind GeoLite2)
- `jinja2`: template per l'esportazione HTML
- Dipendenze di sviluppo (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-httpserver`, `ruff`, `mypy`, `import-linter`

## 3. Utilizzo

### Modalità interattiva (TUI)

Consigliata per l'uso quotidiano — avviata senza argomenti:

```bash
./omega-track.sh
```
se hai creato l'alias, digita semplicemente `track` nel terminale:
```bash
track
```

Percorso: schermata iniziale (si chiude con un tasto o un clic) → menu principale (Obiettivi / Tracker / Risultati / Cronologia / Dashboard / GeoIP / Fonti con chiave / Impostazioni / Aiuto) → inserimento o selezione dell'obiettivo (conferma esplicita se non fissato) e scelta dei moduli di raccolta → osservazione (indicatore e svolgimento delle operazioni in diretta, annullabile) → risultati dettagliati per scheda (Identità/DNS/Rete / ASN/NeoTrace/Certificati/Archivi/Relazioni/Diagnostica, esportazione) → cronologia/dashboard/impostazioni dal menu principale. L'adattamento al terminale (colori, dimensioni, degradazione strutturale) è automatico.

#### Scorciatoie da tastiera

| Tasto | Azione |
|---|---|
| `↑` / `↓` | Navigare tra gli elementi di una schermata |
| `Tab` / `Maiusc+Tab` | Navigare tra i campi di un modulo |
| `Esc` | Tornare alla schermata precedente (conferma di uscita sulla schermata iniziale) |
| `t` | Tema successivo (applicato subito, senza conferma) |
| `r` | Aggiornare il rilevamento del terminale |
| `a` | Mostrare l'aiuto |
| `q` | Uscire (con conferma) |

### Lingue dell'interfaccia

L'interfaccia è disponibile in 17 lingue: francese, inglese, spagnolo, portoghese (Brasile), italiano, tedesco, olandese, polacco, russo, cinese semplificato, vietnamita, thailandese, indonesiano, giapponese, coreano, hindi e arabo. La scelta si fa nelle Impostazioni («Langue / Language») e si applica dopo il riavvio dell'interfaccia; la variabile `OMEGA_TRACK_LANG` (ad esempio `OMEGA_TRACK_LANG=it ./omega-track.sh`) impone una lingua per una sessione. Avviato da omega-suite, omega-track adotta la lingua della suite. Su una console testuale Linux (TTY), le lingue con scrittura non latina vengono mostrate in inglese per la sessione. La riga di comando resta in francese.

### Contatti e supporto

L'aiuto (tasto `a`) propone una schermata **Contatti e supporto**: *Offrire un caffè* (pagina PayPal dello sviluppatore), *Contattare il supporto* (indirizzo e-mail e modulo di contatto del sito, mostrati in chiaro), *Dichiararmi utente (anonimo)* e *Verifica aggiornamenti*. La dichiarazione è volontaria, disattivata per impostazione predefinita e inviata una sola volta: serve solo a contare gli utenti e, se lo si desidera, il loro continente o paese (elenchi chiusi, mai testo libero). Invia una chiave estratta a caso, il nome del software (`omega-track`) e la sua versione; mai un nome, un nome di macchina, un'impostazione, un obiettivo o un risultato. L'indirizzo IP non viene registrato nelle dichiarazioni, ma, come per ogni visita, passa per i controlli di sicurezza e il registro del server di ricezione. Ritiro in qualsiasi momento dalla stessa schermata (*Non dichiararmi più*). La verifica degli aggiornamenti legge solo l'elenco delle versioni pubblicate sul sito, e mai senza un clic.

### Modalità scriptabile (CLI)

Qualsiasi sottocomando attiva la modalità CLI:

```bash
# Obiettivi
./omega-track.sh target add example.org --alias "sito vetrina" --tag prod
./omega-track.sh target list
./omega-track.sh target pin <target_id>

# Avviare e seguire un'osservazione
./omega-track.sh track run <target_id> --module dns --module rdap --module neotrace --authorize
./omega-track.sh track status <run_id>
./omega-track.sh track show <run_id>
./omega-track.sh track replay <run_id> --authorize

# Cronologia
./omega-track.sh history list --target <target_id> --status completed --since 2026-01-01

# Esportazione — 6 formati, 5 temi per l'HTML
./omega-track.sh export <run_id> --format html --theme omega-neon --redact contacts_only

# GeoIP
./omega-track.sh geoip status
./omega-track.sh geoip update --provider dbip

# Fonti di reputazione con chiave (divulgazione mostrata prima di qualsiasi salvataggio)
./omega-track.sh source list
./omega-track.sh source info virustotal
./omega-track.sh source configure virustotal <chiave_api>

# Impostazioni ed eliminazione
./omega-track.sh config show
./omega-track.sh cleanup preview --older-than 30
./omega-track.sh cleanup run --older-than 30 --yes

# Diagnostica locale (versioni, capacità, percorsi, stato GeoIP)
./omega-track.sh diagnostics
```

Ogni sottocomando accetta `--json` per un output rigorosamente leggibile dalle macchine.

#### Codici di uscita

| Codice | Significato |
|---:|---|
| `0` | Successo (osservazione terminata, `COMPLETED`) |
| `1` | Errore di validazione (obiettivo non valido, formato di esportazione sconosciuto, transizione di stato non valida, chiave API assente...) |
| `2` | Obiettivo non autorizzato (né fissato, né `--authorize`) |
| `3` | Risorsa non trovata o fonte non disponibile (obiettivo/esecuzione sconosciuti, download GeoIP fallito) |
| `4` | Osservazione parziale (`PARTIAL`) — non un fallimento, solo alcuni moduli sono andati a buon fine |
| `5` | Errore interno imprevisto |
| `130` | Interrotto dall'utente (`Ctrl+C`) |

### Formati di obiettivo accettati

```text
192.168.1.10                IPv4
2001:db8::1                 IPv6
example.org                 Dominio
```

## 4. Moduli di raccolta

| Modulo | Modalità di raccolta | Attivo per impostazione predefinita | Chiave richiesta |
|---|---|:---:|:---:|
| `dns` | Attivo leggero (risoluzione diretta) | sì | no |
| `reverse_dns` | Attivo leggero (PTR) | sì | no |
| `rdap` | Passivo pubblico | sì | no |
| `neotrace` | Attivo leggero (traceroute/tracepath) | sì | no |
| `certificate_transparency` | Passivo pubblico (`crt.sh`) | no | no |
| `archives` | Passivo pubblico (Wayback Machine) | no | no |
| `bgp` | Passivo pubblico (RIPEstat) | no | no |
| `virustotal` | Con chiave utente | no | sì (gratuita) |
| `hibp` | Con chiave utente | no | sì (**a pagamento** dal 2022) |

I primi quattro moduli formano la base dell'MVP (`dns`/`reverse_dns`/`rdap`/`neotrace`) e sono selezionati per impostazione predefinita nel modulo di avvio; i cinque successivi sono opzionali e vanno attivati esplicitamente. Una fonte senza chiave configurata non fa mai fallire l'osservazione: il modulo corrispondente passa semplicemente a `SKIPPED` («non eseguito»). Dettaglio per fonte, quote e licenze: `docs/DATA_SOURCES.md`.

## 5. Architettura

Omega-track è strutturato in **Clean Architecture** (domain / application / infrastructure / interfaces / ports / core / app / plugins), allineato al modello della suite `omega-` (vedi `omega-check`/`omega-fold`) e verificato da `import-linter` a ogni modifica.

```text
src/omega_track/
├── domain/          Logica di business pura (obiettivi, TrackRun/ModuleRun, findings, relazioni, profili...)
├── application/     Casi d'uso (commands/queries/orchestratori di fase/politiche)
├── ports/           Contratti attesi dall'applicazione (collettori, repository, esportatori...)
├── infrastructure/  Implementazioni concrete (dnspython/httpx/subprocess/maxminddb, SQLite, jinja2)
├── interfaces/      tui/ (Textual) e cli/ (scriptabile), a rigorosa parità funzionale
├── app/             Assemblaggio (DependencyContainer, bootstrap, ciclo di vita)
├── core/            Vocabolario trasversale (versioni, riesportazioni di omega-lib)
└── plugins/         Moduli opzionali a fonte unica (CT, archivi, BGP, VirusTotal, HIBP)
```

Regole di progettazione:
- `domain/` non fa mai rete né I/O; `infrastructure/` fa la rete e l'I/O, e non giudica mai.
- `interfaces/` visualizza e non contiene alcuna logica di business — CLI e TUI chiamano rigorosamente gli stessi casi d'uso.
- 1 modulo di raccolta = 1 fonte = 1 stato (`ModuleRun`): mai due fonti aggregate sotto un unico stato ambiguo.
- L'assenza di un singolo campo non è mai un errore; solo l'indisponibilità totale di una fonte provoca `SKIPPED`/`FAILED`.

## 6. Fonti di dati

| Fonte | Fornitore | Chiave | Modalità |
|---|---|:---:|---|
| DNS diretto/inverso | Resolver di sistema | no | Attivo leggero |
| RDAP | Bootstrap IANA → RIR/registrar | no | Passivo pubblico |
| Certificate Transparency | `crt.sh` (Sectigo) | no | Passivo pubblico |
| Archivi web | Wayback Machine (Internet Archive) | no | Passivo pubblico |
| BGP / annunci di rete | RIPEstat (RIPE NCC) | no | Passivo pubblico |
| GeoIP | DB-IP Lite (predefinito) o MaxMind GeoLite2 | no / sì | Offline (base locale) |
| NeoTrace | `traceroute`/`tracepath` locale | no | Attivo leggero |
| Reputazione | VirusTotal | sì (gratuita) | Con chiave |
| Reputazione | Have I Been Pwned | sì (a pagamento) | Con chiave |

Quota, licenza e ripiego esatti per ogni fonte: `docs/DATA_SOURCES.md`. Nessuna chiave API compare mai nei log, nelle esportazioni o nelle schermate di diagnostica.

## 7. Politica di fiducia

Ogni campo raccolto porta un livello tra i seguenti (condiviso con tutta la suite tramite `omega-lib`):

| Livello | Significato |
|---|---|
| `VERIFIED` | Fatto di protocollo osservato direttamente, non falsificabile dall'obiettivo (es.: risposta DNS diretta, misura traceroute locale). |
| `DECLARED` | Valore autodichiarato dalla fonte in un campo che controlla interamente (es.: dato RDAP mostrato dal registrar) — plausibile ma falsificabile a piacere. |
| `CORROBORATED` | Un valore `DECLARED` confermato da un indizio indipendente (es.: un dominio osservato in almeno due log Certificate Transparency distinti). |
| `INFERRED` | Dedotto da un pattern/euristica, senza dichiarazione esplicita (es.: ASN comune usato per suggerire una relazione, mai promosso automaticamente). |
| `UNKNOWN` | Nessun indizio utilizzabile, o attivamente nascosto dall'obiettivo. |

Il punteggio di fiducia complessivo di un'osservazione è un aiuto alla lettura, mai un verdetto di sicurezza.

## 8. Livelli di raccolta, autorizzazione e oscuramento

Ogni profilo rende esplicita la natura delle proprie azioni (`CollectionMode`):

- **Offline**: validazione dell'obiettivo, lettura GeoIP locale, correlazioni su dati già memorizzati, esportazioni — nessuna rete.
- **Passivo pubblico**: RDAP, DNS pubblico, CT log, archivi, BGP — al terzo viene trasmesso solo l'obiettivo interrogato, proprietà intrinseca del protocollo.
- **Attivo leggero**: risoluzione DNS, DNS inverso, traceroute — il resolver configurato sulla macchina e ogni router intermedio del percorso vedono la richiesta.
- **Con chiave utente**: fornitori che richiedono una chiave o applicano quote, attivati solo dopo configurazione esplicita e divulgazione mostrata (quota, dati inviati).

**Controllo di autorizzazione**: nessuna osservazione parte su un obiettivo non fissato senza conferma esplicita (`--authorize` nella CLI, casella di spunta nella TUI). Fissare un obiettivo lo autorizza in modo duraturo per le sue osservazioni future.

**Oscuramento delle esportazioni**: ogni esportazione accetta una politica (`none`/`contacts_only`/`sensitive_only`/`strict`) che nasconde i campi sensibili (in particolare i contatti RDAP) nel risultato esportato — l'archiviazione locale, invece, conserva sempre il dato completo raccolto. Dettaglio: `docs/PRIVACY.md`.

## 9. Compatibilità dei terminali

La TUI (Textual) rileva automaticamente le capacità del terminale (emulatore, dimensioni) e adatta di conseguenza il proprio foglio di stile strutturale (`complete`/`standard`/`reduced`/`mono`), senza flag manuale. La modalità CLI resta sempre in testo semplice, indipendente dal terminale. Politica condivisa da tutta la suite `omega-` (`omega-lib`, `terminal/policies.py`).

### Profilo secondo l'emulatore rilevato

| Emulatore | Profilo iniziale |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, SSH moderno | `reduced` |
| TTY Linux, SSH legacy | `mono` |
| Emulatore non riconosciuto | `reduced` (ripiego predefinito) |

### Profilo secondo le dimensioni del terminale

| Dimensione minima (colonne × righe) | Tetto di profilo |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| al di sotto | `mono` |

Il profilo finale adottato è **il più restrittivo dei due** (emulatore e dimensioni). Si può aggiornare in diretta con il tasto `r`.

## 10. Esportazioni

I report Markdown e HTML sono scritti nella lingua scelta nelle Impostazioni («Lingua delle esportazioni», per impostazione predefinita quella dell'interfaccia); JSON, CSV, DOT e Mermaid restano dati e non vengono tradotti. I report vengono generati in `var/exports/` per impostazione predefinita (percorso di esecuzione ancorato alla cartella del progetto, `$OMEGA_TRACK_VAR_DIR` per sovrascriverlo), o nel percorso indicato (`--output` nella CLI, finestra di dialogo nella TUI). Nome di file con data e ora e univoco: `{data_ora}_{obiettivo}_{id_breve}.{estensione}`.

| Formato | Contenuto |
|---|---|
| `json` | Struttura completa dell'osservazione (`TrackRun` + findings + relazioni), fonte di verità, rigorosamente serializzabile in JSON |
| `markdown` | Report umano compatto, leggibile fuori dal terminale |
| `html` | Report web autonomo, 5 temi a scelta (`--theme`), grafo delle relazioni Mermaid incorporato inline |
| `csv` | Una tabella per categoria di finding |
| `dot` | Grafo delle relazioni Graphviz, file autonomo |
| `mermaid` | Grafo delle relazioni Mermaid, file autonomo |

## 11. Cronologia, eliminazione e riesecuzione

Ogni osservazione viene salvata (SQLite, `var/db/omega-track.db`): cronologia consultabile e filtrabile (obiettivo/stato/tag/periodo), dashboard di sintesi (ripartizione per stato, affidabilità per modulo, tipologia degli ultimi findings), riesecuzione di un'osservazione sullo stesso obiettivo senza reinserirlo (`track replay`), ed eliminazione della cronologia vecchia con anteprima sistematica prima di qualsiasi cancellazione (`cleanup preview` prima di `cleanup run --yes`).

## 12. Test

```bash
source .venv/bin/activate
lint-imports        # verifica la Dependency Rule
pytest -q           # 485 test
ruff check .
mypy src
```

Struttura: `tests/unit/` (dominio e applicazione, senza I/O reale), `tests/integration/` (SQLite/file reali, server HTTP fittizio `pytest-httpserver`, TUI headless tramite l'API `Pilot` di Textual).

## 13. Fuori perimetro

- Cronologia WHOIS/DNS completa, passive DNS commerciale
- Ricerca di persone, social network, pastebin/leak
- Scansione delle porte, identificazione di servizi e banner (`omega-check`)
- Controlli HTTP/HTTPS, header, TLS (`omega-scan`)
- Crawl e attraversamento dell'architettura (`omega-deep`/`omega-fold`)
- Test di carico (`omega-stress`), fuzzing (`omega-fuzz`)
- Mappa TUI interattiva (riservata al report HTML esportato)
- MTR continuo, multisonda e da più punti di osservazione
- Modalità batch/periodica/sorveglianza ricorrente di un obiettivo — un `TrackRun` resta sempre un'azione manuale esplicita
- Motore di migrazione dello schema SQLite (schema additivo, stessa pratica del resto della suite)

---

> Omega-track — Osservare, correlare, qualificare, riferire.
> Un'identità digitale con una fiducia esplicita su ogni dato, mai una certezza mascherata.
