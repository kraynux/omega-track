# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from datetime import datetime, timezone

from omega_track.application.exceptions import CollectorUnavailableError, QuotaExceededError
from omega_track.application.orchestrators._context import PhaseContext
from omega_track.application.orchestrators.cancellation import CancellationToken
from omega_track.application.orchestrators.phases.reputation_phase import run_reputation_phase
from omega_track.application.policies.quota_backoff import is_in_backoff, record_quota_exceeded
from omega_track.core.enums import ConfidenceLevel
from omega_track.domain.entities.track_run import ModuleRun
from omega_track.domain.value_objects.collected_record import CollectedRecord
from omega_track.domain.value_objects.collection_mode import CollectionMode
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.domain.value_objects.identifiers import ModuleRunId, TrackRunId
from omega_track.domain.value_objects.ip_address import IPAddress
from omega_track.domain.value_objects.statuses import ModuleStatus

_NOW = datetime(2026, 9, 6, tzinfo=timezone.utc)


class _FakeEventPublisher:
    def publish_progress(self, track_run_id: object, message: str, percentage: float) -> None:
        pass

    def publish_module_status(self, track_run_id: object, module_name: str, status: object) -> None:
        pass


class _FakeSecretStore:
    def __init__(self, secrets: dict[str, str] | None = None) -> None:
        self._secrets = dict(secrets or {})

    def get_secret(self, key: str) -> str | None:
        return self._secrets.get(key)

    def set_secret(self, key: str, value: str) -> None:
        self._secrets[key] = value

    def delete_secret(self, key: str) -> None:
        self._secrets.pop(key, None)


class _FakeSettingsRepository:
    def __init__(self) -> None:
        self._data: dict[str, str] = {}

    def get(self, key: str, default: str | None = None) -> str | None:
        return self._data.get(key, default)

    def set(self, key: str, value: str) -> None:
        self._data[key] = value

    def all(self) -> dict[str, str]:
        return dict(self._data)


class _FakeReputationCollector:
    def __init__(self, *, error: Exception | None = None) -> None:
        self._error = error
        self.called = False

    def collect_domain_reputation(self, domain: DomainName) -> list[CollectedRecord]:
        self.called = True
        if self._error is not None:
            raise self._error
        return [_record("reputation.verdict")]


def _record(finding_type: str) -> CollectedRecord:
    return CollectedRecord(
        finding_type=finding_type, payload={}, confidence=ConfidenceLevel.DECLARED,
        source_name="test", observed_at=_NOW,
    )


def _context(*, cancelled: bool = False) -> PhaseContext:
    token = CancellationToken()
    if cancelled:
        token.cancel()
    counter = iter(f"id-{n}" for n in range(1, 1000))
    return PhaseContext(
        track_run_id=TrackRunId("run-1"), id_factory=counter.__next__, now=lambda: _NOW,
        event_publisher=_FakeEventPublisher(), cancellation_token=token,
    )


def _module_runs(*names: str) -> dict[str, ModuleRun]:
    return {
        name: ModuleRun(
            id=ModuleRunId(f"mr-{name}"), module_name=name, status=ModuleStatus.PENDING,
            collection_mode=CollectionMode.API_KEY,
        )
        for name in names
    }


def test_virustotal_completes_when_key_configured() -> None:
    module_runs = _module_runs("virustotal")
    result = run_reputation_phase(
        context=_context(), module_runs=module_runs, target_value=DomainName.parse("example.com"),
        virustotal_collector=_FakeReputationCollector(), hibp_collector=None,
        secret_store=_FakeSecretStore({"virustotal_api_key": "key"}), settings_repository=_FakeSettingsRepository(),
    )
    assert module_runs["virustotal"].status == ModuleStatus.COMPLETED
    assert len(result.findings) == 1
    assert not result.degraded


def test_skipped_for_ip_target() -> None:
    module_runs = _module_runs("virustotal")
    result = run_reputation_phase(
        context=_context(), module_runs=module_runs, target_value=IPAddress.parse("1.1.1.1"),
        virustotal_collector=_FakeReputationCollector(), hibp_collector=None,
        secret_store=_FakeSecretStore({"virustotal_api_key": "key"}), settings_repository=_FakeSettingsRepository(),
    )
    assert module_runs["virustotal"].status == ModuleStatus.SKIPPED
    assert not result.degraded


def test_skipped_when_no_collector_configured() -> None:
    module_runs = _module_runs("virustotal")
    result = run_reputation_phase(
        context=_context(), module_runs=module_runs, target_value=DomainName.parse("example.com"),
        virustotal_collector=None, hibp_collector=None,
        secret_store=_FakeSecretStore(), settings_repository=_FakeSettingsRepository(),
    )
    assert module_runs["virustotal"].status == ModuleStatus.SKIPPED
    assert module_runs["virustotal"].error_detail == "aucun collecteur virustotal configuré"
    assert not result.degraded


