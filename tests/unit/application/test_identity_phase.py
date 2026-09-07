# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone

from omega_track.application.exceptions import CollectorUnavailableError
from omega_track.application.orchestrators._context import PhaseContext
from omega_track.application.orchestrators.cancellation import CancellationToken
from omega_track.application.orchestrators.phases.identity_phase import run_identity_phase
from omega_track.core.enums import ConfidenceLevel
from omega_track.domain.entities.findings.dns import DnsFindingType
from omega_track.domain.entities.track_profile import ExecutionLimits
from omega_track.domain.entities.track_run import ModuleRun
from omega_track.domain.value_objects.collected_record import CollectedRecord
from omega_track.domain.value_objects.collection_mode import CollectionMode
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.domain.value_objects.identifiers import ModuleRunId, TrackRunId
from omega_track.domain.value_objects.ip_address import IPAddress
from omega_track.domain.value_objects.statuses import ModuleStatus

_NOW = datetime(2026, 9, 6, tzinfo=timezone.utc)
_LIMITS = ExecutionLimits(max_ipv4_enriched=1, max_ipv6_enriched=1, max_neotrace_ips=3)


class _FakeEventPublisher:
    def __init__(self) -> None:
        self.module_statuses: list[tuple[str, str]] = []

    def publish_progress(self, track_run_id: TrackRunId, message: str, percentage: float) -> None:
        pass

    def publish_module_status(self, track_run_id: TrackRunId, module_name: str, status: ModuleStatus) -> None:
        self.module_statuses.append((module_name, status.value))


class _FakeDnsCollector:
    def __init__(
        self,
        *,
        resolve_records: list[CollectedRecord] | None = None,
        resolve_error: Exception | None = None,
        ptr_record: CollectedRecord | None = None,
    ) -> None:
        self._resolve_records = resolve_records or []
        self._resolve_error = resolve_error
        self._ptr_record = ptr_record

    def resolve(self, domain: DomainName) -> list[CollectedRecord]:
        if self._resolve_error is not None:
            raise self._resolve_error
        return self._resolve_records

    def reverse_lookup(self, ip: IPAddress) -> CollectedRecord | None:
        return self._ptr_record


class _FakeRdapCollector:
    def __init__(
        self,
        *,
        domain_records: list[CollectedRecord] | None = None,
        domain_error: Exception | None = None,
        ip_records: dict[str, list[CollectedRecord]] | None = None,
        ip_errors: set[str] | None = None,
    ) -> None:
        self._domain_records = domain_records or []
        self._domain_error = domain_error
        self._ip_records = ip_records or {}
        self._ip_errors = ip_errors or set()
        self.ip_calls: list[str] = []

    def collect_domain_registration(self, domain: DomainName) -> list[CollectedRecord]:
        if self._domain_error is not None:
            raise self._domain_error
        return self._domain_records

    def collect_ip_registration(self, ip: IPAddress) -> list[CollectedRecord]:
        self.ip_calls.append(str(ip))
        if str(ip) in self._ip_errors:
            raise CollectorUnavailableError("rdap")
        return self._ip_records.get(str(ip), [])


def _context(*, cancelled: bool = False) -> PhaseContext:
    token = CancellationToken()
    if cancelled:
        token.cancel()
    return PhaseContext(
        track_run_id=TrackRunId("run-1"),
        id_factory=_id_factory(),
        now=lambda: _NOW,
        event_publisher=_FakeEventPublisher(),
        cancellation_token=token,
    )


def _id_factory() -> Callable[[], str]:
    counter = iter(f"id-{n}" for n in range(1, 1000))
    return counter.__next__


def _module_runs(*names: str) -> dict[str, ModuleRun]:
    return {
        name: ModuleRun(id=ModuleRunId(f"mr-{name}"), module_name=name, status=ModuleStatus.PENDING, collection_mode=CollectionMode.ACTIVE_LIGHT)
        for name in names
    }


def _a_record(address: str) -> CollectedRecord:
    return CollectedRecord(
        finding_type=DnsFindingType.A_RECORD.value,
        payload={"address": address},
        confidence=ConfidenceLevel.VERIFIED,
        source_name="dns",
        observed_at=_NOW,
    )


def test_dns_module_resolves_and_completes() -> None:
    context = _context()
    module_runs = _module_runs("dns")
    collector = _FakeDnsCollector(resolve_records=[_a_record("1.1.1.1"), _a_record("1.1.1.2")])

    result = run_identity_phase(
        context=context,
        module_runs=module_runs,
        target_value=DomainName.parse("example.com"),
        limits=ExecutionLimits(),
        dns_collector=collector,
        rdap_collector=_FakeRdapCollector(),
    )

    assert module_runs["dns"].status == ModuleStatus.COMPLETED
    assert result.resolved_ips == [IPAddress.parse("1.1.1.1"), IPAddress.parse("1.1.1.2")]
    assert len(result.findings) == 2
    assert not result.degraded


def test_dns_module_skipped_when_target_is_ip() -> None:
    context = _context()
    module_runs = _module_runs("dns")
    result = run_identity_phase(
        context=context,
        module_runs=module_runs,
        target_value=IPAddress.parse("1.1.1.1"),
        limits=_LIMITS,
        dns_collector=_FakeDnsCollector(),
        rdap_collector=_FakeRdapCollector(),
    )
    assert module_runs["dns"].status == ModuleStatus.SKIPPED
    assert result.resolved_ips == [IPAddress.parse("1.1.1.1")]
    assert not result.degraded


