# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from pathlib import Path

from omega_track.infrastructure.geoip.dbip_resolver import build_dbip_resolver
from omega_track.infrastructure.geoip.maxmind_resolver import build_maxmind_resolver
from omega_track.infrastructure.geoip.mmdb_reader import MmdbGeoIpResolver


def test_build_dbip_resolver_uses_dbip_source(tmp_path: Path) -> None:
    resolver = build_dbip_resolver(tmp_path)
    assert isinstance(resolver, MmdbGeoIpResolver)
    assert resolver.source == "dbip"


def test_build_maxmind_resolver_uses_maxmind_source(tmp_path: Path) -> None:
    resolver = build_maxmind_resolver(tmp_path)
    assert isinstance(resolver, MmdbGeoIpResolver)
    assert resolver.source == "maxmind"
