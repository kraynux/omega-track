# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from omega_track.application.queries.diagnostics import run_diagnostics
from omega_track.application.queries.get_settings import get_settings
from omega_track.core.constants import APP_VERSION, EXPORT_SCHEMA_VERSION
from omega_track.domain.entities.findings.path import NetworkPath
from omega_track.domain.entities.geoip_database_status import GeoIpDatabaseStatus
from omega_track.domain.entities.track_profile import NeoTraceOptions
from omega_track.domain.value_objects.ip_address import IPAddress

_NOW = datetime(2026, 9, 6, tzinfo=timezone.utc)


class _FakeSettingsRepository:
    def __init__(self, data: dict[str, str]) -> None:
        self._data = data

    def get(self, key: str, default: str | None = None) -> str | None:
        return self._data.get(key, default)

    def set(self, key: str, value: str) -> None:
        self._data[key] = value

    def all(self) -> dict[str, str]:
        return dict(self._data)


class _FakeTracerouteCollector:
    def __init__(self, *, available: bool) -> None:
        self._available = available

    def is_available(self) -> bool:
        return self._available

    def trace(self, target_ip: IPAddress, options: NeoTraceOptions) -> NetworkPath:
        raise AssertionError("non exerce par diagnostics")


class _FakeGeoipDatabaseRepository:
    def __init__(self, status: GeoIpDatabaseStatus | None) -> None:
        self._status = status

    def save_status(self, status: GeoIpDatabaseStatus) -> None:
        pass

    def get_status(self, provider: str) -> GeoIpDatabaseStatus | None:
        return self._status


def test_get_settings_returns_all_entries() -> None:
    repo = _FakeSettingsRepository({"theme": "dark", "geoip_provider": "dbip"})
    assert get_settings(settings_repository=repo) == {"theme": "dark", "geoip_provider": "dbip"}


def test_diagnostics_reports_versions_and_traceroute_availability() -> None:
    report = run_diagnostics(
        traceroute_collector=_FakeTracerouteCollector(available=True),
        geoip_database_repository=_FakeGeoipDatabaseRepository(None),
        geoip_provider="dbip",
        var_dir=Path("/var/omega-track"),
        now=lambda: _NOW,
    )
    assert report.app_version == APP_VERSION
    assert report.schema_version == EXPORT_SCHEMA_VERSION
    assert report.var_dir == "/var/omega-track"
    assert report.traceroute_available
    assert report.geoip_status.status is None
    assert report.geoip_status.is_stale


def test_diagnostics_reports_traceroute_unavailable() -> None:
    report = run_diagnostics(
        traceroute_collector=_FakeTracerouteCollector(available=False),
        geoip_database_repository=_FakeGeoipDatabaseRepository(None),
        geoip_provider="dbip",
        var_dir=Path("/var/omega-track"),
        now=lambda: _NOW,
    )
    assert not report.traceroute_available
