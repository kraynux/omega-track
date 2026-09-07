# OMEGA-TRACK – Confidentialité

## 1. Ce qui est stocké localement

Tout ce que produit un `TrackRun` est conservé dans une base SQLite locale (`./var/db/omega-track.db` par défaut, projet-local — pas `~/.local/share/`, voir la note de correction dans `OMEGA_TRACK_PLAN_DEVELOPPEMENT.md` §0 sur la vraie convention de la suite) :

- Cibles (IP/domaine, alias, tags, épinglage).
- Profils de track.
- Chaque exécution (`TrackRun`) : statut, progression, snapshot du profil utilisé.
- Chaque donnée collectée (`Finding`) : type, valeur, source, confiance, horodatage, statut de collecte.
- Relations inférées entre entités, avec leur niveau de confiance.
- Exports générés (métadonnées : format, chemin, checksum, options de redaction utilisées).
- État des bases GeoIP locales (fournisseur, édition, date de téléchargement).

Aucune donnée n'est chiffrée au repos par défaut — TRACK est un outil local mono-utilisateur, la protection du fichier SQLite relève des permissions du système de fichiers de l'utilisateur, comme le reste de la suite (`users.json`/`zones.json` équivalents dans d'autres outils OMEGA n'ont pas de chiffrement applicatif non plus). Si la base contient des contacts RDAP non redactés, c'est à l'utilisateur de protéger l'accès au fichier comme il protégerait n'importe quel autre document contenant des données personnelles.

## 2. Ce qui est envoyé à l'extérieur

Résumé par mode de collecte (voir `DATA_SOURCES.md` pour le détail par source) :

- **Offline** : rien n'est envoyé (lecture de la base GeoIP locale, corrélation sur données déjà stockées, export).
- **Passif public** (RDAP, DNS, CT logs, archives, RIPEstat) : seule la cible (IP/domaine) est transmise au tiers interrogé — c'est la nature même d'une requête RDAP/DNS/CT, ces services voient nécessairement quelle cible est recherchée. Aucune autre donnée de l'utilisateur n'est transmise.
- **Actif léger** (résolution DNS, reverse DNS, traceroute) : le résolveur DNS configuré sur la machine voit les requêtes de résolution (D-014 : jamais un résolveur public codé en dur, pour ne pas ajouter un tiers non choisi par l'utilisateur dans ce circuit) ; le traceroute expose l'IP source de la machine de l'utilisateur à chaque routeur intermédiaire du chemin réseau — propriété inhérente au traceroute lui-même, pas une fuite de TRACK.
- **Avec clé** (VirusTotal, HIBP, GitHub...) : la cible est transmise au fournisseur, selon ses propres conditions d'utilisation et sa propre politique de rétention — affiché explicitement à l'utilisateur avant activation de la source (voir `DATA_SOURCES.md`).

## 3. Redaction des exports

Chaque export supporte une `RedactionPolicy` : `NONE`, `CONTACTS_ONLY`, `SENSITIVE_ONLY`, `STRICT`. Les contacts (emails, téléphones observés via RDAP) sont les premiers candidats à la redaction — un export destiné à être partagé (rapport HTML envoyé à un tiers, par exemple) doit pouvoir masquer ces champs sans perdre la valeur du reste du rapport (relations, chemin réseau, findings techniques).

La redaction s'applique à l'export, jamais au stockage local lui-même — la base SQLite garde toujours la donnée complète collectée ; c'est un choix explicite (permettre de revenir en arrière sur la politique de redaction sans perdre de données), documenté ici pour ne pas être pris pour un oubli.

## 4. Garde d'autorisation (D-010)

Aucun `TrackRun` ne démarre sur une cible non épinglée-autorisée sans confirmation explicite (`--authorize` en CLI, case à cocher en TUI) — même mécanisme que OMEGA-SCAN et OMEGA-DEEP. Cette confirmation est journalisée (horodatage, cible concernée), même patron que l'`audit_hook` de DEEP.

## 5. Politique de rétention

- Les `TrackRun` et exports ne sont jamais supprimés automatiquement sans option explicite.
- Le nettoyage propose d'abord un aperçu (nombre d'éléments, taille, période ciblée) avant toute suppression.
- Les exports peuvent être supprimés sans supprimer l'exécution source qui les a produits.
- Supprimer une cible demande explicitement si les `TrackRun` associés doivent être conservés, anonymisés ou supprimés.
- Le cache (résultats de sources externes mis en cache pour limiter les appels répétés) est distinct de l'historique : vider le cache n'efface jamais l'historique des `TrackRun`.

## 6. Hors périmètre (rappel, voir D-017)

Aucun mode de suivi périodique/automatisé d'une cible n'est prévu jusqu'à la v1.0 incluse. Si ce besoin apparaît un jour, il doit rouvrir explicitement la question du garde d'autorisation (§4) — une surveillance récurrente d'une cible n'a pas le même poids, du point de vue de la vie privée de la cible observée, qu'une consultation ponctuelle.
