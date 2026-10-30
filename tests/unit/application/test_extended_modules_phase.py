# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from datetime import datetime, timezone

from omega_track.application.exceptions import CollectorUnavailableError
from omega_track.application.orchestrators._context import PhaseContext
from omega_track.application.orchestrators.cancellation import CancellationToken
from omega_track.application.orchestrators.phases.extended_modules_phase import (
    run_extended_modules_phase,
)
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


class _FakeCtCollector:
    def __init__(self, *, error: Exception | None = None) -> None:
        self._error = error

    def collect_certificates(self, domain: DomainName) -> list[CollectedRecord]:
        if self._error is not None:
            raise self._error
        return [_record("certificate.observed")]

    def distinct_log_count(self, domain: DomainName) -> int:
        return 1


class _FakeArchiveCollector:
    def __init__(self, *, error: Exception | None = None) -> None:
        self._error = error

    def collect_snapshots(self, domain: DomainName) -> list[CollectedRecord]:
        if self._error is not None:
            raise self._error
        return [_record("history.archive_snapshot")]


class _FakeBgpCollector:
    def __init__(self, *, errors: set[str] | None = None) -> None:
        self._errors = errors or set()
        self.calls: list[str] = []

    def collect_announcements(self, ip: IPAddress) -> list[CollectedRecord]:
        self.calls.append(str(ip))
        if str(ip) in self._errors:
            raise CollectorUnavailableError("ripestat")
        return [_record("network.asn")]


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
            collection_mode=CollectionMode.PASSIVE_PUBLIC,
        )
        for name in names
    }


def test_ct_module_completes_for_domain_target() -> None:
    module_runs = _module_runs("certificate_transparency")
    result = run_extended_modules_phase(
        context=_context(), module_runs=module_runs, target_value=DomainName.parse("example.com"),
        enriched_ips=[], ct_collector=_FakeCtCollector(), archive_collector=None, bgp_collector=None,
    )
    assert module_runs["certificate_transparency"].status == ModuleStatus.COMPLETED
    assert len(result.findings) == 1
    assert not result.degraded


def test_ct_module_skipped_for_ip_target() -> None:
    module_runs = _module_runs("certificate_transparency")
    result = run_extended_modules_phase(
        context=_context(), module_runs=module_runs, target_value=IPAddress.parse("1.1.1.1"),
        enriched_ips=[], ct_collector=_FakeCtCollector(), archive_collector=None, bgp_collector=None,
    )
    assert module_runs["certificate_transparency"].status == ModuleStatus.SKIPPED
    assert not result.degraded


def test_ct_module_skipped_when_no_collector_configured() -> None:
    module_runs = _module_runs("certificate_transparency")
    result = run_extended_modules_phase(
        context=_context(), module_runs=module_runs, target_value=DomainName.parse("example.com"),
        enriched_ips=[], ct_collector=None, archive_collector=None, bgp_collector=None,
    )
    assert module_runs["certificate_transparency"].status == ModuleStatus.SKIPPED
    assert module_runs["certificate_transparency"].error_detail == "aucun collecteur Certificate Transparency configuré"
    assert not result.degraded


def test_ct_module_failed_when_collector_unavailable() -> None:
    module_runs = _module_runs("certificate_transparency")
    result = run_extended_modules_phase(
        context=_context(), module_runs=module_runs, target_value=DomainName.parse("example.com"),
        enriched_ips=[], ct_collector=_FakeCtCollector(error=CollectorUnavailableError("crt.sh")),
        archive_collector=None, bgp_collector=None,
    )
    assert module_runs["certificate_transparency"].status == ModuleStatus.FAILED
    assert result.degraded


def test_archives_module_completes_for_domain_target() -> None:
    module_runs = _module_runs("archives")
    result = run_extended_modules_phase(
        context=_context(), module_runs=module_runs, target_value=DomainName.parse("example.com"),
        enriched_ips=[], ct_collector=None, archive_collector=_FakeArchiveCollector(), bgp_collector=None,
    )
    assert module_runs["archives"].status == ModuleStatus.COMPLETED
    assert len(result.findings) == 1


def test_archives_module_failed_when_collector_unavailable() -> None:
    module_runs = _module_runs("archives")
    result = run_extended_modules_phase(
        context=_context(), module_runs=module_runs, target_value=DomainName.parse("example.com"),
        enriched_ips=[], ct_collector=None, archive_collector=_FakeArchiveCollector(error=CollectorUnavailableError("wayback")),
        bgp_collector=None,
    )
    assert module_runs["archives"].status == ModuleStatus.FAILED
    assert result.degraded


def test_bgp_module_completes_across_multiple_ips() -> None:
    module_runs = _module_runs("bgp")
    ips = [IPAddress.parse("1.1.1.1"), IPAddress.parse("2.2.2.2")]
    collector = _FakeBgpCollector()
    result = run_extended_modules_phase(
        context=_context(), module_runs=module_runs, target_value=DomainName.parse("example.com"),
        enriched_ips=ips, ct_collector=None, archive_collector=None, bgp_collector=collector,
    )
    assert module_runs["bgp"].status == ModuleStatus.COMPLETED
    assert len(result.findings) == 2
    assert collector.calls == ["1.1.1.1", "2.2.2.2"]


def test_bgp_module_partial_when_one_ip_fails() -> None:
    module_runs = _module_runs("bgp")
    ips = [IPAddress.parse("1.1.1.1"), IPAddress.parse("2.2.2.2")]
    collector = _FakeBgpCollector(errors={"2.2.2.2"})
    result = run_extended_modules_phase(
        context=_context(), module_runs=module_runs, target_value=DomainName.parse("example.com"),
        enriched_ips=ips, ct_collector=None, archive_collector=None, bgp_collector=collector,
    )
    assert module_runs["bgp"].status == ModuleStatus.PARTIAL
    assert result.degraded


def test_bgp_module_skipped_when_no_ips() -> None:
    module_runs = _module_runs("bgp")
    run_extended_modules_phase(
        context=_context(), module_runs=module_runs, target_value=DomainName.parse("example.com"),
        enriched_ips=[], ct_collector=None, archive_collector=None, bgp_collector=_FakeBgpCollector(),
    )
    assert module_runs["bgp"].status == ModuleStatus.SKIPPED


def test_modules_not_in_profile_are_left_untouched() -> None:
    module_runs: dict[str, ModuleRun] = {}
    result = run_extended_modules_phase(
        context=_context(), module_runs=module_runs, target_value=DomainName.parse("example.com"),
        enriched_ips=[], ct_collector=_FakeCtCollector(), archive_collector=_FakeArchiveCollector(),
        bgp_collector=_FakeBgpCollector(),
    )
    assert result.findings == []
    assert not result.degraded


def test_cancelled_before_start_skips_all_enabled_modules() -> None:
    module_runs = _module_runs("certificate_transparency", "archives", "bgp")
    result = run_extended_modules_phase(
        context=_context(cancelled=True), module_runs=module_runs, target_value=DomainName.parse("example.com"),
        enriched_ips=[IPAddress.parse("1.1.1.1")], ct_collector=_FakeCtCollector(),
        archive_collector=_FakeArchiveCollector(), bgp_collector=_FakeBgpCollector(),
    )
    assert all(mr.status == ModuleStatus.SKIPPED for mr in module_runs.values())
    assert result.findings == []
