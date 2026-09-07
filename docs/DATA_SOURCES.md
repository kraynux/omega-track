# OMEGA-TRACK – Sources de données

> **Ces informations (quotas, conditions, disponibilité de clé gratuite) sont susceptibles de changer sans préavis de la part des fournisseurs tiers.** Chaque ligne doit être revérifiée au moment de l'implémentation réelle du collecteur correspondant, pas seulement recopiée depuis ce tableau au moment de la Phase 0. Ce document sert de point de départ documenté, pas de garantie figée.

Chaque source suit la classification `CollectionMode` du domaine (`OFFLINE`, `PASSIVE_PUBLIC`, `ACTIVE_LIGHT`, `API_KEY`) et le niveau de confiance qu'elle peut raisonnablement produire (`domain/value_objects/evidence.py`, `ConfidenceLevel`).

---

## Sources sans clé (MVP)

### Résolveur DNS système

- **Fournisseur** : celui déjà configuré sur la machine de l'utilisateur (`/etc/resolv.conf` ou équivalent OS), via `dnspython`.
- **Clé requise** : non.
- **Quota** : celui du résolveur configuré, hors du contrôle de TRACK.
- **Licence/CGU** : sans objet.
- **Mode de collecte** : `ACTIVE_LIGHT`.
- **Repli** : jamais de résolveur public codé en dur (D-014) — si la résolution échoue, le module DNS passe `FAILED`/`PARTIAL` selon le reste du TrackRun.
- **Confiance produite** : `VERIFIED` (réponse DNS directe).

### RDAP public

- **Fournisseur** : bootstrap IANA (`https://data.iana.org/rdap/`) redirigeant vers le serveur RDAP du RIR/registre concerné (ARIN, RIPE, APNIC, registrars de TLD...).
- **Clé requise** : non.
- **Quota** : variable par registre, non centralisé ; certains registrars appliquent un rate-limit informel. Aucun quota unique à documenter — comportement de repli générique (backoff + `PARTIAL`) plutôt qu'une règle par registre.
- **Licence/CGU** : RDAP est un protocole standardisé (RFC 7480-7484), pas un service à conditions d'usage centralisées — les CGU réelles dépendent du registre interrogé.
- **Mode de collecte** : `PASSIVE_PUBLIC`.
- **Repli** : un champ RDAP individuel manquant n'est jamais une erreur (D-015) ; seule une indisponibilité totale de la requête déclenche un statut `PARTIAL` sur le TrackRun.
- **Confiance produite** : `DECLARED` (donnée affichée par le registrar/registre, non corroborée indépendamment).

### Reverse DNS / PTR

- **Fournisseur** : même résolveur système que ci-dessus.
- **Clé requise** : non.
- **Quota** : celui du résolveur.
- **Mode de collecte** : `ACTIVE_LIGHT` (facultatif par hop, activable dans le profil).
- **Confiance produite** : `VERIFIED` si la requête aboutit, `UNKNOWN` sinon (jamais bloquant).

### GeoIP — DB-IP Lite