def test_dns_module_failure_marks_degraded() -> None:
    context = _context()
    module_runs = _module_runs("dns")
    collector = _FakeDnsCollector(resolve_error=CollectorUnavailableError("dns"))

    result = run_identity_phase(
        context=context,
        module_runs=module_runs,
        target_value=DomainName.parse("example.com"),
        limits=_LIMITS,
        dns_collector=collector,
        rdap_collector=_FakeRdapCollector(),
    )

    assert module_runs["dns"].status == ModuleStatus.FAILED
    assert module_runs["dns"].error_code == "collector_unavailable"
    assert result.degraded
    assert result.findings == []


def test_reverse_dns_skipped_without_resolved_ip() -> None:
    context = _context()
    module_runs = _module_runs("reverse_dns")
    result = run_identity_phase(
        context=context,
        module_runs=module_runs,
        target_value=DomainName.parse("example.com"),
        limits=_LIMITS,
        dns_collector=_FakeDnsCollector(),
        rdap_collector=_FakeRdapCollector(),
    )
    assert module_runs["reverse_dns"].status == ModuleStatus.SKIPPED
    assert not result.degraded


def test_reverse_dns_completes_with_ptr_record() -> None:
    context = _context()
    module_runs = _module_runs("reverse_dns")
    ptr = CollectedRecord(
        finding_type=DnsFindingType.PTR_RECORD.value,
        payload={"hostname": "host.example.com"},
        confidence=ConfidenceLevel.VERIFIED,
        source_name="dns",
        observed_at=_NOW,
    )
    result = run_identity_phase(
        context=context,
        module_runs=module_runs,
        target_value=IPAddress.parse("1.1.1.1"),
        limits=_LIMITS,
        dns_collector=_FakeDnsCollector(ptr_record=ptr),
        rdap_collector=_FakeRdapCollector(),
    )
    assert module_runs["reverse_dns"].status == ModuleStatus.COMPLETED
    assert len(result.findings) == 1
    assert result.findings[0].finding_type == "dns.ptr_record"


def test_excess_ips_become_raw_ip_observed_findings() -> None:
    context = _context()
    module_runs = _module_runs("dns")
    collector = _FakeDnsCollector(resolve_records=[_a_record("1.1.1.1"), _a_record("1.1.1.2")])

    result = run_identity_phase(
        context=context,
        module_runs=module_runs,
        target_value=DomainName.parse("example.com"),
        limits=_LIMITS,  # max_ipv4_enriched=1
        dns_collector=collector,
        rdap_collector=_FakeRdapCollector(),
    )

    ip_observed = [f for f in result.findings if f.finding_type == "network.ip_observed"]
    assert len(ip_observed) == 1
    assert ip_observed[0].payload == {"address": "1.1.1.2"}
    assert ip_observed[0].module_run_id == "mr-dns"


def test_rdap_module_completes_for_domain_and_ips() -> None:
    context = _context()
    module_runs = _module_runs("dns", "rdap")
    registrar_record = CollectedRecord(
        finding_type="identity.registrar",
        payload={"name": "Example Registrar"},
        confidence=ConfidenceLevel.DECLARED,
        source_name="rdap",
        observed_at=_NOW,
    )
    dns_collector = _FakeDnsCollector(resolve_records=[_a_record("1.1.1.1")])
    rdap_collector = _FakeRdapCollector(domain_records=[registrar_record])

    result = run_identity_phase(
        context=context,
        module_runs=module_runs,
        target_value=DomainName.parse("example.com"),
        limits=_LIMITS,
        dns_collector=dns_collector,
        rdap_collector=rdap_collector,
    )

    assert module_runs["rdap"].status == ModuleStatus.COMPLETED
    assert rdap_collector.ip_calls == ["1.1.1.1"]
    assert not result.degraded


def test_rdap_module_partial_when_one_ip_fails() -> None:
    context = _context()
    module_runs = _module_runs("dns", "rdap")
    dns_collector = _FakeDnsCollector(resolve_records=[_a_record("1.1.1.1")])
    rdap_collector = _FakeRdapCollector(domain_records=[], ip_errors={"1.1.1.1"})

    result = run_identity_phase(
        context=context,
        module_runs=module_runs,
        target_value=DomainName.parse("example.com"),
        limits=_LIMITS,
        dns_collector=dns_collector,
        rdap_collector=rdap_collector,
    )

    # domaine reussi (liste vide mais pas d'exception) + IP en echec -> PARTIAL
    assert module_runs["rdap"].status == ModuleStatus.PARTIAL
    assert result.degraded


def test_rdap_module_failed_when_everything_fails() -> None:
    context = _context()
    module_runs = _module_runs("rdap")
    rdap_collector = _FakeRdapCollector(domain_error=CollectorUnavailableError("rdap"))

    result = run_identity_phase(
        context=context,
        module_runs=module_runs,
        target_value=DomainName.parse("example.com"),
        limits=_LIMITS,
        dns_collector=_FakeDnsCollector(),
        rdap_collector=rdap_collector,
    )

    assert module_runs["rdap"].status == ModuleStatus.FAILED
    assert result.degraded


def test_rdap_module_skipped_when_cancelled_before_start() -> None:
    context = _context(cancelled=True)
    module_runs = _module_runs("rdap")

    result = run_identity_phase(
        context=context,
        module_runs=module_runs,
        target_value=DomainName.parse("example.com"),
        limits=_LIMITS,
        dns_collector=_FakeDnsCollector(),
        rdap_collector=_FakeRdapCollector(),
    )

    assert module_runs["rdap"].status == ModuleStatus.SKIPPED
    assert not result.degraded
