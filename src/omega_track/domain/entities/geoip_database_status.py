# Copyright (c) 2026 kraynux - Licence MIT
"""Etat d'une base GeoIP locale (table `geoip_databases`, Phase 4) -
absent de ARBORESCENCE.md/du plan de dev, ajoute par necessite : le port
`geoip_database_repository.py` (Phase 3) a besoin d'un type de retour
propre au domaine, pas d'un dict/tuple SQLite brut."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class GeoIpDatabaseStatus:
    provider: str
    """'dbip' ou 'maxmind' (Phase 5)."""
    edition: str
    local_path: str
    checksum: str
    downloaded_at: datetime
    published_at: datetime | None
    status: str
    """'ok'|'stale'|'missing'|'download_failed' - Phase 5."""
