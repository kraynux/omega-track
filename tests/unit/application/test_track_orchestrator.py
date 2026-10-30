# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta, timezone

from omega_track.application.exceptions import CollectorUnavailableError
from omega_track.application.orchestrators.cancellation import CancellationToken
from omega_track.application.orchestrators.track_orchestrator import TrackOrchestrator
from omega_track.core.enums import ConfidenceLevel
from omega_track.domain.entities.findings.base import Finding
from omega_track.domain.entities.findings.dns import DnsFindingType
from omega_track.domain.entities.findings.path import NetworkHop, NetworkPath
from omega_track.domain.entities.relation import Relation
from omega_track.domain.entities.track_profile import ExecutionLimits, NeoTraceOptions, TrackProfile
from omega_track.domain.entities.track_run import TrackRun
from omega_track.domain.value_objects.collected_record import CollectedRecord
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.domain.value_objects.identifiers import TargetId, TrackProfileId, TrackRunId
from omega_track.domain.value_objects.ip_address import IPAddress
from omega_track.domain.value_objects.statuses import ModuleStatus, TrackStatus
from omega_track.ports.collectors.certificate_transparency_collector import (
    CertificateTransparencyCollector,
)
from omega_track.ports.collectors.dns_collector import DnsCollector
from omega_track.ports.collectors.rdap_collector import RdapCollector
from omega_track.ports.collectors.traceroute_collector import TracerouteCollector

_T0 = datetime(2026, 9, 6, 12, 0, tzinfo=timezone.utc)


class _FakeEventPublisher:
    def publish_progress(self, track_run_id: TrackRunId, message: str, percentage: float) -> None:
        pass

    def publish_module_status(self, track_run_id: TrackRunId, module_name: str, status: ModuleStatus) -> None:
        pass


class _FakeFindingRepository:
    def __init__(self) -> None:
        self.findings: list[Finding] = []
        self.relations: list[Relation] = []

    def save_findings(self, findings: list[Finding]) -> None:
        self.findings.extend(findings)

    def save_relations(self, relations: list[Relation]) -> None:
        self.relations.extend(relations)

    def list_findings_for_run(self, track_run_id: TrackRunId) -> list[Finding]:
        return list(self.findings)

    def list_relations_for_run(self, track_run_id: TrackRunId) -> list[Relation]:
        return list(self.relations)

    def delete_for_run(self, track_run_id: TrackRunId) -> None:
        self.findings = [f for f in self.findings if f.track_run_id != track_run_id]
        self.relations = [r for r in self.relations if r.track_run_id != track_run_id]


class _FakeTrackRunRepository:
    def __init__(self) -> None:
        self.saved: list[TrackRun] = []

    def save(self, run: TrackRun) -> None:
        self.saved.append(run)

    def get(self, track_run_id: TrackRunId) -> TrackRun | None:
        return self.saved[-1] if self.saved else None

    def list_for_target(self, target_id: TargetId) -> list[TrackRun]:
        return []

    def list_recent(self, **kwargs: object) -> list[TrackRun]:
        return []

    def delete(self, track_run_id: TrackRunId) -> None:
        pass


class _FakeDnsCollector:
    def resolve(self, domain: DomainName) -> list[CollectedRecord]:
        return [
            CollectedRecord(
                finding_type=DnsFindingType.A_RECORD.value,
                payload={"address": "1.1.1.1"},
                confidence=ConfidenceLevel.VERIFIED,
                source_name="dns",
                observed_at=_T0,
            )
        ]

    def reverse_lookup(self, ip: IPAddress) -> CollectedRecord | None:
        return None


class _FailingDnsCollector:
    def resolve(self, domain: DomainName) -> list[CollectedRecord]:
        raise CollectorUnavailableError("dns")

    def reverse_lookup(self, ip: IPAddress) -> CollectedRecord | None:
        return None


class _FakeRdapCollector:
    def __init__(self, *, fail: bool = False) -> None:
        self._fail = fail

    def collect_domain_registration(self, domain: DomainName) -> list[CollectedRecord]:
        if self._fail:
            raise CollectorUnavailableError("rdap")
        return []

    def collect_ip_registration(self, ip: IPAddress) -> list[CollectedRecord]:
        if self._fail:
            raise CollectorUnavailableError("rdap")
        return []


