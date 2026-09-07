# Copyright (c) 2026 kraynux - Licence MIT
"""Resolution des chemins runtime (var/), la seule source de verite pour
ces chemins. Copie verbatim du patron de omega-check/paths.py (D-007/D-008)
: tout vit par defaut dans le dossier de l'application (`./var`), rien
dans le filesystem utilisateur (`~/.config`, `~/.local/share`) sauf choix
explicite (override via `$OMEGA_TRACK_VAR_DIR` ou les chemins passes a
bootstrap.py) - voir docs/PRIVACY.md §1 pour la justification produit."""
from __future__ import annotations

import os
from pathlib import Path

DEFAULT_VAR_DIRNAME = "var"
ENV_VAR_DIR = "OMEGA_TRACK_VAR_DIR"


def resolve_var_dir() -> Path:
    """Racine des fichiers runtime : `$OMEGA_TRACK_VAR_DIR` si defini,
    sinon `./var` relatif au repertoire courant d'execution."""
    override = os.environ.get(ENV_VAR_DIR)
    if override:
        return Path(override)
    return Path.cwd() / DEFAULT_VAR_DIRNAME


def default_db_path(var_dir: Path | None = None) -> Path:
    base = var_dir if var_dir is not None else resolve_var_dir()
    return base / "db" / "omega-track.db"


def default_settings_path(var_dir: Path | None = None) -> Path:
    """settings.json - JSON, pas TOML (tranche, voir plan de dev §Phase 4)."""
    base = var_dir if var_dir is not None else resolve_var_dir()
    return base / "settings.json"


def default_exports_dir(var_dir: Path | None = None) -> Path:
    base = var_dir if var_dir is not None else resolve_var_dir()
    return base / "exports"


def default_geoip_dir(var_dir: Path | None = None) -> Path:
    base = var_dir if var_dir is not None else resolve_var_dir()
    return base / "geoip"


def default_geoip_db_path(provider: str, var_dir: Path | None = None) -> Path:
    """Fichier MMDB local d'un fournisseur donne (Phase 5) - un seul
    fichier gere par fournisseur, geo et ASN combinees quand la base
    source les porte toutes les deux (voir infrastructure/geoip/
    mmdb_reader.py::MmdbGeoIpResolver)."""
    return default_geoip_dir(var_dir) / f"{provider}-city.mmdb"


def default_secrets_path(var_dir: Path | None = None) -> Path:
    """secrets.json (Phase 5) - separe de settings.json : permissions
    0600 dediees, jamais melange aux reglages non sensibles (voir
    infrastructure/config/secret_store_adapter.py)."""
    base = var_dir if var_dir is not None else resolve_var_dir()
    return base / "secrets.json"


def default_cache_dir(var_dir: Path | None = None) -> Path:
    base = var_dir if var_dir is not None else resolve_var_dir()
    return base / "cache"


def default_screenshots_dir(var_dir: Path | None = None) -> Path:
    """Captures d'ecran Textual (`App.deliver_screenshot`, Phase 12,
    retour utilisateur : "il manque le menu screenshot de base fourni
    avec textual") - meme convention que les autres sous-dossiers de
    `var/`, jamais dans le filesystem utilisateur."""
    base = var_dir if var_dir is not None else resolve_var_dir()
    return base / "screenshots"
