# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from omega_track.application.commands.reputation.clear_source_key import clear_source_key
from omega_track.application.commands.reputation.configure_source_key import configure_source_key
from omega_track.application.exceptions import ApiKeyMissingError, UnknownReputationSourceError
from omega_track.application.policies.quota_backoff import record_quota_exceeded
from omega_track.application.queries.get_source_disclosure import (
    get_source_disclosure,
    list_known_reputation_sources,
    secret_name_for,
)
from omega_track.application.queries.get_source_status import get_source_status

_NOW = datetime(2026, 9, 7, tzinfo=timezone.utc)


class _FakeSecretStore:
    def __init__(self) -> None:
        self._data: dict[str, str] = {}

    def get_secret(self, key: str) -> str | None:
        return self._data.get(key)

    def set_secret(self, key: str, value: str) -> None:
        self._data[key] = value

    def delete_secret(self, key: str) -> None:
        self._data.pop(key, None)


class _FakeSettingsRepository:
    def __init__(self) -> None:
        self._data: dict[str, str] = {}

    def get(self, key: str, default: str | None = None) -> str | None:
        return self._data.get(key, default)

    def set(self, key: str, value: str) -> None:
        self._data[key] = value

    def all(self) -> dict[str, str]:
        return dict(self._data)


def test_list_known_reputation_sources_contains_virustotal_and_hibp() -> None:
    assert list_known_reputation_sources() == ["hibp", "virustotal"]


def test_get_source_disclosure_flags_hibp_as_paid_and_virustotal_as_not() -> None:
    assert get_source_disclosure("hibp").is_paid
    assert not get_source_disclosure("virustotal").is_paid


def test_get_source_disclosure_rejects_unknown_source() -> None:
    with pytest.raises(UnknownReputationSourceError):
        get_source_disclosure("bogus")


def test_configure_source_key_stores_stripped_key_under_the_conventional_name() -> None:
    secrets = _FakeSecretStore()
    configure_source_key(secret_store=secrets, source_name="virustotal", api_key="  abc123  ")
    assert secrets.get_secret(secret_name_for("virustotal")) == "abc123"


def test_configure_source_key_rejects_empty_key() -> None:
    secrets = _FakeSecretStore()
    with pytest.raises(ApiKeyMissingError):
        configure_source_key(secret_store=secrets, source_name="virustotal", api_key="   ")


def test_configure_source_key_rejects_unknown_source() -> None:
    secrets = _FakeSecretStore()
    with pytest.raises(UnknownReputationSourceError):
        configure_source_key(secret_store=secrets, source_name="bogus", api_key="key")


def test_clear_source_key_removes_a_configured_key() -> None:
    secrets = _FakeSecretStore()
    configure_source_key(secret_store=secrets, source_name="virustotal", api_key="abc123")
    clear_source_key(secret_store=secrets, source_name="virustotal")
    assert secrets.get_secret(secret_name_for("virustotal")) is None


def test_clear_source_key_is_idempotent_on_an_already_absent_key() -> None:
    secrets = _FakeSecretStore()
    clear_source_key(secret_store=secrets, source_name="virustotal")  # ne leve pas


def test_get_source_status_reports_key_not_configured_by_default() -> None:
    view = get_source_status(
        secret_store=_FakeSecretStore(), settings_repository=_FakeSettingsRepository(),
        source_name="virustotal", now=lambda: _NOW,
    )
    assert not view.key_configured
    assert not view.in_backoff
    assert view.backoff_until is None


def test_get_source_status_reports_key_configured_and_backoff() -> None:
    secrets = _FakeSecretStore()
    configure_source_key(secret_store=secrets, source_name="virustotal", api_key="abc123")
    settings = _FakeSettingsRepository()
    record_quota_exceeded(settings_repository=settings, source_name="virustotal", now=lambda: _NOW)

    view = get_source_status(
        secret_store=secrets, settings_repository=settings, source_name="virustotal", now=lambda: _NOW
    )
    assert view.key_configured
    assert view.in_backoff
    assert view.backoff_until is not None


def test_get_source_status_never_exposes_the_key_value() -> None:
    secrets = _FakeSecretStore()
    configure_source_key(secret_store=secrets, source_name="virustotal", api_key="tres-secrete-cle")
    view = get_source_status(
        secret_store=secrets, settings_repository=_FakeSettingsRepository(),
        source_name="virustotal", now=lambda: _NOW,
    )
    assert "tres-secrete-cle" not in repr(view)
    assert "tres-secrete-cle" not in str(view)
