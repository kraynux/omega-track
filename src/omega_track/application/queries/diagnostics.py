# Copyright (c) 2026 kraynux - Licence MIT
"""Use case Diagnostics (plan de dev §9 `diagnostics` - "versions,
capacites locales, chemins, base GeoIP"). `var_dir` est fourni par
l'appelant (jamais resolu ici via infrastructure/config/paths.py -
Dependency Rule). "mtr"/"graphviz" ne sont pas rapportes : aucune
infrastructure reelle ne les utilise dans ce projet (MTR deliberement
hors perimetre depuis la Phase 6, aucun rendu Graphviz automatique
construit - l'export .dot reste un fichier texte, voir Phase 8) -
rapporter une detection de binaire pour des fonctionnalites qui
n'existent pas serait trompeur."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from omega_track.application.queries.get_geoip_status import (
    GeoIpStatusView,
    get_geoip_database_status,
)
from omega_track.core.constants import APP_VERSION, EXPORT_SCHEMA_VERSION
from omega_track.ports.collectors.traceroute_collector import TracerouteCollector
from omega_track.ports.repositories.geoip_database_repository import GeoipDatabaseRepository


@dataclass(frozen=True, slots=True)
class DiagnosticsReport:
    app_version: str
    schema_version: int
    var_dir: str
    traceroute_available: bool
    geoip_status: GeoIpStatusView


def run_diagnostics(
    *,
    traceroute_collector: TracerouteCollector,
    geoip_database_repository: GeoipDatabaseRepository,
    geoip_provider: str,
    var_dir: Path,
    now: Callable[[], datetime],
) -> DiagnosticsReport:
    return DiagnosticsReport(
        app_version=APP_VERSION,
        schema_version=EXPORT_SCHEMA_VERSION,
        var_dir=str(var_dir),
        traceroute_available=traceroute_collector.is_available(),
        geoip_status=get_geoip_database_status(
            geoip_database_repository=geoip_database_repository, provider=geoip_provider, now=now
        ),
    )