class _FakeTracerouteCollector:
    def is_available(self) -> bool:
        return True

    def trace(self, target_ip: IPAddress, options: NeoTraceOptions) -> NetworkPath:
        return NetworkPath(target_ip=target_ip, protocol="icmp", hops=[NetworkHop(sequence=1, ip=target_ip, rtt_ms=1.0)])


class _FakeCtCollector:
    def __init__(self, *, distinct_log_count: int = 1) -> None:
        self._distinct_log_count = distinct_log_count

    def collect_certificates(self, domain: DomainName) -> list[CollectedRecord]:
        return [
            CollectedRecord(
                finding_type="certificate.observed",
                payload={"serial_number": "abc123", "issuer_name": "Let's Encrypt", "not_before": None, "not_after": None},
                confidence=ConfidenceLevel.DECLARED,
                source_name="crt.sh",
                observed_at=_T0,
            )
        ]

    def distinct_log_count(self, domain: DomainName) -> int:
        return self._distinct_log_count


def _clock(start: datetime = _T0, *, step: timedelta = timedelta(seconds=1)) -> Callable[[], datetime]:
    state = {"now": start}

    def now() -> datetime:
        value = state["now"]
        state["now"] = value + step
        return value

    return now


def _id_factory() -> Callable[[], str]:
    counter = iter(f"id-{n}" for n in range(1, 1000))
    return counter.__next__


def _profile(*, modules: set[str], limits: ExecutionLimits | None = None) -> TrackProfile:
    return TrackProfile(
        id=TrackProfileId("profile-1"),
        name="default",
        modules=modules,
        created_at=_T0,
        updated_at=_T0,
        limits=limits or ExecutionLimits(),
    )


def _track_run(profile: TrackProfile) -> TrackRun:
    return TrackRun(
        id=TrackRunId("run-1"),
        target_id=TargetId("target-1"),
        profile_snapshot=profile,
        status=TrackStatus.QUEUED,
        created_at=_T0,
    )


def _orchestrator(
    *,
    dns_collector: DnsCollector | None = None,
    rdap_collector: RdapCollector | None = None,
    traceroute_collector: TracerouteCollector | None = None,
    finding_repository: _FakeFindingRepository | None = None,
    track_run_repository: _FakeTrackRunRepository | None = None,
    now: Callable[[], datetime] | None = None,
    ct_collector: CertificateTransparencyCollector | None = None,
) -> tuple[TrackOrchestrator, _FakeFindingRepository, _FakeTrackRunRepository]:
    findings_repo = finding_repository or _FakeFindingRepository()
    runs_repo = track_run_repository or _FakeTrackRunRepository()
    orchestrator = TrackOrchestrator(
        dns_collector=dns_collector or _FakeDnsCollector(),
        rdap_collector=rdap_collector or _FakeRdapCollector(),
        traceroute_collector=traceroute_collector or _FakeTracerouteCollector(),
        finding_repository=findings_repo,
        track_run_repository=runs_repo,
        event_publisher=_FakeEventPublisher(),
        id_factory=_id_factory(),
        now=now or _clock(),
        ct_collector=ct_collector,
    )
    return orchestrator, findings_repo, runs_repo


def test_happy_path_completes_and_persists_findings_and_relations() -> None:
    profile = _profile(modules={"dns", "rdap", "neotrace"})
    track_run = _track_run(profile)
    orchestrator, findings_repo, runs_repo = _orchestrator()

    result = orchestrator.run(track_run=track_run, target_value=DomainName.parse("example.com"))

    assert result.status == TrackStatus.COMPLETED
    assert result.module_runs["dns"].status == ModuleStatus.COMPLETED
    assert result.module_runs["rdap"].status == ModuleStatus.COMPLETED
    assert result.module_runs["neotrace"].status == ModuleStatus.COMPLETED
    assert findings_repo.findings  # au moins un finding persiste
    assert findings_repo.relations  # RESOLVES_TO persistee (D-011)
    assert runs_repo.saved[-1] is result
    assert result.progress == 1.0


def test_degraded_module_yields_partial_status() -> None:
    profile = _profile(modules={"dns", "rdap"})
    track_run = _track_run(profile)
    orchestrator, findings_repo, _ = _orchestrator(rdap_collector=_FakeRdapCollector(fail=True))

    result = orchestrator.run(track_run=track_run, target_value=DomainName.parse("example.com"))

    assert result.status == TrackStatus.PARTIAL
    assert result.module_runs["rdap"].status == ModuleStatus.FAILED
    assert findings_repo.findings  # DNS a quand meme produit des resultats