- **Fournisseur** : DB-IP (db-ip.com), édition "Lite", fichier MMDB téléchargeable mensuellement.
- **Clé requise** : non.
- **Quota** : téléchargement du fichier mensuel, pas d'appel réseau par lookup (base locale).
- **Licence** : CC BY 4.0 (Creative Commons Attribution) — attribution obligatoire, redistribution autorisée avec attribution. Comportement par défaut du produit (D-003 du plan de dev).
- **Mode de collecte** : `OFFLINE` (une fois la base téléchargée).
- **Repli** : le tracker continue sans géolocalisation si la base est absente/périmée, marque le finding réseau comme "géolocalisation indisponible" plutôt que d'échouer.
- **Confiance produite** : `VERIFIED` (base locale déjà identifiée par l'utilisateur).

### Certificate Transparency — `crt.sh`

- **Fournisseur** : crt.sh (opéré par Sectigo), interface de recherche sur les logs CT publics.
- **Clé requise** : non.
- **Quota** : **aucun quota formellement publié** — service communautaire sans SLA, connu pour ralentir/timeout sous charge. Traiter comme une source à clé du point de vue de la robustesse (quota/cache/backoff/statut "non exécuté", voir `PRODUCT_SCOPE.md` §3) malgré l'absence de clé.
- **Licence/CGU** : logs CT publics par nature (RFC 6962) ; pas de CGU distincte connue pour crt.sh au-delà d'un usage raisonnable.
- **Mode de collecte** : `PASSIVE_PUBLIC`.
- **Confiance produite** : `DECLARED` sur une seule occurrence, `CORROBORATED` si observé par 2+ CT logs distincts (D-011).

### Archives web publiques — Wayback Machine (Internet Archive)

- **Fournisseur** : archive.org, API CDX (`web.archive.org/cdx/search/cdx`).
- **Clé requise** : non.
- **Quota** : pas de quota formel publié, mais rate-limiting informel documenté par l'Internet Archive en cas d'usage automatisé intensif — même traitement de robustesse que crt.sh (quota/cache/backoff).
- **Licence/CGU** : contenu archivé soumis aux conditions de l'Internet Archive ; usage à des fins de recherche/vérification généralement toléré, éviter tout téléchargement en masse.
- **Mode de collecte** : `PASSIVE_PUBLIC`.
- **Confiance produite** : `DECLARED` (snapshot archivé, horodaté par l'Internet Archive).

### BGP / annonces réseau — RIPEstat

- **Fournisseur** : RIPE NCC, API publique RIPEstat (`stat.ripe.net`).
- **Clé requise** : non.
- **Quota** : documenté par RIPE NCC comme généreux pour un usage raisonnable non massif ; pas de chiffre figé à citer ici sans revérification.
- **Licence/CGU** : conditions d'usage RIPEstat (usage raisonnable, pas de scraping massif).
- **Mode de collecte** : `PASSIVE_PUBLIC`.
- **Confiance produite** : `DECLARED`/`INFERRED` selon la donnée (annonce BGP observée = `DECLARED`, ASN commun utilisé pour une inférence de relation = `INFERRED`, jamais promu automatiquement en `Relation`, D-011).

### NeoTrace (traceroute/tracepath local)

- **Fournisseur** : aucun tiers — binaire local (`traceroute`, `tracepath`, ou équivalent OS).
- **Clé requise** : non.
- **Quota** : sans objet (local).
- **Licence** : celle du binaire système (généralement GPL pour `traceroute`/`tracepath` sous Linux — sans impact produit, un appel `subprocess`, pas une dépendance liée).
- **Mode de collecte** : `ACTIVE_LIGHT` — **la seule action réseau active du MVP**, toujours visible dans le profil utilisé (D-008 du plan de dev).
- **Repli** : état dégradé nommé "traceroute indisponible" (binaire absent ou capacité insuffisante — `CAP_NET_RAW`/setuid selon plateforme) distinct d'un hop non répondant. IPv4/IPv6 : branches de collecte et fixtures de test séparées (D-016).
- **Confiance produite** : `VERIFIED` (mesure locale directe).

---

## Sources à clé (v0.3+)

### GeoIP — MaxMind GeoLite2

- **Fournisseur** : MaxMind.
- **Clé requise** : **oui** — compte MaxMind gratuit + génération d'une "license key" (obligatoire depuis la modification de politique de MaxMind de décembre 2019, anti-scraping).
- **Quota** : téléchargement périodique du fichier MMDB, limité en fréquence par MaxMind (pas de chiffre à citer sans revérification à l'implémentation).
- **Licence** : EULA MaxMind GeoLite2 — attribution obligatoire, **redistribution du fichier brut interdite**, re-téléchargement périodique requis (le fichier n'expire pas techniquement mais l'EULA impose une actualisation régulière). Confirmer les termes exacts au moment de l'implémentation, l'EULA MaxMind a déjà changé plusieurs fois.
- **Mode de collecte** : `OFFLINE` une fois la base téléchargée ; `API_KEY` pour le téléchargement lui-même.
- **Confiance produite** : `VERIFIED`.

### VirusTotal (réputation)

- **Fournisseur** : VirusTotal (Google).
- **Clé requise** : oui (clé API gratuite disponible avec compte, limites plus généreuses en payant).
- **Quota connu à la rédaction** (2026-09-06, **à revérifier avant implémentation**) : de l'ordre de quelques requêtes/minute et quelques centaines/jour pour une clé gratuite — VirusTotal ajuste régulièrement ces seuils, ne jamais coder en dur un chiffre sans le revérifier contre la documentation officielle à jour.
- **Licence/CGU** : conditions d'utilisation VirusTotal — partage de données avec l'écosystème VirusTotal selon le type de requête, à afficher explicitement à l'utilisateur avant activation (spec §5.3 du plan de dev : "affichage préalable... données envoyées").
- **Mode de collecte** : `API_KEY`.
- **Confiance produite** : `DECLARED` (verdict d'un moteur tiers, jamais vérifié indépendamment par TRACK).

### Have I Been Pwned (réputation/organisation)

- **Fournisseur** : Troy Hunt / HIBP.
- **Clé requise** : **oui, et payante** depuis le changement de politique HIBP de 2022 — HIBP n'a plus d'offre d'API gratuite pour les recherches par domaine/breach depuis cette date. À confirmer précisément avant toute promesse faite à l'utilisateur dans l'écran de configuration (v0.3, `PRODUCT_SCOPE.md` §3) : ne jamais présenter HIBP comme "optionnel et gratuit avec clé", le distinguer explicitement des sources à clé gratuite (VirusTotal) dans l'UI.
- **Licence/CGU** : conditions d'utilisation HIBP, usage à des fins légitimes de sécurité uniquement.
- **Mode de collecte** : `API_KEY`.
- **Confiance produite** : `DECLARED`.

### GitHub (organisation, v0.4)

- **Fournisseur** : GitHub REST API.
- **Clé requise** : non pour un usage minimal (60 requêtes/heure par IP, non authentifié), oui pour un quota plus large (5000 requêtes/heure avec un token personnel — chiffres GitHub stables et documentés publiquement, à revérifier tout de même).
- **Licence/CGU** : conditions d'utilisation de l'API GitHub, usage raisonnable.
- **Mode de collecte** : `PASSIVE_PUBLIC` sans clé (quota réduit), `API_KEY` avec token (quota étendu).
- **Confiance produite** : `DECLARED` (dépôt/organisation publiquement listé, pas une preuve d'appartenance vérifiée indépendamment).

---

## Règle transverse

Aucune clé API ne doit jamais apparaître dans les logs, les exports, les écrans ou les diagnostics (§2.2 du plan de dev). Les clés sont stockées hors de la base de résultats, idéalement dans le trousseau système si disponible (`secret_store.py`), un fichier de configuration protégé restant le repli.
