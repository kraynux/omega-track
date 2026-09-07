# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from omega_track.application.commands.geoip.initialize_database import initialize_geoip_database
from omega_track.application.commands.geoip.update_database import update_geoip_database
from omega_track.application.exceptions import GeoIpDownloadError
from omega_track.domain.entities.geoip_database_status import GeoIpDatabaseStatus

_NOW = datetime(2026, 9, 6, tzinfo=timezone.utc)
_DESTINATION = Path("/var/geoip/dbip-city.mmdb")


class _FakeGeoipDatabaseRepository:
    def __init__(self, status: GeoIpDatabaseStatus | None = None) -> None:
        self._status = status
        self.saved: list[GeoIpDatabaseStatus] = []

    def save_status(self, status: GeoIpDatabaseStatus) -> None:
        self._status = status
        self.saved.append(status)

    def get_status(self, provider: str) -> GeoIpDatabaseStatus | None:
        return self._status


class _FakeDatabaseUpdaterSuccess:
    def __init__(self) -> None:
        self.calls: list[tuple[str, Path]] = []

    def download_latest(self, provider: str, destination: Path) -> GeoIpDatabaseStatus:
        self.calls.append((provider, destination))
        return GeoIpDatabaseStatus(
            provider=provider,
            edition="City Lite",
            local_path=str(destination),
            checksum="fresh-checksum",
            downloaded_at=_NOW,
            published_at=None,
            status="ok",
        )


class _FakeDatabaseUpdaterFailure:
    def download_latest(self, provider: str, destination: Path) -> GeoIpDatabaseStatus:
        raise GeoIpDownloadError("echec simule")


def _ok_status(*, local_path: str) -> GeoIpDatabaseStatus:
    return GeoIpDatabaseStatus(
        provider="dbip",
        edition="City Lite",
        local_path=local_path,
        checksum="old-checksum",
        downloaded_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        published_at=None,
        status="ok",
    )


def test_initialize_skips_download_when_already_ok_and_file_exists(tmp_path: Path) -> None:
    existing_file = tmp_path / "dbip-city.mmdb"
    existing_file.write_bytes(b"already-there")
    repo = _FakeGeoipDatabaseRepository(_ok_status(local_path=str(existing_file)))
    updater = _FakeDatabaseUpdaterSuccess()

    result = initialize_geoip_database(
        geoip_database_repository=repo, database_updater=updater, provider="dbip", destination=existing_file, now=lambda: _NOW
    )

    assert result.checksum == "old-checksum"
    assert updater.calls == []


def test_initialize_downloads_when_no_status_yet() -> None:
    repo = _FakeGeoipDatabaseRepository(None)
    updater = _FakeDatabaseUpdaterSuccess()

    result = initialize_geoip_database(
        geoip_database_repository=repo, database_updater=updater, provider="dbip", destination=_DESTINATION, now=lambda: _NOW
    )

    assert result.status == "ok"
    assert result.checksum == "fresh-checksum"
    assert updater.calls == [("dbip", _DESTINATION)]
    assert repo.saved == [result]


def test_initialize_downloads_when_status_ok_but_file_missing(tmp_path: Path) -> None:
    missing_file = tmp_path / "gone.mmdb"
    repo = _FakeGeoipDatabaseRepository(_ok_status(local_path=str(missing_file)))
    updater = _FakeDatabaseUpdaterSuccess()

    result = initialize_geoip_database(
        geoip_database_repository=repo, database_updater=updater, provider="dbip", destination=missing_file, now=lambda: _NOW
    )

    assert result.checksum == "fresh-checksum"
    assert updater.calls == [("dbip", missing_file)]


def test_update_always_downloads_even_when_already_ok(tmp_path: Path) -> None:
    existing_file = tmp_path / "dbip-city.mmdb"
    existing_file.write_bytes(b"already-there")
    repo = _FakeGeoipDatabaseRepository(_ok_status(local_path=str(existing_file)))
    updater = _FakeDatabaseUpdaterSuccess()

    result = update_geoip_database(
        geoip_database_repository=repo, database_updater=updater, provider="dbip", destination=existing_file, now=lambda: _NOW
    )

    assert result.checksum == "fresh-checksum"
    assert updater.calls == [("dbip", existing_file)]


def test_update_failure_is_non_destructive_and_persists_download_failed_status() -> None:
    repo = _FakeGeoipDatabaseRepository(_ok_status(local_path=str(_DESTINATION)))
    updater = _FakeDatabaseUpdaterFailure()

    result = update_geoip_database(
        geoip_database_repository=repo, database_updater=updater, provider="dbip", destination=_DESTINATION, now=lambda: _NOW
    )

    assert result.status == "download_failed"
    assert result.checksum == "old-checksum"
    assert result.edition == "City Lite"


def test_update_failure_without_previous_status_still_persists() -> None:
    repo = _FakeGeoipDatabaseRepository(None)
    updater = _FakeDatabaseUpdaterFailure()

    result = update_geoip_database(
        geoip_database_repository=repo, database_updater=updater, provider="dbip", destination=_DESTINATION, now=lambda: _NOW
    )

    assert result.status == "download_failed"
    assert result.edition == "inconnue"
    assert result.checksum == ""
