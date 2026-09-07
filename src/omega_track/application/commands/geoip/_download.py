# Copyright (c) 2026 kraynux - Licence MIT
"""Logique de telechargement+persistance partagee entre
initialize_database.py et update_database.py (Phase 5) - prive (voir
infrastructure/repositories/sqlite/_profile_serde.py pour le meme usage
d'un module `_xxx.py` partage entre deux fichiers publics du meme
sous-package).

Seul GeoIpDownloadError (echec I/O/integrite du telechargement) est
rattrape ici et transforme en statut 'download_failed' persiste - jamais
destructif, l'ancien fichier/statut reste inchange (plan de dev §5).
MaxMindCredentialsMissingError n'est PAS rattrape : c'est une precondition
de configuration que l'appelant doit corriger avant de reessayer
(voir application/commands/geoip/configure_provider.py::
validate_geoip_configuration, fait pour detecter ce cas en amont), pas un
echec de telechargement au meme titre."""
from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from omega_track.application.exceptions import GeoIpDownloadError
from omega_track.domain.entities.geoip_database_status import GeoIpDatabaseStatus
from omega_track.ports.repositories.geoip_database_repository import GeoipDatabaseRepository
from omega_track.ports.services.database_updater import DatabaseUpdater


def download_and_persist_geoip_database(
    *,
    geoip_database_repository: GeoipDatabaseRepository,
    database_updater: DatabaseUpdater,
    provider: str,
    destination: Path,
    now: Callable[[], datetime],
) -> GeoIpDatabaseStatus:
    try:
        status = database_updater.download_latest(provider, destination)
    except GeoIpDownloadError:
        previous = geoip_database_repository.get_status(provider)
        status = GeoIpDatabaseStatus(
            provider=provider,
            edition=previous.edition if previous is not None else "inconnue",
            local_path=str(destination),
            checksum=previous.checksum if previous is not None else "",
            downloaded_at=previous.downloaded_at if previous is not None else now(),
            published_at=previous.published_at if previous is not None else None,
            status="download_failed",
        )
    geoip_database_repository.save_status(status)
    return status