def test_everything_failing_yields_failed_status() -> None:
    profile = _profile(modules={"dns"})
    track_run = _track_run(profile)
    orchestrator, findings_repo, _ = _orchestrator(dns_collector=_FailingDnsCollector())

    result = orchestrator.run(track_run=track_run, target_value=DomainName.parse("example.com"))

    assert result.status == TrackStatus.FAILED
    assert findings_repo.findings == []


def test_cancellation_before_start_yields_cancelled_status() -> None:
    profile = _profile(modules={"dns", "rdap", "neotrace"})
    track_run = _track_run(profile)
    orchestrator, _, _ = _orchestrator()
    token = CancellationToken()
    token.cancel()

    result = orchestrator.run(
        track_run=track_run, target_value=DomainName.parse("example.com"), cancellation_token=token
    )

    assert result.status == TrackStatus.CANCELLED
    assert result.module_runs["dns"].status == ModuleStatus.SKIPPED
    assert result.module_runs["rdap"].status == ModuleStatus.SKIPPED
    assert result.module_runs["neotrace"].status == ModuleStatus.SKIPPED


def test_global_timeout_exceeded_before_start_skips_everything_and_stays_partial() -> None:
    profile = _profile(
        modules={"dns", "rdap"}, limits=ExecutionLimits(global_timeout_seconds=0.0)
    )
    track_run = _track_run(profile)
    # l'horloge avance de 1s a chaque appel -> le tout premier controle de budget est deja depasse
    orchestrator, findings_repo, _ = _orchestrator(now=_clock(step=timedelta(seconds=1)))

    result = orchestrator.run(track_run=track_run, target_value=DomainName.parse("example.com"))

    assert result.status in (TrackStatus.PARTIAL, TrackStatus.FAILED)
    assert result.module_runs["dns"].status == ModuleStatus.SKIPPED
    assert result.module_runs["dns"].error_detail == "budget de temps global dépassé"
    assert findings_repo.findings == []


def test_only_enabled_mvp_modules_get_a_module_run() -> None:
    profile = _profile(modules={"dns"})
    track_run = _track_run(profile)
    orchestrator, _, _ = _orchestrator()

    result = orchestrator.run(track_run=track_run, target_value=DomainName.parse("example.com"))

    assert set(result.module_runs) == {"dns"}


def test_certificate_transparency_module_produces_findings_and_san_relation() -> None:
    profile = _profile(modules={"dns", "certificate_transparency"})
    track_run = _track_run(profile)
    orchestrator, findings_repo, _ = _orchestrator(ct_collector=_FakeCtCollector(distinct_log_count=2))

    result = orchestrator.run(track_run=track_run, target_value=DomainName.parse("example.com"))

    assert result.status == TrackStatus.COMPLETED
    assert result.module_runs["certificate_transparency"].status == ModuleStatus.COMPLETED
    assert any(f.finding_type == "certificate.observed" for f in findings_repo.findings)
    san_relations = [r for r in findings_repo.relations if r.relation_type.value == "certificate_san"]
    assert len(san_relations) == 1
    assert san_relations[0].confidence == ConfidenceLevel.CORROBORATED  # 2 logs distincts


def test_unsupported_extended_module_is_skipped_with_explicit_reason() -> None:
    profile = _profile(modules={"dns", "organization"})
    track_run = _track_run(profile)
    orchestrator, _, _ = _orchestrator()

    result = orchestrator.run(track_run=track_run, target_value=DomainName.parse("example.com"))

    assert result.module_runs["organization"].status == ModuleStatus.SKIPPED
    assert result.module_runs["organization"].error_detail == "module non encore implémenté"


def test_certificate_transparency_module_skipped_without_collector_configured() -> None:
    profile = _profile(modules={"dns", "certificate_transparency"})
    track_run = _track_run(profile)
    orchestrator, _, _ = _orchestrator()

    result = orchestrator.run(track_run=track_run, target_value=DomainName.parse("example.com"))

    assert result.module_runs["certificate_transparency"].status == ModuleStatus.SKIPPED
    assert result.status == TrackStatus.COMPLETED
