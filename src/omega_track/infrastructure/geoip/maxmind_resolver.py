# Copyright (c) 2026 kraynux - Licence MIT
"""Fournisseur GeoIP avance, apres renseignement volontaire d'une cle
utilisateur (plan de dev §5 "Avance : MaxMind GeoLite2")."""
from __future__ import annotations

from pathlib import Path

from omega_track.infrastructure.config.paths import default_geoip_db_path
from omega_track.infrastructure.geoip.mmdb_reader import MmdbGeoIpResolver, MmdbReader

PROVIDER = "maxmind"


def build_maxmind_resolver(var_dir: Path | None = None) -> MmdbGeoIpResolver:
    return MmdbGeoIpResolver(MmdbReader(default_geoip_db_path(PROVIDER, var_dir)), source=PROVIDER)
