# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from omega_track.application.exceptions import TrackRunNotFoundError
from omega_track.application.orchestrators.report_builder import build_identity_report
from omega_track.core.enums import ConfidenceLevel
from omega_track.domain.entities.findings.base import Finding
from omega_track.domain.entities.relation import Relation, RelationType
from omega_track.domain.entities.target import Target
from omega_track.domain.entities.track_profile import TrackProfile
from omega_track.domain.entities.track_run import TrackRun
from omega_track.domain.value_objects.collection_mode import CollectionMode
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.domain.value_objects.identifiers import (
    FindingId,
    ModuleRunId,
    RelationId,
    TargetId,
    TrackProfileId,
    TrackRunId,
)
from omega_track.domain.value_objects.statuses import TrackStatus

_NOW = datetime(2026, 9, 6, tzinfo=timezone.utc)
_RUN_ID = TrackRunId("run-1")
_TARGET_ID = TargetId("target-1")


class _FakeTrackRunRepository:
    def __init__(self, run: TrackRun | None) -> None:
        self._run = run

    def save(self, run: TrackRun) -> None:
        self._run = run

    def get(self, track_run_id: TrackRunId) -> TrackRun | None:
        return self._run

    def list_for_target(self, target_id: TargetId) -> list[TrackRun]:
        return []

    def list_recent(self, **kwargs: object) -> list[TrackRun]:
        return []

    def delete(self, track_run_id: TrackRunId) -> None:
        pass


class _FakeTargetRepository:
    def __init__(self, target: Target | None) -> None:
        self._target = target

    def save(self, target: Target) -> None:
        self._target = target

    def get(self, target_id: TargetId) -> Target | None:
        return self._target

    def find_by_value(self, value: object) -> Target | None:
        return self._target

    def list_all(self) -> list[Target]:
        return []

    def delete(self, target_id: TargetId) -> None:
        pass


class _FakeFindingRepository:
    def __init__(self, findings: list[Finding], relations: list[Relation]) -> None:
        self._findings = findings
        self._relations = relations

    def save_findings(self, findings: list[Finding]) -> None:
        pass

    def save_relations(self, relations: list[Relation]) -> None:
        pass

    def list_findings_for_run(self, track_run_id: TrackRunId) -> list[Finding]:
        return self._findings

    def list_relations_for_run(self, track_run_id: TrackRunId) -> list[Relation]:
        return self._relations

    def delete_for_run(self, track_run_id: TrackRunId) -> None:
        pass


def _profile() -> TrackProfile:
    return TrackProfile(
        id=TrackProfileId("profile-1"), name="default", modules={"dns"}, created_at=_NOW, updated_at=_NOW
    )


def _track_run() -> TrackRun:
    return TrackRun(
        id=_RUN_ID, target_id=_TARGET_ID, profile_snapshot=_profile(), status=TrackStatus.COMPLETED, created_at=_NOW
    )


def _target() -> Target:
    return Target(id=_TARGET_ID, value=DomainName.parse("example.com"), created_at=_NOW, updated_at=_NOW)


def _finding(finding_type: str, payload: dict) -> Finding:
    return Finding(
        id=FindingId(f"f-{finding_type}"), track_run_id=_RUN_ID, module_run_id=ModuleRunId("mr-1"),
        finding_type=finding_type, payload=payload, confidence=ConfidenceLevel.VERIFIED,
        collection_mode=CollectionMode.ACTIVE_LIGHT, source_name="dns", observed_at=_NOW, collected_at=_NOW,
    )


def _hop_finding(target_ip: str, sequence: int, ip: str | None, **extra: object) -> Finding:
    payload = {
        "target_ip": target_ip, "protocol": "icmp", "sequence": sequence, "ip": ip,
        "hostname": None, "rtt_ms": 1.0, "asn": None, "geo": None,
    }
    payload.update(extra)
    return _finding("path.hop", payload)


def test_builds_report_with_target_and_profile() -> None:
    repo_run = _FakeTrackRunRepository(_track_run())
    repo_target = _FakeTargetRepository(_target())
    repo_finding = _FakeFindingRepository([], [])

    report = build_identity_report(
        track_run_id=_RUN_ID, track_run_repository=repo_run, target_repository=repo_target,
        finding_repository=repo_finding, now=lambda: _NOW,
    )

    assert report.track_run_id == _RUN_ID
    assert report.target_id == _TARGET_ID
    assert report.target_value == DomainName.parse("example.com")
    assert report.profile_snapshot.name == "default"
    assert report.generated_at == _NOW


