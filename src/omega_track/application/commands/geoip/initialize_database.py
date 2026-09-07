# Copyright (c) 2026 kraynux - Licence MIT
"""Use case InitializeGeoIpDatabase (plan de dev §5) - idempotent :
ne telecharge que si aucune base valide n'est deja presente localement,
utilisable a chaque demarrage sans effet de bord si la base est deja
saine."""
from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from omega_track.application.commands.geoip._download import download_and_persist_geoip_database
from omega_track.domain.entities.geoip_database_status import GeoIpDatabaseStatus
from omega_track.ports.repositories.geoip_database_repository import GeoipDatabaseRepository
from omega_track.ports.services.database_updater import DatabaseUpdater


def initialize_geoip_database(
    *,
    geoip_database_repository: GeoipDatabaseRepository,
    database_updater: DatabaseUpdater,
    provider: str,
    destination: Path,
    now: Callable[[], datetime],
) -> GeoIpDatabaseStatus:
    existing = geoip_database_repository.get_status(provider)
    if existing is not None and existing.status == "ok" and Path(existing.local_path).exists():
        return existing
    return download_and_persist_geoip_database(
        geoip_database_repository=geoip_database_repository,
        database_updater=database_updater,
        provider=provider,
        destination=destination,
        now=now,
    )
