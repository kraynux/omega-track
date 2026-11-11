<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Licencja MIT (zobacz plik LICENSE) -->
<div align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/assets/omega-track.png" alt="Omega-Track" width="512">
</div>

# 🛰️ OMEGA-TRACK

**Profilowanie tożsamości cyfrowej i obserwacja ścieżki sieciowej**

> Opracowane przez [kraynux](https://github.com/kraynux) dla [Omega-Server](https://kraynux.snake-mackarel.ts.net)   

Oficjalna strona: [OMEGA-TRACK](https://kraynux.snake-mackarel.ts.net/omega-track/) &nbsp; Podgląd: [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-track/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](../../../LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 Interfejs i eksportowane raporty dostępne w **17 językach** — zobacz [Języki interfejsu](#języki-interfejsu).  
**Języki:**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](../../../README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](../en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](../es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](../pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](../it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](../de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](../nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](../ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](../zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](../vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](../th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](../id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](../ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](../ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](../hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](../ar/README.md)

---

**Omega-track** to narzędzie TUI + CLI, które na podstawie adresu IP, adresu IPv6 lub domeny buduje możliwie najpełniejszą tożsamość cyfrową: kto odpowiada za tym celem, jak do niego dotrzeć i z jakim poziomem zaufania każdą informację można uznać za pewną. To narzędzie pakietu `omega-`, zbudowane zgodnie z Clean Architecture — szczegóły w `docs/PRODUCT_SCOPE.md` i `docs/DATA_SOURCES.md`.

<p align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/pl/omega-track/A.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/pl/omega-track/B.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/pl/omega-track/C.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/translation/pl/omega-track/D.png" width="24%" />
</p>

## 1. Wizja i zakres

Omega-track odpowiada na dwa pytania: „kim jest ten cel?” (tożsamość RDAP/DNS/certyfikaty/reputacja) i „jak do niego dotrzeć?” (ścieżka sieciowa NeoTrace, GeoIP, ASN). Uzupełnia `omega-check` (ekspozycja sieciowa), `omega-scan` (higiena HTTP/HTTPS) i `omega-deep` (ograniczona analiza architektury), nie powielając ich.

### Co robi Omega-track

- Przyjmuje cel w postaci IP, IPv6 lub nazwy domeny, zapisany i ewentualnie przypięty (trwała autoryzacja).
- Gromadzi informacje publiczne, pasywne lub jawnie włączone przez profil (RDAP, DNS, Certificate Transparency, archiwa Wayback, ogłoszenia BGP).
- Wykonuje wzbogacony traceroute w stylu NeoTrace (jedyne aktywne działanie sieciowe w rdzeniu produktu).
- Wzbogaca każdy istotny adres IP za pomocą lokalnej bazy GeoIP (DB-IP Lite bez klucza, opcjonalnie MaxMind GeoLite2 z kluczem).
- Odpytuje, z kluczem dostarczonym przez użytkownika, źródła reputacji (VirusTotal, HIBP), zawsze ujawniając limit i wysyłane dane przed jakąkolwiek aktywacją.
- Łączy zaobserwowane dane w spójny profil, z jawnym poziomem zaufania dla każdej danej.
- Przechowuje cele, uruchomienia, wyniki, błędy i eksporty lokalnie (SQLite, `./var/`).
- Zapewnia TUI Textual i CLI ściśle równoważne funkcjonalnie.
- Tworzy raporty HTML (5 motywów, wbudowany graf relacji Mermaid), JSON, Markdown, CSV oraz samodzielne pliki DOT i Mermaid.

### Czego Omega-track nie robi

| Funkcja | Odpowiedzialne narzędzie |
|---|---|
| Skanowanie portów, identyfikacja usług i banerów | OMEGA-CHECK |
| Kontrole HTTP/HTTPS, nagłówki, TLS, higiena sieciowa | OMEGA-SCAN |
| Crawl, przechodzenie architektury i schodzenie do powiązanych celów | OMEGA-DEEP |
| Zdalny crawl strona po stronie (linki, pliki) | OMEGA-FOLD |
| Testy obciążeniowe | OMEGA-STRESS |
| Fuzzing i testy odporności aplikacji | OMEGA-FUZZ |

Do unikania, także poza MVP: brute-force subdomen, skanowanie portów, crawl sieciowy, inwazyjne zbieranie danych osobowych, automatyzacja obchodzenia zabezpieczeń, kruchy scraping platform wymagających uwierzytelnienia, wyszukiwanie osób/sieci społecznościowych/pastebinów-wycieków, okresowe/cykliczne monitorowanie celu (zobacz `docs/PRODUCT_SCOPE.md` §7 "Celowo odłożone").

### Ostrzeżenie o autoryzowanym użyciu

Omega-track to narzędzie do dochodzeń sieciowych przeznaczone do legalnego użytku: audytu własnej infrastruktury, reagowania na incydenty, obserwacji obszaru, który masz prawo dokumentować. Zbieranie pozostaje niemal całkowicie pasywne/publiczne (RDAP, DNS, logi CT — dane, które cel lub jego rejestrator już udostępnia publicznie), z wyjątkiem traceroute (lekko aktywnego, zawsze widocznego w używanym profilu).

**Żadna obserwacja nie rusza na nieprzypiętym celu bez jawnego potwierdzenia** (`--authorize` w CLI, potwierdzenie w TUI). Tylko Ty odpowiadasz za sprawdzenie, czy Twoje użycie jest zgodne z obowiązującym prawem i warunkami korzystania z odpytywanych źródeł zewnętrznych.

## 2. Instalacja

### Wymagania wstępne

- Python 3.10+
- Połączenie z Internetem, dla zależności i odpytywanych źródeł pasywnych
- Zainstalowany `traceroute` lub `tracepath` (moduł NeoTrace) — w razie braku następuje czyste ograniczenie funkcji, reszta narzędzia działa normalnie

### Instalacja

```bash
[ -d omega-track ] && echo "ℹ️ Już rozpakowane tutaj, krok pominięty." || tar -xzf omega-track.tar.gz
cd omega-track/
chmod +x install.sh
./install.sh
```

`install.sh`:

1. Tworzy środowisko wirtualne `.venv`, jeśli jeszcze nie istnieje.
2. Instaluje zależności (`pip install -e .`, `pyproject.toml` pozostaje jedynym źródłem prawdy).
3. Nadaje plikom `omega-track.sh` i `install.sh` prawo wykonywania.
4. Dodaje alias `track` do `~/.bashrc` i `~/.zshrc` (bez duplikatu, jeśli już istnieje).

### Zależności

Zadeklarowane w `pyproject.toml` (bez osobnego `requirements.txt`):
- `omega-lib`: współdzielona biblioteka pakietu (`ConfidenceLevel`, motywy, wykrywanie terminala)
- `textual`: interfejs TUI, motywy, automatyczne dopasowanie do terminala
- `dnspython`: bezpośrednie i odwrotne rozwiązywanie DNS
- `httpx`: sondy RDAP/CT/archiwa/BGP/VirusTotal/HIBP
- `maxminddb`: odczyt lokalnych baz GeoIP (DB-IP Lite, MaxMind GeoLite2)
- `jinja2`: szablony dla eksportu HTML
- Zależności deweloperskie (`pip install -e ".[dev]"`): `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-httpserver`, `ruff`, `mypy`, `import-linter`

## 3. Użycie

### Tryb interaktywny (TUI)

Zalecany do codziennego użytku — uruchamiany bez argumentów:

```bash
./omega-track.sh
```
jeśli utworzono alias, wystarczy wpisać `track` w terminalu:
```bash
track
```

Przebieg: ekran startowy (zamyka się po naciśnięciu klawisza lub kliknięciu) → menu główne (Cele / Tracker / Wyniki / Historia / Pulpit / GeoIP / Źródła z kluczem / Ustawienia / Pomoc) → wpisanie lub wybór celu (jawne potwierdzenie, jeśli nie jest przypięty) i wybór modułów zbierania → obserwacja (wskaźnik i przebieg operacji na żywo, z możliwością anulowania) → szczegółowe wyniki w kartach (Tożsamość/DNS/Sieć / ASN/NeoTrace/Certyfikaty/Archiwa/Powiązania/Diagnostyka, eksport) → historia/pulpit/ustawienia z menu głównego. Dopasowanie do terminala (kolory, rozmiar, strukturalne uproszczenie) jest automatyczne.

#### Skróty klawiszowe

| Klawisz | Działanie |
|---|---|
| `↑` / `↓` | Poruszanie się między elementami ekranu |
| `Tab` / `Shift+Tab` | Poruszanie się między polami formularza |
| `Esc` | Powrót do poprzedniego ekranu (potwierdzenie wyjścia na ekranie startowym) |
| `t` | Następny motyw (stosowany od razu, bez potwierdzenia) |
| `r` | Odświeżenie wykrywania terminala |
| `a` | Wyświetlenie pomocy |
| `q` | Wyjście (z potwierdzeniem) |

### Języki interfejsu

Interfejs jest dostępny w 17 językach: francuskim, angielskim, hiszpańskim, portugalskim (Brazylia), włoskim, niemieckim, niderlandzkim, polskim, rosyjskim, chińskim uproszczonym, wietnamskim, tajskim, indonezyjskim, japońskim, koreańskim, hindi i arabskim. Wybór odbywa się w Ustawieniach („Langue / Language”) i obowiązuje po ponownym uruchomieniu interfejsu; zmienna `OMEGA_TRACK_LANG` (na przykład `OMEGA_TRACK_LANG=pl ./omega-track.sh`) wymusza język na czas jednej sesji. Uruchomiony z omega-suite, omega-track przejmuje język pakietu. Na tekstowej konsoli Linuksa (TTY) języki o piśmie innym niż łacińskie są wyświetlane po angielsku przez całą sesję. Wiersz poleceń pozostaje po francusku.

### Kontakt i wsparcie

Pomoc (klawisz `a`) oferuje ekran **Kontakt i wsparcie**: *Postaw kawę* (strona PayPal dewelopera), *Skontaktuj się ze wsparciem* (adres e-mail i formularz kontaktowy strony, wyświetlane jawnie), *Zgłoś mnie jako użytkownika (anonimowo)* oraz *Sprawdź aktualizacje*. Zgłoszenie jest dobrowolne, domyślnie wyłączone i wysyłane tylko raz: służy wyłącznie do liczenia użytkowników oraz, jeśli tego chcesz, ich kontynentu lub kraju (zamknięte listy, nigdy dowolny tekst). Wysyła losowo wygenerowany klucz, nazwę programu (`omega-track`) i jego wersję; nigdy imienia i nazwiska, nazwy maszyny, ustawienia, celu ani wyniku. Adres IP nie jest zapisywany w zgłoszeniach, ale — jak przy każdej wizycie — przechodzi przez kontrole bezpieczeństwa i dziennik serwera odbiorczego. Wycofanie w dowolnym momencie z tego samego ekranu (*Nie zgłaszaj mnie więcej*). Sprawdzanie aktualizacji odczytuje jedynie listę wersji opublikowanych na stronie, i nigdy bez kliknięcia.

### Tryb skryptowy (CLI)

Każde podpolecenie włącza tryb CLI:

```bash
# Cele
./omega-track.sh target add example.org --alias "strona wizytówka" --tag prod
./omega-track.sh target list
./omega-track.sh target pin <target_id>

# Uruchomienie i śledzenie obserwacji
./omega-track.sh track run <target_id> --module dns --module rdap --module neotrace --authorize
./omega-track.sh track status <run_id>
./omega-track.sh track show <run_id>
./omega-track.sh track replay <run_id> --authorize

# Historia
./omega-track.sh history list --target <target_id> --status completed --since 2026-01-01

# Eksport — 6 formatów, 5 motywów dla HTML
./omega-track.sh export <run_id> --format html --theme omega-neon --redact contacts_only

# GeoIP
./omega-track.sh geoip status
./omega-track.sh geoip update --provider dbip

# Źródła reputacji z kluczem (ujawnienie wyświetlane przed jakimkolwiek zapisem)
./omega-track.sh source list
./omega-track.sh source info virustotal
./omega-track.sh source configure virustotal <klucz_api>

# Ustawienia i czyszczenie
./omega-track.sh config show
./omega-track.sh cleanup preview --older-than 30
./omega-track.sh cleanup run --older-than 30 --yes

# Lokalna diagnostyka (wersje, możliwości, ścieżki, stan GeoIP)
./omega-track.sh diagnostics
```

Każde podpolecenie przyjmuje `--json`, aby uzyskać wyjście ściśle czytelne maszynowo.

#### Kody wyjścia

| Kod | Znaczenie |
|---:|---|
| `0` | Sukces (obserwacja zakończona, `COMPLETED`) |
| `1` | Błąd walidacji (nieprawidłowy cel, nieznany format eksportu, nieprawidłowe przejście stanu, brak klucza API...) |
| `2` | Cel nieautoryzowany (ani przypięty, ani `--authorize`) |
| `3` | Zasób nie znaleziony lub źródło niedostępne (nieznany cel/uruchomienie, nieudane pobranie GeoIP) |
| `4` | Częściowa obserwacja (`PARTIAL`) — nie porażka, powiodły się tylko niektóre moduły |
| `5` | Nieoczekiwany błąd wewnętrzny |
| `130` | Przerwane przez użytkownika (`Ctrl+C`) |

### Akceptowane formaty celu

```text
192.168.1.10                IPv4
2001:db8::1                 IPv6
example.org                 Domena
```

## 4. Moduły zbierania

| Moduł | Tryb zbierania | Domyślnie aktywny | Wymagany klucz |
|---|---|:---:|:---:|
| `dns` | Lekko aktywny (rozwiązywanie bezpośrednie) | tak | nie |
| `reverse_dns` | Lekko aktywny (PTR) | tak | nie |
| `rdap` | Publiczny pasywny | tak | nie |
| `neotrace` | Lekko aktywny (traceroute/tracepath) | tak | nie |
| `certificate_transparency` | Publiczny pasywny (`crt.sh`) | nie | nie |
| `archives` | Publiczny pasywny (Wayback Machine) | nie | nie |
| `bgp` | Publiczny pasywny (RIPEstat) | nie | nie |
| `virustotal` | Z kluczem użytkownika | nie | tak (darmowy) |
| `hibp` | Z kluczem użytkownika | nie | tak (**płatny** od 2022) |

Pierwsze cztery moduły tworzą bazę MVP (`dns`/`reverse_dns`/`rdap`/`neotrace`) i są domyślnie zaznaczone w formularzu uruchamiania; pięć kolejnych jest opcjonalnych i trzeba je jawnie włączyć. Źródło bez skonfigurowanego klucza nigdy nie powoduje niepowodzenia obserwacji: odpowiedni moduł po prostu przechodzi w `SKIPPED` („nie wykonano”). Szczegóły dla każdego źródła, limity i licencje: `docs/DATA_SOURCES.md`.

## 5. Architektura

Omega-track jest zbudowany zgodnie z **Clean Architecture** (domain / application / infrastructure / interfaces / ports / core / app / plugins), dopasowany do szablonu pakietu `omega-` (zobacz `omega-check`/`omega-fold`) i sprawdzany przez `import-linter` przy każdej zmianie.

```text
src/omega_track/
├── domain/          Czysta logika biznesowa (cele, TrackRun/ModuleRun, findings, relacje, profile...)
├── application/     Przypadki użycia (commands/queries/orkiestratory faz/polityki)
├── ports/           Kontrakty oczekiwane przez aplikację (kolektory, repozytoria, eksportery...)
├── infrastructure/  Konkretne implementacje (dnspython/httpx/subprocess/maxminddb, SQLite, jinja2)
├── interfaces/      tui/ (Textual) i cli/ (skryptowe), ze ścisłą równoważnością funkcji
├── app/             Składanie (DependencyContainer, bootstrap, cykl życia)
├── core/            Wspólne słownictwo (wersje, reeksporty omega-lib)
└── plugins/         Opcjonalne moduły z jednym źródłem (CT, archiwa, BGP, VirusTotal, HIBP)
```

Zasady projektowe:
- `domain/` nigdy nie korzysta z sieci ani I/O; `infrastructure/` obsługuje sieć i I/O, ale nigdy nie ocenia.
- `interfaces/` wyświetla i nie zawiera żadnej logiki biznesowej — CLI i TUI wywołują ściśle te same przypadki użycia.
- 1 moduł zbierania = 1 źródło = 1 status (`ModuleRun`): nigdy dwa źródła połączone pod jednym niejednoznacznym statusem.
- Brak pojedynczego pola nigdy nie jest błędem; tylko całkowita niedostępność źródła powoduje `SKIPPED`/`FAILED`.

## 6. Źródła danych

| Źródło | Dostawca | Klucz | Tryb |
|---|---|:---:|---|
| DNS bezpośredni/odwrotny | Resolver systemowy | nie | Lekko aktywny |
| RDAP | Bootstrap IANA → RIR/rejestrator | nie | Publiczny pasywny |
| Certificate Transparency | `crt.sh` (Sectigo) | nie | Publiczny pasywny |
| Archiwa sieciowe | Wayback Machine (Internet Archive) | nie | Publiczny pasywny |
| BGP / ogłoszenia sieciowe | RIPEstat (RIPE NCC) | nie | Publiczny pasywny |
| GeoIP | DB-IP Lite (domyślnie) lub MaxMind GeoLite2 | nie / tak | Offline (lokalna baza) |
| NeoTrace | Lokalny `traceroute`/`tracepath` | nie | Lekko aktywny |
| Reputacja | VirusTotal | tak (darmowy) | Z kluczem |
| Reputacja | Have I Been Pwned | tak (płatny) | Z kluczem |

Dokładny limit, licencja i rozwiązanie zastępcze dla każdego źródła: `docs/DATA_SOURCES.md`. Żaden klucz API nigdy nie pojawia się w logach, eksportach ani na ekranach diagnostycznych.

## 7. Polityka zaufania

Każde zebrane pole ma jeden z poniższych poziomów (wspólny dla całego pakietu przez `omega-lib`):

| Poziom | Znaczenie |
|---|---|
| `VERIFIED` | Bezpośrednio zaobserwowany fakt protokołu, którego cel nie może sfałszować (np. bezpośrednia odpowiedź DNS, lokalny pomiar traceroute). |
| `DECLARED` | Wartość samodzielnie podana przez źródło w polu, które w pełni kontroluje (np. dane RDAP wyświetlane przez rejestratora) — wiarygodna, ale dowolnie fałszowalna. |
| `CORROBORATED` | Wartość `DECLARED` potwierdzona niezależną poszlaką (np. domena zaobserwowana w co najmniej dwóch różnych logach Certificate Transparency). |
| `INFERRED` | Wywnioskowana ze wzorca/heurystyki, bez jawnej deklaracji (np. wspólny ASN sugerujący powiązanie, nigdy automatycznie podnoszony). |
| `UNKNOWN` | Brak użytecznej poszlaki lub aktywnie ukryte przez cel. |

Ogólny wynik zaufania obserwacji to pomoc w odczycie, nigdy werdykt bezpieczeństwa.

## 8. Poziomy zbierania, autoryzacja i redakcja

Każdy profil jawnie określa charakter swoich działań (`CollectionMode`):

- **Offline**: walidacja celu, lokalny odczyt GeoIP, korelacje na już zapisanych danych, eksporty — bez sieci.
- **Publiczny pasywny**: RDAP, publiczny DNS, logi CT, archiwa, BGP — stronie trzeciej przekazywany jest tylko odpytywany cel, co wynika z samego protokołu.
- **Lekko aktywny**: rozwiązywanie DNS, odwrotny DNS, traceroute — resolver skonfigurowany na maszynie i każdy pośredni router na ścieżce widzą zapytanie.
- **Z kluczem użytkownika**: dostawcy wymagający klucza lub stosujący limity, włączani tylko po jawnej konfiguracji i wyświetlonym ujawnieniu (limit, wysyłane dane).

**Ochrona autoryzacji**: żadna obserwacja nie rusza na nieprzypiętym celu bez jawnego potwierdzenia (`--authorize` w CLI, pole wyboru w TUI). Przypięcie celu autoryzuje go trwale dla przyszłych obserwacji.

**Redakcja eksportów**: każdy eksport przyjmuje politykę (`none`/`contacts_only`/`sensitive_only`/`strict`), która maskuje pola wrażliwe (zwłaszcza kontakty RDAP) w eksportowanym wyniku — lokalny magazyn zawsze zachowuje pełne zebrane dane. Szczegóły: `docs/PRIVACY.md`.

## 9. Zgodność z terminalami

TUI (Textual) automatycznie wykrywa możliwości terminala (emulator, rozmiar) i odpowiednio dopasowuje swój strukturalny arkusz stylów (`complete`/`standard`/`reduced`/`mono`), bez ręcznej flagi. Tryb CLI zawsze pozostaje zwykłym tekstem, niezależnym od terminala. Polityka wspólna dla całego pakietu `omega-` (`omega-lib`, `terminal/policies.py`).

### Profil według wykrytego emulatora

| Emulator | Profil początkowy |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, nowoczesny SSH | `reduced` |
| TTY Linuksa, starszy SSH | `mono` |
| Nierozpoznany emulator | `reduced` (domyślne rozwiązanie zastępcze) |

### Profil według rozmiaru terminala

| Minimalny rozmiar (kolumny × wiersze) | Pułap profilu |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| poniżej | `mono` |

Ostatecznie wybrany profil to **bardziej restrykcyjny z dwóch** (emulator i rozmiar). Można go odświeżyć na żywo klawiszem `r`.

## 10. Eksporty

Raporty Markdown i HTML są pisane w języku wybranym w Ustawieniach („Język eksportów”, domyślnie język interfejsu); JSON, CSV, DOT i Mermaid pozostają danymi i nie są tłumaczone. Raporty są domyślnie generowane w `var/exports/` (ścieżka wykonawcza zakotwiczona w folderze projektu, `$OMEGA_TRACK_VAR_DIR`, aby ją nadpisać) lub pod wskazaną ścieżką (`--output` w CLI, okno dialogowe w TUI). Unikalna nazwa pliku ze znacznikiem czasu: `{znacznik_czasu}_{cel}_{krotki_id}.{rozszerzenie}`.

| Format | Zawartość |
|---|---|
| `json` | Pełna struktura obserwacji (`TrackRun` + findings + relacje), źródło prawdy, ściśle serializowalna do JSON |
| `markdown` | Zwięzły raport dla ludzi, czytelny poza terminalem |
| `html` | Samodzielny raport sieciowy, 5 motywów do wyboru (`--theme`), graf relacji Mermaid wbudowany inline |
| `csv` | Jedna tabela na kategorię findingów |
| `dot` | Graf relacji Graphviz, samodzielny plik |
| `mermaid` | Graf relacji Mermaid, samodzielny plik |

## 11. Historia, czyszczenie i ponowne uruchomienie

Każda obserwacja jest zapisywana (SQLite, `var/db/omega-track.db`): historia do przeglądania i filtrowania (cel/status/tag/okres), podsumowujący pulpit (podział według statusu, niezawodność modułów, typologia ostatnich findingów), ponowne uruchomienie obserwacji na tym samym celu bez ponownego wpisywania (`track replay`) i czyszczenie starej historii z systematycznym podglądem przed każdym usunięciem (`cleanup preview` przed `cleanup run --yes`).

## 12. Testy

```bash
source .venv/bin/activate
lint-imports        # sprawdza Dependency Rule
pytest -q           # 485 testów
ruff check .
mypy src
```

Struktura: `tests/unit/` (domena i aplikacja, bez prawdziwego I/O), `tests/integration/` (prawdziwy SQLite/pliki, fikcyjny serwer HTTP `pytest-httpserver`, TUI bez okna przez API `Pilot` z Textual).

## 13. Poza zakresem

- Pełna historia WHOIS/DNS, komercyjny passive DNS
- Wyszukiwanie osób, sieci społecznościowych, pastebinów/wycieków
- Skanowanie portów, identyfikacja usług i banerów (`omega-check`)
- Kontrole HTTP/HTTPS, nagłówki, TLS (`omega-scan`)
- Crawl i przechodzenie architektury (`omega-deep`/`omega-fold`)
- Testy obciążeniowe (`omega-stress`), fuzzing (`omega-fuzz`)
- Interaktywna mapa w TUI (zarezerwowana dla eksportowanego raportu HTML)
- Ciągły MTR, wiele sond i wiele punktów obserwacji
- Tryb wsadowy/okresowy/cykliczne monitorowanie celu — `TrackRun` zawsze pozostaje jawnym działaniem ręcznym
- Silnik migracji schematu SQLite (schemat addytywny, ta sama praktyka co w reszcie pakietu)

---

> Omega-track — Obserwować, korelować, kwalifikować, raportować.
> Tożsamość cyfrowa z jawnym zaufaniem do każdej danej, nigdy zamaskowana pewność.
