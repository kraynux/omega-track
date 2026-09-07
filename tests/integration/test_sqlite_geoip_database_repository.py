# Copyright (c) 2026 kraynux - Licence MIT
import sqlite3
from datetime import datetime, timezone

from omega_track.domain.entities.geoip_database_status import GeoIpDatabaseStatus
from omega_track.infrastructure.repositories.sqlite.geoip_database_repository import (
    SqliteGeoipDatabaseRepository,
)

_NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def _status(**overrides) -> GeoIpDatabaseStatus:
    defaults = {
        "provider": "dbip",
        "edition": "city-lite",
        "local_path": "var/geoip/dbip-city-lite.mmdb",
        "checksum": "deadbeef",
        "downloaded_at": _NOW,
        "published_at": None,
        "status": "ok",
    }
    defaults.update(overrides)
    return GeoIpDatabaseStatus(**defaults)


def test_save_and_get_status(connection: sqlite3.Connection) -> None:
    repo = SqliteGeoipDatabaseRepository(connection)
    repo.save_status(_status())
    fetched = repo.get_status("dbip")
    assert fetched is not None
    assert fetched.edition == "city-lite"
    assert fetched.status == "ok"


def test_get_unknown_provider_returns_none(connection: sqlite3.Connection) -> None:
    repo = SqliteGeoipDatabaseRepository(connection)
    assert repo.get_status("maxmind") is None


def test_resave_overwrites_single_row_per_provider(connection: sqlite3.Connection) -> None:
    repo = SqliteGeoipDatabaseRepository(connection)
    repo.save_status(_status(status="ok"))
    repo.save_status(_status(status="stale"))
    assert repo.get_status("dbip").status == "stale"  # type: ignore[union-attr]


def test_two_providers_coexist_independently(connection: sqlite3.Connection) -> None:
    repo = SqliteGeoipDatabaseRepository(connection)
    repo.save_status(_status(provider="dbip"))
    repo.save_status(_status(provider="maxmind", edition="GeoLite2-City"))
    assert repo.get_status("dbip").edition == "city-lite"  # type: ignore[union-attr]
    assert repo.get_status("maxmind").edition == "GeoLite2-City"  # type: ignore[union-attr]
