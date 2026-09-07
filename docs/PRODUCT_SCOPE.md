# OMEGA-TRACK – Périmètre produit

Extrait et formalisé depuis `OMEGA_TRACK_PLAN_DEVELOPPEMENT.md` (§5) — ce document reste la référence détaillée, celui-ci en est la vue synthétique pour ne pas avoir à relire tout le plan pour savoir "est-ce que ce module est prévu, et à quelle version".

---

## 1. MVP (v0.1) — noyau local et réseau

Doit fonctionner correctement **sans clé API** et rester utile dès la première installation.

| Module | MVP | Dépendance | Sortie |
|---|---:|---|---|
| Gestion des cibles | Oui | SQLite | cibles, alias, tags, épinglage |
| Garde d'autorisation (D-010) | Oui | domaine/application | confirmation explicite avant tout track sur cible non épinglée |
| Profils de track | Oui | SQLite/config | modules et limites |
| DNS direct + PTR | Oui | dnspython/résolveur système (D-014) | records normalisés |
| RDAP public | Oui | HTTP | identité du domaine/IP lorsque disponible |
| GeoIP locale | Oui | DB-IP Lite | pays/ville/coords selon DB |
| ASN local | Oui si base disponible | MMDB locale | ASN et organisation |
| NeoTrace local | Oui | traceroute/tracepath, IPv4+IPv6 séparés (D-016) | hops, RTT, hostname, GeoIP/ASN |
| Corrélations simples | Oui | domaine, règles figées (D-011) | liens IP-domain-NS-cert |
| Résultats persistants | Oui | SQLite, schéma additif (D-018) | TrackRun + findings |
| JSON + Markdown | Oui | exporteurs | exports initiaux |
| TUI + CLI | Oui | Textual/CLI, `omega_lib.theme`/`terminal` | mêmes cas d'usage |

## 2. Version 0.2 : identité étendue

- Certificate Transparency (`crt.sh`) via source publique et normalisation des SAN.
- Sous-domaines observés passivement via CT ; aucun brute-force.
- Archives web publiques (Wayback Machine) et timeline de snapshots.
- HTML local autonome avec carte OpenStreetMap/Leaflet et **graphe de relations Mermaid embarqué inline** (pas seulement un fichier séparé — leçon D-009 de la suite).
- Graphviz DOT et Mermaid pour les relations (fichiers autonomes, en plus de l'inclusion HTML).
- CSV par table métier : IPs, DNS, certificats, hops, relations.
- Comparaison d'un TrackRun avec le précédent TrackRun de la même cible (`track replay`, D-013).

## 3. Version 0.3 : sources optionnelles à clé

- Écran/commande de configuration de sources avec clé utilisateur.
- VirusTotal, HIBP ou autres sources seulement si clé explicitement fournie et conditions d'usage acceptées — voir `DATA_SOURCES.md` pour l'état réel de chaque clé (HIBP n'est plus gratuite depuis 2022, à confirmer avant de promettre quoi que ce soit à l'utilisateur).
- Affichage préalable : clé requise, quota connu/configuré, données envoyées, mode de confidentialité.
- Quotas, cache, backoff et statut "non exécuté faute de clé/quota" — **même traitement pour les sources gratuites mais fragiles** (`crt.sh`, Wayback) que pour les sources à clé, pas réservé aux seules sources payantes.
- Ne jamais faire dépendre le succès global du track d'une API facultative.

## 4. Version 0.4 : organisation et enrichissements

- Dépôts publics via API officielle quand une clé est configurée ou via données explicitement publiques accessibles légalement.
- Patterns d'adresses email à partir de sources publiques, en distinguant `observed` et `inferred`.
- Comptes officiels et domaines associés, seulement avec preuve de relation.
- Offres d'emploi / stack déclarée : collecte modulaire, opt-in, stockage de la source et de l'horodatage.

## 5. Version 1.0 : stabilisation

- Schéma de stockage versionné et **vrai moteur de migrations** (D-018 : différé jusqu'ici volontairement, le MVP reste additif comme le reste de la suite).
- Rapports stables et versionnés.
- Politique de compatibilité des plugins.
- Documentation d'installation, de confidentialité, de licences de données et de limites.
- Batterie de tests complète et tests E2E TUI/CLI.

---

## 6. Hors périmètre — responsabilité d'un autre outil de la suite

| Fonction | Outil responsable |
|---|---|
| Scan de ports, identification de services et bannières | OMEGA-CHECK |
| Contrôles HTTP/HTTPS, headers, TLS, hygiène web | OMEGA-SCAN |
| Crawl, traversal d'architecture et descente sur cibles liées | OMEGA-DEEP |
| Crawl distant page par page (liens, fichiers) | OMEGA-FOLD |
| Tests de charge | OMEGA-STRESS |
| Fuzzing et tests de robustesse applicative | OMEGA-FUZZ |

## 7. Différé volontairement (tout périmètre, pas seulement MVP)

Ces éléments augmentent fortement la complexité, la fragilité ou les contraintes de conformité :

- Historique WHOIS/DNS complet : souvent dépendant de fournisseurs payants ou à clé.
- Passive DNS commercial : connecteur optionnel, quota déclaré clairement.
- VirusTotal, Google Safe Browsing, HIBP : uniquement via clés fournies par l'utilisateur.
- Recherche de personnes, LinkedIn, pastebins/leaks : forte volatilité, contraintes de CGU et risques de collecte — modules séparés et opt-in si jamais construits, jamais le cœur du produit.
- Carte TUI interactive : vue tabulaire/ASCII en Textual, carte détaillée réservée au HTML exporté.
- MTR en continu, multi-sonde et multi-vantage-points : extension NeoTrace après stabilité du traceroute local.
- Screenshots : seulement si la relation avec OMEGA-SCAN/OMEGA-DEEP est clairement définie.
- **Mode batch/périodique/surveillance récurrente d'une cible (D-017)** : hors périmètre jusqu'à la v1.0 incluse. Un `TrackRun` reste toujours une action manuelle explicite. Si un besoin réel apparaît un jour, cela rouvre la question du garde d'autorisation (D-010) — une surveillance récurrente n'a pas le même poids qu'une consultation ponctuelle, donc une nouvelle décision à part entière, pas une simple extension technique.
- **Vrai moteur de migration de schéma SQLite avant v1.0 (D-018)** : le MVP reste additif (`CREATE TABLE IF NOT EXISTS`), même pratique que CHECK/DEEP/FOLD.
