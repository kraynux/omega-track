<!-- Copyright (c) 2026 kraynux - kraynux@proton.me - Licence MIT (voir fichier LICENSE) -->
<div align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/assets/omega-track.png" alt="Omega-Track" width="512">
</div>

# 🛰️ OMEGA-TRACK

**Profilage d'identité numérique et observation de chemin réseau**

> Élaboré par [kraynux](https://github.com/kraynux) pour [Omega-Server](https://kraynux.snake-mackarel.ts.net)   

Page officielle : [OMEGA-TRACK](https://kraynux.snake-mackarel.ts.net/omega-track/) &nbsp; Aperçu : [Screenshots](https://kraynux.snake-mackarel.ts.net/omega-track/screenshots/)  

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform](https://img.shields.io/badge/Platform-Linux-informational.svg)](https://www.linux.org/)
[![Interface](https://img.shields.io/badge/Interface-TUI%20%2B%20Rich-cyan.svg)](https://github.com/Textualize/rich)

🌐 Interface et rapports exportés disponibles en **17 langues** — voir [Langues de l'interface](#langues-de-linterface).  
**Langues :**  
<img src="https://flagcdn.com/w20/fr.png" alt="Français" style="height:14px;"> [Français](README.md) · <img src="https://flagcdn.com/w20/gb.png" alt="English" style="height:14px;"> [English](docs/translation/en/README.md) · <img src="https://flagcdn.com/w20/es.png" alt="Español" style="height:14px;"> [Español](docs/translation/es/README.md) · <img src="https://flagcdn.com/w20/br.png" alt="Português (Brasil)" style="height:14px;"> [Português (Brasil)](docs/translation/pt-BR/README.md) · <img src="https://flagcdn.com/w20/it.png" alt="Italiano" style="height:14px;"> [Italiano](docs/translation/it/README.md) · <img src="https://flagcdn.com/w20/de.png" alt="Deutsch" style="height:14px;"> [Deutsch](docs/translation/de/README.md) · <img src="https://flagcdn.com/w20/nl.png" alt="Nederlands" style="height:14px;"> [Nederlands](docs/translation/nl/README.md) · <img src="https://flagcdn.com/w20/pl.png" alt="Polski" style="height:14px;"> [Polski](docs/translation/pl/README.md) · <img src="https://flagcdn.com/w20/ru.png" alt="Русский" style="height:14px;"> [Русский](docs/translation/ru/README.md) · <img src="https://flagcdn.com/w20/cn.png" alt="中文" style="height:14px;"> [中文](docs/translation/zh-CN/README.md) · <img src="https://flagcdn.com/w20/vn.png" alt="Tiếng Việt" style="height:14px;"> [Tiếng Việt](docs/translation/vi/README.md) · <img src="https://flagcdn.com/w20/th.png" alt="ไทย" style="height:14px;"> [ไทย](docs/translation/th/README.md) · <img src="https://flagcdn.com/w20/id.png" alt="Bahasa Indonesia" style="height:14px;"> [Bahasa Indonesia](docs/translation/id/README.md) · <img src="https://flagcdn.com/w20/jp.png" alt="日本語" style="height:14px;"> [日本語](docs/translation/ja/README.md) · <img src="https://flagcdn.com/w20/kr.png" alt="한국어" style="height:14px;"> [한국어](docs/translation/ko/README.md) · <img src="https://flagcdn.com/w20/in.png" alt="हिन्दी" style="height:14px;"> [हिन्दी](docs/translation/hi/README.md) · <img src="https://flagcdn.com/w20/ae.png" alt="العربية" style="height:14px;"> [العربية](docs/translation/ar/README.md)

---

**Omega-track** est un outil TUI + CLI qui construit, à partir d'une IP, IPv6 ou d'un domaine, l'identité numérique la plus complète possible : qui répond derrière cette cible, comment y arrive-t-on, et avec quel niveau de confiance chaque information peut être tenue pour acquise. Outil de la suite `omega-`, structuré en Clean Architecture — voir `docs/PRODUCT_SCOPE.md` et `docs/DATA_SOURCES.md` pour le détail complet.

<p align="center">
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/assets/omega-track/A.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/assets/omega-track/B.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/assets/omega-track/C.png" width="24%" />
  <img src="https://raw.githubusercontent.com/kraynux/kraynux/refs/heads/main/docs/assets/omega-track/D.png" width="24%" />
</p>

## 1. Vision et périmètre

Omega-track répond à deux questions : « qui est cette cible ? » (identité RDAP/DNS/certificats/réputation) et « comment y arrive-t-on ? » (chemin réseau NeoTrace, GeoIP, ASN). Il complète `omega-check` (exposition réseau), `omega-scan` (hygiène HTTP/HTTPS) et `omega-deep` (analyse d'architecture bornée), sans les dupliquer.

### Ce que fait Omega-track

- Accepte une cible IP, IPv6 ou nom de domaine, enregistrée et éventuellement épinglée (autorisation durable).
- Centralise des renseignements publics, passifs ou explicitement activés par le profil (RDAP, DNS, Certificate Transparency, archives Wayback, annonces BGP).
- Exécute un traceroute enrichi de type NeoTrace (la seule action réseau active du cœur du produit).
- Enrichit chaque IP pertinente au moyen d'une base GeoIP locale (DB-IP Lite sans clé, MaxMind GeoLite2 en option avec clé).
- Interroge, sur clé fournie par l'utilisateur, des sources de réputation (VirusTotal, HIBP), avec divulgation systématique (quota, données envoyées) avant toute activation.
- Met en relation les données observées afin de former un profil cohérent, avec un niveau de confiance explicite sur chaque donnée.
- Conserve cibles, exécutions, résultats, erreurs et exports en local (SQLite, `./var/`).
- Fournit une TUI Textual et une CLI strictement équivalentes fonctionnellement.
- Produit des rapports HTML (5 thèmes, graphe de relations Mermaid embarqué), JSON, Markdown, CSV, DOT et Mermaid autonomes.

### Ce qu'Omega-track ne fait pas

| Fonction | Outil responsable |
|---|---|
| Scan de ports, identification de services et bannières | OMEGA-CHECK |
| Contrôles HTTP/HTTPS, headers, TLS, hygiène web | OMEGA-SCAN |
| Crawl, traversal d'architecture et descente sur cibles liées | OMEGA-DEEP |
| Crawl distant page par page (liens, fichiers) | OMEGA-FOLD |
| Tests de charge | OMEGA-STRESS |
| Fuzzing et tests de robustesse applicative | OMEGA-FUZZ |

À éviter, y compris hors MVP : brute-force de sous-domaines, scan de ports, crawl web, collecte intrusive de données personnelles, automatisation de contournement de protections, scraping fragile de plateformes imposant une authentification, recherche de personnes/réseaux sociaux/pastebins-leaks, surveillance périodique/récurrente d'une cible (voir `docs/PRODUCT_SCOPE.md` §7 "Différé volontairement").

### Avertissement d'usage autorisé

Omega-track est un outil d'investigation réseau destiné à un usage légitime : audit de votre propre infrastructure, réponse à incident, veille sur un périmètre que vous êtes autorisé à documenter. La collecte reste presque entièrement passive/publique (RDAP, DNS, CT logs — des données déjà exposées publiquement par la cible ou son registrar), à l'exception du traceroute (actif léger, toujours visible dans le profil utilisé).

**Aucune observation ne démarre sur une cible non épinglée sans confirmation explicite** (`--authorize` en CLI, confirmation en TUI). Vous êtes seul responsable de vérifier que votre usage respecte les lois applicables et les conditions d'utilisation des sources tierces consultées.

## 2. Installation

### Prérequis

- Python 3.10+
- Connexion Internet, pour les dépendances et les sources passives interrogées
- `traceroute` ou `tracepath` installé (module NeoTrace) — dégrade proprement en son absence, le reste de l'outil fonctionne normalement

### Installation

```bash
[ -d omega-track ] && echo "ℹ️ Déjà extrait ici, étape ignorée." || tar -xzf omega-track.tar.gz
cd omega-track/
chmod +x install.sh
./install.sh
```

`install.sh` :

1. Crée l'environnement virtuel `.venv` s'il n'existe pas déjà.
2. Installe les dépendances (`pip install -e .`, `pyproject.toml` reste l'unique source de vérité).
3. Rend `omega-track.sh` et `install.sh` exécutables.
4. Ajoute l'alias `track` à `~/.bashrc` et `~/.zshrc` (sans doublon si déjà présent).

### Dépendances

Déclarées dans `pyproject.toml` (pas de `requirements.txt` séparé) :
- `omega-lib` : bibliothèque partagée de la suite (`ConfidenceLevel`, thèmes, détection de terminal)
- `textual` : interface TUI, thèmes, adaptation automatique au terminal
- `dnspython` : résolution DNS directe et inverse
- `httpx` : sondes RDAP/CT/archives/BGP/VirusTotal/HIBP
- `maxminddb` : lecture des bases GeoIP locales (DB-IP Lite, MaxMind GeoLite2)
- `jinja2` : templating pour l'export HTML
- Dépendances de développement (`pip install -e ".[dev]"`) : `pytest`, `pytest-asyncio`, `pytest-cov`, `pytest-httpserver`, `ruff`, `mypy`, `import-linter`

## 3. Utilisation

### Mode interactif (TUI)

Recommandé pour l'usage quotidien — lancé sans argument :

```bash
./omega-track.sh
```
si vous avez créé l'alias, tapez juste `track` dans le terminal :
```bash
track
```

Parcours : écran de démarrage (se ferme sur une touche ou un clic) → menu principal (Cibles / Tracker / Résultats / Historique / Dashboard / GeoIP / Sources à clé / Réglages / Aide) → saisie ou sélection de la cible (confirmation explicite si non épinglée) et choix des modules de collecte → observation (jauge et déroulé des opérations en direct, annulable) → résultats détaillés par onglet (Identité/DNS/Réseau-ASN/NeoTrace/Certificats/Archives/Relations/Diagnostics, export) → historique/dashboard/réglages depuis le menu principal. L'adaptation au terminal (couleurs, taille, dégradation structurelle) est automatique.

#### Raccourcis clavier

| Touche | Action |
|---|---|
| `↑` / `↓` | Naviguer entre les éléments d'un écran |
| `Tab` / `Maj+Tab` | Naviguer entre les champs d'un formulaire |
| `Échap` | Retour à l'écran précédent (confirmation de sortie sur l'accueil) |
| `t` | Thème suivant (appliqué immédiatement, sans confirmation) |
| `r` | Rafraîchir la détection du terminal |
| `a` | Afficher l'aide |
| `q` | Quitter (avec confirmation) |

### Langues de l'interface

L'interface est disponible en 17 langues : français, anglais, espagnol, portugais (Brésil), italien, allemand, néerlandais, polonais, russe, chinois simplifié, vietnamien, thaï, indonésien, japonais, coréen, hindi et arabe. Le choix se fait dans les Réglages (« Langue / Language ») et s'applique après un redémarrage de l'interface ; la variable `OMEGA_TRACK_LANG` (par exemple `OMEGA_TRACK_LANG=en ./omega-track.sh`) force une langue le temps d'une session. Lancé depuis omega-suite, omega-track prend la langue de la suite. Sur une console texte Linux (TTY), les langues à écriture non latine s'affichent en anglais pour la session. La ligne de commande reste en français.

### Contact et support

L'aide (touche `a`) propose un écran **Contact et support** : *Payer un café* (page PayPal du développeur), *Contacter le support* (adresse mail et formulaire de contact du site, affichés en clair), *Se déclarer utilisateur (anonyme)* et *Vérifier les mises à jour*. La déclaration est volontaire, désactivée par défaut et envoyée une seule fois : elle sert seulement à compter les utilisateurs et, si on le souhaite, leur continent ou leur pays (listes fermées, jamais de texte libre). Elle envoie une clé tirée au hasard, le nom du logiciel (`omega-track`) et sa version ; jamais de nom, de nom de machine, de réglage, de cible ni de résultat. L'adresse IP n'est pas enregistrée dans les déclarations, mais passe, comme toute visite, par les contrôles de sécurité et le journal du serveur de réception. Retrait à tout moment depuis le même écran (*Ne plus me déclarer*). La vérification des mises à jour lit seulement la liste des versions publiées sur le site, et jamais sans clic.

### Mode scriptable (CLI)

Toute sous-commande déclenche le mode CLI :

```bash
# Cibles
./omega-track.sh target add example.org --alias "site vitrine" --tag prod
./omega-track.sh target list
./omega-track.sh target pin <target_id>

# Lancer et suivre une observation
./omega-track.sh track run <target_id> --module dns --module rdap --module neotrace --authorize
./omega-track.sh track status <run_id>
./omega-track.sh track show <run_id>
./omega-track.sh track replay <run_id> --authorize

# Historique
./omega-track.sh history list --target <target_id> --status completed --since 2026-01-01

# Export — 6 formats, 5 thèmes pour le HTML
./omega-track.sh export <run_id> --format html --theme omega-neon --redact contacts_only

# GeoIP
./omega-track.sh geoip status
./omega-track.sh geoip update --provider dbip

# Sources de réputation à clé (divulgation affichée avant tout enregistrement)
./omega-track.sh source list
./omega-track.sh source info virustotal
./omega-track.sh source configure virustotal <cle_api>

# Réglages et purge
./omega-track.sh config show
./omega-track.sh cleanup preview --older-than 30
./omega-track.sh cleanup run --older-than 30 --yes

# Diagnostics locaux (versions, capacités, chemins, état GeoIP)
./omega-track.sh diagnostics
```

Toute sous-commande accepte `--json` pour une sortie strictement machine-lisible.

#### Codes de sortie

| Code | Signification |
|---:|---|
| `0` | Succès (observation terminée, `COMPLETED`) |
| `1` | Erreur de validation (cible invalide, format d'export inconnu, transition d'état invalide, clé API absente...) |
| `2` | Cible non autorisée (ni épinglée, ni `--authorize`) |
| `3` | Ressource introuvable ou source indisponible (cible/run inconnu, échec de téléchargement GeoIP) |
| `4` | Observation partielle (`PARTIAL`) — pas un échec, certains modules seulement ont abouti |
| `5` | Erreur interne inattendue |
| `130` | Interrompu par l'utilisateur (`Ctrl+C`) |

### Formats de cible acceptés

```text
192.168.1.10                IPv4
2001:db8::1                 IPv6
example.org                 Domaine
```

## 4. Modules de collecte

| Module | Mode de collecte | Actif par défaut | Clé requise |
|---|---|:---:|:---:|
| `dns` | Actif léger (résolution directe) | oui | non |
| `reverse_dns` | Actif léger (PTR) | oui | non |
| `rdap` | Passif public | oui | non |
| `neotrace` | Actif léger (traceroute/tracepath) | oui | non |
| `certificate_transparency` | Passif public (`crt.sh`) | non | non |
| `archives` | Passif public (Wayback Machine) | non | non |
| `bgp` | Passif public (RIPEstat) | non | non |
| `virustotal` | Avec clé utilisateur | non | oui (gratuite) |
| `hibp` | Avec clé utilisateur | non | oui (**payante** depuis 2022) |

Les quatre premiers modules forment le socle MVP (`dns`/`reverse_dns`/`rdap`/`neotrace`) et sont cochés par défaut dans le formulaire de lancement ; les cinq suivants sont optionnels et doivent être explicitement activés. Une source sans clé configurée n'échoue jamais l'observation : le module correspondant passe simplement `SKIPPED` (« non exécuté »). Détail par source, quotas et licences : `docs/DATA_SOURCES.md`.

## 5. Architecture

Omega-track est structuré en **Clean Architecture** (domain / application / infrastructure / interfaces / ports / core / app / plugins), alignée sur le gabarit de la suite `omega-` (voir `omega-check`/`omega-fold`) et vérifiée par `import-linter` à chaque modification.

```text
src/omega_track/
├── domain/          Logique métier pure (cibles, TrackRun/ModuleRun, findings, relations, profils...)
├── application/     Cas d'usage (commands/queries/orchestrateurs de phase/politiques)
├── ports/           Contrats attendus par l'application (collecteurs, repositories, exporteurs...)
├── infrastructure/  Implémentations concrètes (dnspython/httpx/subprocess/maxminddb, SQLite, jinja2)
├── interfaces/      tui/ (Textual) et cli/ (scriptable), à parité fonctionnelle stricte
├── app/             Assemblage (DependencyContainer, bootstrap, cycle de vie)
├── core/            Vocabulaire transverse (versions, réexports omega-lib)
└── plugins/         Modules optionnels à source unique (CT, archives, BGP, VirusTotal, HIBP)
```

Règles de conception :
- `domain/` ne fait jamais de réseau ni d'I/O ; `infrastructure/` fait le réseau et l'I/O, ne juge jamais.
- `interfaces/` affiche, ne contient aucune logique métier — CLI et TUI appellent strictement les mêmes cas d'usage.
- 1 module de collecte = 1 source = 1 statut (`ModuleRun`) : jamais deux sources agrégées sous un seul statut ambigu.
- Une absence de champ isolé n'est jamais une erreur ; seule l'indisponibilité totale d'une source déclenche `SKIPPED`/`FAILED`.

## 6. Sources de données

| Source | Fournisseur | Clé | Mode |
|---|---|:---:|---|
| DNS direct/inverse | Résolveur système | non | Actif léger |
| RDAP | Bootstrap IANA → RIR/registrar | non | Passif public |
| Certificate Transparency | `crt.sh` (Sectigo) | non | Passif public |
| Archives web | Wayback Machine (Internet Archive) | non | Passif public |
| BGP / annonces réseau | RIPEstat (RIPE NCC) | non | Passif public |
| GeoIP | DB-IP Lite (défaut) ou MaxMind GeoLite2 | non / oui | Offline (base locale) |
| NeoTrace | `traceroute`/`tracepath` local | non | Actif léger |
| Réputation | VirusTotal | oui (gratuite) | Avec clé |
| Réputation | Have I Been Pwned | oui (payante) | Avec clé |

Quota, licence et repli exacts pour chaque source : `docs/DATA_SOURCES.md`. Aucune clé API n'apparaît jamais dans les logs, exports ou écrans de diagnostic.

## 7. Politique de confiance

Chaque champ collecté porte un niveau parmi (partagé avec toute la suite via `omega-lib`) :

| Niveau | Signification |
|---|---|
| `VERIFIED` | Fait protocolaire observé directement, non falsifiable par la cible (ex : réponse DNS directe, mesure traceroute locale). |
| `DECLARED` | Valeur auto-annoncée par la source dans un champ qu'elle contrôle entièrement (ex : donnée RDAP affichée par le registrar) — plausible mais falsifiable à volonté. |
| `CORROBORATED` | Une valeur `DECLARED` confirmée par un indice indépendant (ex : un domaine observé par au moins deux logs Certificate Transparency distincts). |
| `INFERRED` | Déduit d'un pattern/heuristique, sans déclaration explicite (ex : ASN commun utilisé pour suggérer une relation, jamais promu automatiquement). |
| `UNKNOWN` | Aucun indice exploitable, ou activement masqué par la cible. |

Le score de confiance global d'une observation est une aide de lecture, jamais un verdict de sécurité.

## 8. Niveaux de collecte, autorisation et redaction

Chaque profil rend la nature de ses actions explicite (`CollectionMode`) :

- **Offline** : validation de cible, lecture GeoIP locale, corrélations sur données déjà stockées, exports — aucun réseau.
- **Passif public** : RDAP, DNS public, CT logs, archives, BGP — seule la cible interrogée est transmise au tiers, propriété inhérente au protocole.
- **Actif léger** : résolution DNS, reverse DNS, traceroute — le résolveur configuré sur la machine et chaque routeur intermédiaire du chemin voient la requête.
- **Avec clé utilisateur** : fournisseurs qui exigent une clé ou appliquent des quotas, activés uniquement après configuration explicite et divulgation affichée (quota, données envoyées).

**Garde d'autorisation** : aucune observation ne démarre sur une cible non épinglée sans confirmation explicite (`--authorize` en CLI, case à cocher en TUI). Épingler une cible l'autorise durablement pour ses futures observations.

**Redaction des exports** : chaque export accepte une politique (`none`/`contacts_only`/`sensitive_only`/`strict`) qui masque les champs sensibles (contacts RDAP notamment) dans le rendu exporté — le stockage local, lui, garde toujours la donnée complète collectée. Détail : `docs/PRIVACY.md`.

## 9. Compatibilité terminaux

Le TUI (Textual) détecte automatiquement les capacités du terminal (émulateur, taille) et adapte sa feuille de style structurelle en conséquence (`complete`/`standard`/`reduced`/`mono`), sans flag manuel. Le mode CLI reste toujours en texte simple, indépendant du terminal. Politique partagée par toute la suite `omega-` (`omega-lib`, `terminal/policies.py`).

### Profil selon l'émulateur détecté

| Émulateur | Profil initial |
|---|---|
| Ghostty, Alacritty, WezTerm, Kitty | `complete` |
| Konsole, GNOME Terminal, Terminator, Xfce4 Terminal | `standard` |
| xterm, urxvt, SSH moderne | `reduced` |
| TTY Linux, SSH legacy | `mono` |
| Émulateur non reconnu | `reduced` (repli par défaut) |

### Profil selon la taille du terminal

| Taille minimale (colonnes × lignes) | Plafond de profil |
|---|---|
| 120 × 32 | `complete` |
| 100 × 28 | `standard` |
| 80 × 24 | `reduced` |
| en dessous | `mono` |

Le profil final retenu est **le plus restrictif des deux** (émulateur et taille). Rafraîchissable en direct par la touche `r`.

## 10. Exports

Les rapports Markdown et HTML s'écrivent dans la langue choisie dans les Réglages (« Langue des exports », par défaut celle de l'interface) ; JSON, CSV, DOT et Mermaid restent des données, non traduites. Les rapports sont générés dans `var/exports/` par défaut (chemin runtime ancré sur le dossier du projet, `$OMEGA_TRACK_VAR_DIR` pour le surcharger), ou au chemin indiqué (`--output` en CLI, boîte de dialogue en TUI). Nom de fichier horodaté et unique : `{horodatage}_{cible}_{id_court}.{extension}`.

| Format | Contenu |
|---|---|
| `json` | Structure complète de l'observation (`TrackRun` + findings + relations), source de vérité, strictement JSON-sérialisable |
| `markdown` | Rapport humain compact, lisible hors terminal |
| `html` | Rapport web autonome, 5 thèmes au choix (`--theme`), graphe de relations Mermaid embarqué inline |
| `csv` | Une table par catégorie de finding |
| `dot` | Graphe de relations Graphviz, fichier autonome |
| `mermaid` | Graphe de relations Mermaid, fichier autonome |

## 11. Historique, purge et rejeu

Chaque observation est persistée (SQLite, `var/db/omega-track.db`) : historique consultable et filtrable (cible/statut/tag/période), dashboard de synthèse (répartition par statut, fiabilité par module, typologie des derniers findings), rejeu d'une observation sur la même cible sans ressaisie (`track replay`), et purge de l'historique ancien avec aperçu systématique avant toute suppression (`cleanup preview` avant `cleanup run --yes`).

## 12. Tests

```bash
source .venv/bin/activate
lint-imports        # verifie la Dependency Rule
pytest -q           # 485 tests
ruff check .
mypy src
```

Structure : `tests/unit/` (domaine et application, sans I/O réelle), `tests/integration/` (SQLite/fichiers réels, serveur HTTP factice `pytest-httpserver`, TUI headless via l'API `Pilot` de Textual).

## 13. Hors périmètre

- Historique WHOIS/DNS complet, passive DNS commercial
- Recherche de personnes, réseaux sociaux, pastebins/leaks
- Scan de ports, identification de services et bannières (`omega-check`)
- Contrôles HTTP/HTTPS, headers, TLS (`omega-scan`)
- Crawl et traversal d'architecture (`omega-deep`/`omega-fold`)
- Tests de charge (`omega-stress`), fuzzing (`omega-fuzz`)
- Carte TUI interactive (réservée au rapport HTML exporté)
- MTR en continu, multi-sonde et multi-vantage-points
- Mode batch/périodique/surveillance récurrente d'une cible — un `TrackRun` reste toujours une action manuelle explicite
- Moteur de migration de schéma SQLite (schéma additif, même pratique que le reste de la suite)

---

> Omega-track — Observer, corréler, qualifier, rapporter.
> Une identité numérique avec une confiance explicite sur chaque donnée, jamais une certitude déguisée.
