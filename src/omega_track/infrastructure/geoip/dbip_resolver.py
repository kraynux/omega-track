# Copyright (c) 2026 kraynux - Licence MIT
"""Fournisseur GeoIP par defaut, sans cle API (plan de dev §5
"Standard : DB-IP Lite")."""
from __future__ import annotations

from pathlib import Path

from omega_track.infrastructure.config.paths import default_geoip_db_path
from omega_track.infrastructure.geoip.mmdb_reader import MmdbGeoIpResolver, MmdbReader

PROVIDER = "dbip"


def build_dbip_resolver(var_dir: Path | None = None) -> MmdbGeoIpResolver:
    return MmdbGeoIpResolver(MmdbReader(default_geoip_db_path(PROVIDER, var_dir)), source=PROVIDER)
