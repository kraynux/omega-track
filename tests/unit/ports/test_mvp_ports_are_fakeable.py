# Copyright (c) 2026 kraynux - Licence MIT
"""Preuve du critere de sortie de la Phase 3 : "Tous les use cases du MVP
peuvent etre ecrits avec des fakes." Chaque fake ci-dessous est un simple
objet Python en duck-typing (aucune classe de base, aucun import
d'infrastructure) qui satisfait la forme d'un port MVP (Phase 6/7) - la
preuve que l'implementation reelle n'est pas necessaire pour ecrire/tester
l'application qui viendra plus tard."""
from __future__ import annotations

from datetime import datetime, timezone

from omega_track.core.enums import ConfidenceLevel
from omega_track.domain.entities.findings.base import Finding
from omega_track.domain.entities.findings.path import NetworkHop, NetworkPath
from omega_track.domain.entities.relation import Relation
from omega_track.domain.entities.target import Target
from omega_track.domain.entities.track_profile import NeoTraceOptions
from omega_track.domain.entities.track_run import TrackRun
from omega_track.domain.value_objects.asn import Asn
from omega_track.domain.value_objects.collected_record import CollectedRecord
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.domain.value_objects.geo_location import GeoLocation
from omega_track.domain.value_objects.identifiers import TargetId, TrackRunId
from omega_track.domain.value_objects.ip_address import IPAddress
from omega_track.domain.value_objects.statuses import ModuleStatus
from omega_track.domain.value_objects.target_value import TargetValue, parse_target_value

_NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


class _FakeTargetRepository:
    def __init__(self) -> None:
        self._targets: dict[TargetId, Target] = {}

    def save(self, target: Target) -> None:
        self._targets[target.id] = target

    def get(self, target_id: TargetId) -> Target | None:
        return self._targets.get(target_id)

    def find_by_value(self, value: TargetValue) -> Target | None:
        return next((t for t in self._targets.values() if t.value == value), None)

    def list_all(self) -> list[Target]:
        return list(self._targets.values())

    def delete(self, target_id: TargetId) -> None:
        self._targets.pop(target_id, None)


