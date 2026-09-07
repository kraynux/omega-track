# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat de persistance de l'etat des bases GeoIP locales (plan de dev,
Phase 3/4/5)."""
from __future__ import annotations

from typing import Protocol

from omega_track.domain.entities.geoip_database_status import GeoIpDatabaseStatus


class GeoipDatabaseRepository(Protocol):
    def save_status(self, status: GeoIpDatabaseStatus) -> None: ...

    def get_status(self, provider: str) -> GeoIpDatabaseStatus | None: ...
