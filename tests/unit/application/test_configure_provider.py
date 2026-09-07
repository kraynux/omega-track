# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from omega_track.application.commands.geoip.configure_provider import (
    configure_maxmind_credentials,
    select_geoip_provider,
    validate_geoip_configuration,
)
from omega_track.application.exceptions import (
    MaxMindCredentialsMissingError,
    UnknownGeoIpProviderError,
)
from omega_track.domain.entities.geoip_database_status import GeoIpDatabaseStatus


class _FakeSettingsRepository:
    def __init__(self) -> None:
        self._data: dict[str, str] = {}

    def get(self, key: str, default: str | None = None) -> str | None:
        return self._data.get(key, default)

    def set(self, key: str, value: str) -> None:
        self._data[key] = value

    def all(self) -> dict[str, str]:
        return dict(self._data)


class _FakeSecretStore:
    def __init__(self) -> None:
        self._data: dict[str, str] = {}

    def get_secret(self, key: str) -> str | None:
        return self._data.get(key)

    def set_secret(self, key: str, value: str) -> None:
        self._data[key] = value

    def delete_secret(self, key: str) -> None:
        self._data.pop(key, None)


class _FakeGeoipDatabaseRepository:
    def __init__(self, status: GeoIpDatabaseStatus | None = None) -> None:
        self._status = status

    def save_status(self, status: GeoIpDatabaseStatus) -> None:
        self._status = status

    def get_status(self, provider: str) -> GeoIpDatabaseStatus | None:
        return self._status


def _ok_status(provider: str) -> GeoIpDatabaseStatus:
    return GeoIpDatabaseStatus(
        provider=provider,
        edition="City Lite",
        local_path="/var/geoip/db.mmdb",
        checksum="abc",
        downloaded_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
        published_at=None,
        status="ok",
    )


def test_select_geoip_provider_persists_valid_choice() -> None:
    settings = _FakeSettingsRepository()
    select_geoip_provider(settings_repository=settings, provider="maxmind")
    assert settings.get("geoip_provider") == "maxmind"


def test_select_geoip_provider_rejects_unknown_provider() -> None:
    settings = _FakeSettingsRepository()
    with pytest.raises(UnknownGeoIpProviderError):
        select_geoip_provider(settings_repository=settings, provider="bogus")


def test_configure_maxmind_credentials_stores_stripped_key() -> None:
    secrets = _FakeSecretStore()
    configure_maxmind_credentials(secret_store=secrets, license_key="  abc123  ")
    assert secrets.get_secret("maxmind_license_key") == "abc123"


def test_configure_maxmind_credentials_rejects_empty_key() -> None:
    secrets = _FakeSecretStore()
    with pytest.raises(MaxMindCredentialsMissingError):
        configure_maxmind_credentials(secret_store=secrets, license_key="   ")


def test_validate_geoip_configuration_ready_for_dbip_with_ok_database() -> None:
    settings = _FakeSettingsRepository()
    secrets = _FakeSecretStore()
    repo = _FakeGeoipDatabaseRepository(_ok_status("dbip"))
    result = validate_geoip_configuration(
        settings_repository=settings, secret_store=secrets, geoip_database_repository=repo
    )
    assert result.provider == "dbip"
    assert result.ready
    assert result.reason is None


def test_validate_geoip_configuration_flags_missing_maxmind_key() -> None:
    settings = _FakeSettingsRepository()
    settings.set("geoip_provider", "maxmind")
    secrets = _FakeSecretStore()
    repo = _FakeGeoipDatabaseRepository(None)
    result = validate_geoip_configuration(
        settings_repository=settings, secret_store=secrets, geoip_database_repository=repo
    )
    assert not result.ready
    assert result.reason == "cle_maxmind_absente"


def test_validate_geoip_configuration_flags_missing_database() -> None:
    settings = _FakeSettingsRepository()
    secrets = _FakeSecretStore()
    repo = _FakeGeoipDatabaseRepository(None)
    result = validate_geoip_configuration(
        settings_repository=settings, secret_store=secrets, geoip_database_repository=repo
    )
    assert not result.ready
    assert result.reason == "base_absente_ou_invalide"
