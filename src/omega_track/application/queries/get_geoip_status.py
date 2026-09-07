# Copyright (c) 2026 kraynux - Licence MIT
"""Use case GetGeoIpDatabaseStatus (plan de dev §5) - calcule l'age de la
base sans jamais declencher de telechargement ("Verifier l'age de la DB
au demarrage sans obligatoirement telecharger") : purement une lecture,
`is_stale` est informatif pour la TUI/CLI, pas une action."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta

from omega_track.domain.entities.geoip_database_status import GeoIpDatabaseStatus
from omega_track.ports.repositories.geoip_database_repository import GeoipDatabaseRepository

DEFAULT_STALE_AFTER = timedelta(days=45)
"""DB-IP et MaxMind republient tous les deux mensuellement - marge d'un
mois et demi avant de signaler une base perimee."""


@dataclass(frozen=True, slots=True)
class GeoIpStatusView:
    provider: str
    status: GeoIpDatabaseStatus | None
    age: timedelta | None
    is_stale: bool


def get_geoip_database_status(
    *,
    geoip_database_repository: GeoipDatabaseRepository,
    provider: str,
    now: Callable[[], datetime],
    stale_after: timedelta = DEFAULT_STALE_AFTER,
) -> GeoIpStatusView:
    status = geoip_database_repository.get_status(provider)
    if status is None:
        return GeoIpStatusView(provider=provider, status=None, age=None, is_stale=True)
    age = now() - status.downloaded_at
    return GeoIpStatusView(provider=provider, status=status, age=age, is_stale=age > stale_after)
