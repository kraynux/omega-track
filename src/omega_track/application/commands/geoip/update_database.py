# Copyright (c) 2026 kraynux - Licence MIT
"""Use case UpdateGeoIpDatabase (plan de dev §5) - declenche par une
action explicite (TUI/CLI) ou l'option auto-update : contrairement a
InitializeGeoIpDatabase, telecharge toujours, meme si une base valide est
deja presente."""
from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from omega_track.application.commands.geoip._download import download_and_persist_geoip_database
from omega_track.domain.entities.geoip_database_status import GeoIpDatabaseStatus
from omega_track.ports.repositories.geoip_database_repository import GeoipDatabaseRepository
from omega_track.ports.services.database_updater import DatabaseUpdater


def update_geoip_database(
    *,
    geoip_database_repository: GeoipDatabaseRepository,
    database_updater: DatabaseUpdater,
    provider: str,
    destination: Path,
    now: Callable[[], datetime],
) -> GeoIpDatabaseStatus:
    return download_and_persist_geoip_database(
        geoip_database_repository=geoip_database_repository,
        database_updater=database_updater,
        provider=provider,
        destination=destination,
        now=now,
    )