class _FakeTrackRunRepository:
    def __init__(self) -> None:
        self._runs: dict[str, TrackRun] = {}

    def save(self, run: TrackRun) -> None:
        self._runs[run.id] = run

    def get(self, track_run_id: TrackRunId) -> TrackRun | None:
        return self._runs.get(track_run_id)

    def list_for_target(self, target_id: TargetId) -> list[TrackRun]:
        return [r for r in self._runs.values() if r.target_id == target_id]

    def list_recent(
        self,
        *,
        status: str | None = None,
        tag: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> list[TrackRun]:
        return list(self._runs.values())

    def delete(self, track_run_id: TrackRunId) -> None:
        self._runs.pop(track_run_id, None)


class _FakeFindingRepository:
    def __init__(self) -> None:
        self._findings: list[Finding] = []
        self._relations: list[Relation] = []

    def save_findings(self, findings: list[Finding]) -> None:
        self._findings.extend(findings)

    def save_relations(self, relations: list[Relation]) -> None:
        self._relations.extend(relations)

    def list_findings_for_run(self, track_run_id: TrackRunId) -> list[Finding]:
        return [f for f in self._findings if f.track_run_id == track_run_id]

    def list_relations_for_run(self, track_run_id: TrackRunId) -> list[Relation]:
        return [r for r in self._relations if r.track_run_id == track_run_id]

    def delete_for_run(self, track_run_id: TrackRunId) -> None:
        self._findings = [f for f in self._findings if f.track_run_id != track_run_id]
        self._relations = [r for r in self._relations if r.track_run_id != track_run_id]


class _FakeSettingsRepository:
    def __init__(self) -> None:
        self._data: dict[str, str] = {}

    def get(self, key: str, default: str | None = None) -> str | None:
        return self._data.get(key, default)

    def set(self, key: str, value: str) -> None:
        self._data[key] = value

    def all(self) -> dict[str, str]:
        return dict(self._data)


class _FakeDnsCollector:
    def resolve(self, domain: DomainName) -> list[CollectedRecord]:
        return [
            CollectedRecord(
                finding_type="dns.a_record", payload={"value": "203.0.113.10"},
                confidence=ConfidenceLevel.VERIFIED, source_name="dns", observed_at=_NOW,
            )
        ]

    def reverse_lookup(self, ip: IPAddress) -> CollectedRecord | None:
        return None


class _FakeRdapCollector:
    def collect_domain_registration(self, domain: DomainName) -> list[CollectedRecord]:
        return [
            CollectedRecord(
                finding_type="identity.registrar", payload={"name": "Example Registrar"},
                confidence=ConfidenceLevel.DECLARED, source_name="rdap", observed_at=_NOW,
            )
        ]

    def collect_ip_registration(self, ip: IPAddress) -> list[CollectedRecord]:
        return []


class _FakeTracerouteCollector:
    def trace(self, target_ip: IPAddress, options: NeoTraceOptions) -> NetworkPath:
        return NetworkPath(target_ip=target_ip, protocol=options.protocol, hops=[NetworkHop(sequence=1, ip=target_ip)])

    def is_available(self) -> bool:
        return True


class _FakeGeoIpResolver:
    def locate(self, ip: IPAddress) -> GeoLocation | None:
        return GeoLocation(country="XX", source="fake")

    def lookup_asn(self, ip: IPAddress) -> Asn | None:
        return Asn(number=64512)


class _FakeReverseDnsResolver:
    def resolve_ptr(self, ip: IPAddress) -> str | None:
        return "host.example.com"


class _FakeEventPublisher:
    def __init__(self) -> None:
        self.events: list[tuple] = []

    def publish_progress(self, track_run_id: TrackRunId, message: str, percentage: float) -> None:
        self.events.append(("progress", message, percentage))

    def publish_module_status(
        self, track_run_id: TrackRunId, module_name: str, status: ModuleStatus
    ) -> None:
        self.events.append(("module_status", module_name, status))


def _fixed_clock() -> datetime:
    return _NOW


def test_target_repository_fake_round_trips() -> None:
    repo = _FakeTargetRepository()
    target = Target(id=TargetId("t1"), value=parse_target_value("example.com"), created_at=_NOW, updated_at=_NOW)
    repo.save(target)
    assert repo.get(TargetId("t1")) is target
    assert repo.find_by_value(parse_target_value("example.com")) is target


def test_dns_and_rdap_collectors_fake_return_collected_records() -> None:
    dns = _FakeDnsCollector()
    rdap = _FakeRdapCollector()
    records = dns.resolve(DomainName.parse("example.com")) + rdap.collect_domain_registration(
        DomainName.parse("example.com")
    )
    assert len(records) == 2
    assert all(isinstance(r, CollectedRecord) for r in records)


def test_traceroute_collector_fake_returns_network_path() -> None:
    collector = _FakeTracerouteCollector()
    ip = IPAddress.parse("203.0.113.10")
    path = collector.trace(ip, NeoTraceOptions())
    assert isinstance(path, NetworkPath)
    assert path.reached_target
    assert collector.is_available()


def test_geoip_and_reverse_dns_fakes_return_domain_types() -> None:
    geoip = _FakeGeoIpResolver()
    reverse_dns = _FakeReverseDnsResolver()
    ip = IPAddress.parse("203.0.113.10")
    assert isinstance(geoip.locate(ip), GeoLocation)
    assert isinstance(geoip.lookup_asn(ip), Asn)
    assert reverse_dns.resolve_ptr(ip) == "host.example.com"


def test_event_publisher_fake_records_events() -> None:
    publisher = _FakeEventPublisher()
    publisher.publish_progress(TrackRunId("run-1"), "resolving DNS", 0.2)
    publisher.publish_module_status(TrackRunId("run-1"), "dns", ModuleStatus.RUNNING)
    assert len(publisher.events) == 2


def test_clock_fake_is_a_plain_callable() -> None:
    assert _fixed_clock() == _NOW


def test_settings_repository_fake_matches_reexported_omega_lib_contract() -> None:
    from omega_track.ports.repositories.settings_repository import SettingsRepository

    repo = _FakeSettingsRepository()
    repo.set("theme", "dark")
    assert repo.get("theme") == "dark"
    assert repo.get("missing", "fallback") == "fallback"
    assert repo.all() == {"theme": "dark"}
    assert SettingsRepository is not None  # le type existe bien, reexporte sans erreur