def test_skipped_with_not_executed_no_key_when_key_missing() -> None:
    module_runs = _module_runs("virustotal")
    collector = _FakeReputationCollector()
    result = run_reputation_phase(
        context=_context(), module_runs=module_runs, target_value=DomainName.parse("example.com"),
        virustotal_collector=collector, hibp_collector=None,
        secret_store=_FakeSecretStore(), settings_repository=_FakeSettingsRepository(),
    )
    assert module_runs["virustotal"].status == ModuleStatus.SKIPPED
    assert not collector.called
    assert len(result.findings) == 1
    assert result.findings[0].finding_type == "collection.not_executed_no_key"
    assert not result.degraded


def test_skipped_with_quota_exceeded_when_in_backoff_without_calling_collector() -> None:
    module_runs = _module_runs("virustotal")
    settings_repository = _FakeSettingsRepository()
    record_quota_exceeded(settings_repository=settings_repository, source_name="virustotal", now=lambda: _NOW)
    collector = _FakeReputationCollector()

    result = run_reputation_phase(
        context=_context(), module_runs=module_runs, target_value=DomainName.parse("example.com"),
        virustotal_collector=collector, hibp_collector=None,
        secret_store=_FakeSecretStore({"virustotal_api_key": "key"}), settings_repository=settings_repository,
    )
    assert module_runs["virustotal"].status == ModuleStatus.SKIPPED
    assert not collector.called
    assert result.findings[0].finding_type == "collection.quota_exceeded"
    assert not result.degraded


def test_quota_exceeded_during_call_records_backoff_and_fails() -> None:
    module_runs = _module_runs("virustotal")
    settings_repository = _FakeSettingsRepository()
    collector = _FakeReputationCollector(error=QuotaExceededError("virustotal"))

    result = run_reputation_phase(
        context=_context(), module_runs=module_runs, target_value=DomainName.parse("example.com"),
        virustotal_collector=collector, hibp_collector=None,
        secret_store=_FakeSecretStore({"virustotal_api_key": "key"}), settings_repository=settings_repository,
    )
    assert module_runs["virustotal"].status == ModuleStatus.FAILED
    assert module_runs["virustotal"].error_code == "quota_exceeded"
    assert result.degraded
    assert is_in_backoff(settings_repository=settings_repository, source_name="virustotal", now=lambda: _NOW)


def test_collector_unavailable_fails_without_recording_backoff() -> None:
    module_runs = _module_runs("virustotal")
    settings_repository = _FakeSettingsRepository()
    collector = _FakeReputationCollector(error=CollectorUnavailableError("virustotal"))

    result = run_reputation_phase(
        context=_context(), module_runs=module_runs, target_value=DomainName.parse("example.com"),
        virustotal_collector=collector, hibp_collector=None,
        secret_store=_FakeSecretStore({"virustotal_api_key": "key"}), settings_repository=settings_repository,
    )
    assert module_runs["virustotal"].status == ModuleStatus.FAILED
    assert module_runs["virustotal"].error_code == "collector_unavailable"
    assert result.degraded
    assert not is_in_backoff(settings_repository=settings_repository, source_name="virustotal", now=lambda: _NOW)


def test_hibp_and_virustotal_are_independent_modules() -> None:
    module_runs = _module_runs("virustotal", "hibp")
    result = run_reputation_phase(
        context=_context(), module_runs=module_runs, target_value=DomainName.parse("example.com"),
        virustotal_collector=_FakeReputationCollector(), hibp_collector=None,
        secret_store=_FakeSecretStore({"virustotal_api_key": "key"}), settings_repository=_FakeSettingsRepository(),
    )
    assert module_runs["virustotal"].status == ModuleStatus.COMPLETED
    assert module_runs["hibp"].status == ModuleStatus.SKIPPED
    assert module_runs["hibp"].error_detail == "aucun collecteur hibp configuré"
    assert len(result.findings) == 1


def test_cancelled_before_start_skips_all_enabled_modules() -> None:
    module_runs = _module_runs("virustotal", "hibp")
    result = run_reputation_phase(
        context=_context(cancelled=True), module_runs=module_runs, target_value=DomainName.parse("example.com"),
        virustotal_collector=_FakeReputationCollector(), hibp_collector=_FakeReputationCollector(),
        secret_store=_FakeSecretStore({"virustotal_api_key": "key", "hibp_api_key": "key"}),
        settings_repository=_FakeSettingsRepository(),
    )
    assert all(mr.status == ModuleStatus.SKIPPED for mr in module_runs.values())
    assert result.findings == []


def test_modules_not_in_profile_are_left_untouched() -> None:
    module_runs: dict[str, ModuleRun] = {}
    result = run_reputation_phase(
        context=_context(), module_runs=module_runs, target_value=DomainName.parse("example.com"),
        virustotal_collector=_FakeReputationCollector(), hibp_collector=_FakeReputationCollector(),
        secret_store=_FakeSecretStore({"virustotal_api_key": "key", "hibp_api_key": "key"}),
        settings_repository=_FakeSettingsRepository(),
    )
    assert result.findings == []
    assert not result.degraded
