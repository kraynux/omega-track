# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat de mise a jour des bases GeoIP locales (plan de dev, Phase
3/5). L'atomicite (fichier temporaire, verification d'integrite,
remplacement atomique, sauvegarde courte de l'ancienne version - "Regles
d'update", §5) est une responsabilite d'infrastructure ; ce port n'expose
que le resultat final."""
from __future__ import annotations

from pathlib import Path
from typing import Protocol

from omega_track.domain.entities.geoip_database_status import GeoIpDatabaseStatus


class DatabaseUpdater(Protocol):
    def download_latest(self, provider: str, destination: Path) -> GeoIpDatabaseStatus: ...
