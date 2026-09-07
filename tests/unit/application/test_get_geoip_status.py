# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from omega_track.application.queries.get_geoip_status import get_geoip_database_status
from omega_track.domain.entities.geoip_database_status import GeoIpDatabaseStatus

_NOW = datetime(2026, 9, 6, tzinfo=timezone.utc)


class _FakeGeoipDatabaseRepository:
    def __init__(self, status: GeoIpDatabaseStatus | None) -> None:
        self._status = status

    def save_status(self, status: GeoIpDatabaseStatus) -> None:
        self._status = status

    def get_status(self, provider: str) -> GeoIpDatabaseStatus | None:
        return self._status


def _status(downloaded_at: datetime) -> GeoIpDatabaseStatus:
    return GeoIpDatabaseStatus(
        provider="dbip",
        edition="City Lite",
        local_path="/var/geoip/dbip-city.mmdb",
        checksum="deadbeef",
        downloaded_at=downloaded_at,
        published_at=None,
        status="ok",
    )


def test_missing_status_is_reported_as_stale_without_downloading() -> None:
    repo = _FakeGeoipDatabaseRepository(None)
    view = get_geoip_database_status(geoip_database_repository=repo, provider="dbip", now=lambda: _NOW)
    assert view.status is None
    assert view.age is None
    assert view.is_stale


def test_fresh_status_is_not_stale() -> None:
    repo = _FakeGeoipDatabaseRepository(_status(_NOW - timedelta(days=1)))
    view = get_geoip_database_status(geoip_database_repository=repo, provider="dbip", now=lambda: _NOW)
    assert view.status is not None
    assert view.age == timedelta(days=1)
    assert not view.is_stale


def test_old_status_is_stale() -> None:
    repo = _FakeGeoipDatabaseRepository(_status(_NOW - timedelta(days=90)))
    view = get_geoip_database_status(geoip_database_repository=repo, provider="dbip", now=lambda: _NOW)
    assert view.is_stale
