# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from omega_track.application.policies.quota_backoff import (
    DEFAULT_BACKOFF,
    backoff_setting_key,
    is_in_backoff,
    record_quota_exceeded,
)

_NOW = datetime(2026, 9, 7, tzinfo=timezone.utc)


class _FakeSettingsRepository:
    def __init__(self) -> None:
        self._data: dict[str, str] = {}

    def get(self, key: str, default: str | None = None) -> str | None:
        return self._data.get(key, default)

    def set(self, key: str, value: str) -> None:
        self._data[key] = value

    def all(self) -> dict[str, str]:
        return dict(self._data)


def test_no_backoff_recorded_means_not_in_backoff() -> None:
    repo = _FakeSettingsRepository()
    assert not is_in_backoff(settings_repository=repo, source_name="virustotal", now=lambda: _NOW)


def test_record_quota_exceeded_puts_source_in_backoff() -> None:
    repo = _FakeSettingsRepository()
    record_quota_exceeded(settings_repository=repo, source_name="virustotal", now=lambda: _NOW)
    assert is_in_backoff(settings_repository=repo, source_name="virustotal", now=lambda: _NOW)


def test_backoff_expires_after_the_configured_delay() -> None:
    repo = _FakeSettingsRepository()
    record_quota_exceeded(
        settings_repository=repo, source_name="virustotal", now=lambda: _NOW, backoff=timedelta(minutes=1)
    )
    later = _NOW + timedelta(minutes=2)
    assert not is_in_backoff(settings_repository=repo, source_name="virustotal", now=lambda: later)


def test_backoff_is_per_source_not_shared() -> None:
    repo = _FakeSettingsRepository()
    record_quota_exceeded(settings_repository=repo, source_name="virustotal", now=lambda: _NOW)
    assert not is_in_backoff(settings_repository=repo, source_name="hibp", now=lambda: _NOW)


def test_default_backoff_is_a_defensive_internal_policy_not_zero() -> None:
    assert DEFAULT_BACKOFF > timedelta(0)


def test_backoff_setting_key_is_namespaced_per_source() -> None:
    assert backoff_setting_key("virustotal") != backoff_setting_key("hibp")