def test_raises_when_track_run_missing() -> None:
    repo_run = _FakeTrackRunRepository(None)
    repo_target = _FakeTargetRepository(_target())
    repo_finding = _FakeFindingRepository([], [])

    with pytest.raises(TrackRunNotFoundError):
        build_identity_report(
            track_run_id=_RUN_ID, track_run_repository=repo_run, target_repository=repo_target,
            finding_repository=repo_finding, now=lambda: _NOW,
        )


def test_raises_when_target_missing() -> None:
    repo_run = _FakeTrackRunRepository(_track_run())
    repo_target = _FakeTargetRepository(None)
    repo_finding = _FakeFindingRepository([], [])

    with pytest.raises(TrackRunNotFoundError):
        build_identity_report(
            track_run_id=_RUN_ID, track_run_repository=repo_run, target_repository=repo_target,
            finding_repository=repo_finding, now=lambda: _NOW,
        )


def test_clusters_are_recomputed_from_relations() -> None:
    relations = [
        Relation(
            id=RelationId("rel-1"), track_run_id=_RUN_ID, source_entity_ref="example.com",
            target_entity_ref="1.1.1.1", relation_type=RelationType.RESOLVES_TO,
            confidence=ConfidenceLevel.VERIFIED,
        )
    ]
    repo_run = _FakeTrackRunRepository(_track_run())
    repo_target = _FakeTargetRepository(_target())
    repo_finding = _FakeFindingRepository([], relations)

    report = build_identity_report(
        track_run_id=_RUN_ID, track_run_repository=repo_run, target_repository=repo_target,
        finding_repository=repo_finding, now=lambda: _NOW,
    )

    assert len(report.clusters) == 1
    assert report.clusters[0].member_refs == {"example.com", "1.1.1.1"}


def test_rebuilds_network_paths_from_hop_findings_including_non_responding() -> None:
    findings = [
        _hop_finding("1.1.1.1", 1, "192.168.1.1", hostname="gateway"),
        _hop_finding("1.1.1.1", 2, None),
        _hop_finding("1.1.1.1", 3, "1.1.1.1"),
    ]
    repo_run = _FakeTrackRunRepository(_track_run())
    repo_target = _FakeTargetRepository(_target())
    repo_finding = _FakeFindingRepository(findings, [])

    report = build_identity_report(
        track_run_id=_RUN_ID, track_run_repository=repo_run, target_repository=repo_target,
        finding_repository=repo_finding, now=lambda: _NOW,
    )

    assert len(report.paths) == 1
    path = report.paths[0]
    assert str(path.target_ip) == "1.1.1.1"
    assert path.protocol == "icmp"
    assert len(path.hops) == 3
    assert path.hops[1].ip is None
    assert path.non_responding_count == 1
    assert path.reached_target


def test_rebuilds_asn_and_geo_on_hops() -> None:
    findings = [
        _hop_finding(
            "1.1.1.1", 1, "1.1.1.1",
            asn={"number": 13335, "organization": "Cloudflare"},
            geo={
                "country": "AU", "region": None, "city": None, "latitude": None,
                "longitude": None, "timezone": None, "precision": "country", "source": "dbip",
            },
        ),
    ]
    repo_run = _FakeTrackRunRepository(_track_run())
    repo_target = _FakeTargetRepository(_target())
    repo_finding = _FakeFindingRepository(findings, [])

    report = build_identity_report(
        track_run_id=_RUN_ID, track_run_repository=repo_run, target_repository=repo_target,
        finding_repository=repo_finding, now=lambda: _NOW,
    )

    hop = report.paths[0].hops[0]
    assert hop.asn is not None and hop.asn.number == 13335
    assert hop.geo is not None and hop.geo.country == "AU"


def test_multiple_neotrace_targets_produce_separate_paths() -> None:
    findings = [
        _hop_finding("1.1.1.1", 1, "1.1.1.1"),
        _hop_finding("2.2.2.2", 1, "2.2.2.2"),
    ]
    repo_run = _FakeTrackRunRepository(_track_run())
    repo_target = _FakeTargetRepository(_target())
    repo_finding = _FakeFindingRepository(findings, [])

    report = build_identity_report(
        track_run_id=_RUN_ID, track_run_repository=repo_run, target_repository=repo_target,
        finding_repository=repo_finding, now=lambda: _NOW,
    )

    assert {str(p.target_ip) for p in report.paths} == {"1.1.1.1", "2.2.2.2"}
