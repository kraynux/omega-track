# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone

import pytest

from omega_track.application.commands.tracking.cancel_track import cancel_track
from omega_track.application.commands.tracking.replay_track import replay_track
from omega_track.application.commands.tracking.start_track import start_track
from omega_track.application.exceptions import TargetNotFoundError, TrackRunNotFoundError
from omega_track.application.orchestrators.track_orchestrator import TrackOrchestrator
from omega_track.domain.entities.findings.base import Finding
from omega_track.domain.entities.findings.path import NetworkPath
from omega_track.domain.entities.relation import Relation
from omega_track.domain.entities.target import Target
from omega_track.domain.entities.track_profile import NeoTraceOptions, TrackProfile
from omega_track.domain.entities.track_run import TrackRun
from omega_track.domain.exceptions.track import TargetNotAuthorizedError
from omega_track.domain.value_objects.collected_record import CollectedRecord
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.domain.value_objects.identifiers import TargetId, TrackProfileId, TrackRunId
from omega_track.domain.value_objects.ip_address import IPAddress
from omega_track.domain.value_objects.statuses import TrackStatus
from omega_track.domain.value_objects.target_value import TargetValue

_NOW = datetime(2026, 9, 6, tzinfo=timezone.utc)


class _FakeEventPublisher:
    def publish_progress(self, track_run_id: object, message: str, percentage: float) -> None:
        pass

    def publish_module_status(self, track_run_id: object, module_name: str, status: object) -> None:
        pass


class _FakeTargetRepository:
    def __init__(self, targets: dict[TargetId, Target] | None = None) -> None:
        self._targets = targets or {}

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
        self._runs: dict[TrackRunId, TrackRun] = {}

    def save(self, run: TrackRun) -> None:
        self._runs[run.id] = run

    def get(self, track_run_id: TrackRunId) -> TrackRun | None:
        return self._runs.get(track_run_id)

    def list_for_target(self, target_id: TargetId) -> list[TrackRun]:
        return [r for r in self._runs.values() if r.target_id == target_id]

    def list_recent(self, **kwargs: object) -> list[TrackRun]:
        return list(self._runs.values())

    def delete(self, track_run_id: TrackRunId) -> None:
        self._runs.pop(track_run_id, None)


class _FakeDnsCollector:
    def resolve(self, domain: DomainName) -> list[CollectedRecord]:
        return []

    def reverse_lookup(self, ip: IPAddress) -> CollectedRecord | None:
        return None


class _FakeRdapCollector:
    def collect_domain_registration(self, domain: DomainName) -> list[CollectedRecord]:
        return []

    def collect_ip_registration(self, ip: IPAddress) -> list[CollectedRecord]:
        return []


class _FakeTracerouteCollector:
    def is_available(self) -> bool:
        return False

    def trace(self, target_ip: IPAddress, options: NeoTraceOptions) -> NetworkPath:
        raise AssertionError("ne doit pas etre appele (is_available=False)")


class _FakeFindingRepository:
    def save_findings(self, findings: list[Finding]) -> None:
        pass

    def save_relations(self, relations: list[Relation]) -> None:
        pass

    def list_findings_for_run(self, track_run_id: object) -> list[Finding]:
        return []

    def list_relations_for_run(self, track_run_id: object) -> list[Relation]:
        return []

    def delete_for_run(self, track_run_id: object) -> None:
        pass


def _id_factory() -> Callable[[], str]:
    counter = iter(f"id-{n}" for n in range(1, 1000))
    return counter.__next__


def _orchestrator(track_run_repository: _FakeTrackRunRepository) -> TrackOrchestrator:
    return TrackOrchestrator(
        dns_collector=_FakeDnsCollector(),
        rdap_collector=_FakeRdapCollector(),
        traceroute_collector=_FakeTracerouteCollector(),
        finding_repository=_FakeFindingRepository(),
        track_run_repository=track_run_repository,
        event_publisher=_FakeEventPublisher(),
        id_factory=_id_factory(),
        now=lambda: _NOW,
    )


def _pinned_target() -> Target:
    target = Target(id=TargetId("t1"), value=DomainName.parse("example.com"), created_at=_NOW, updated_at=_NOW)
    target.pin(now=_NOW)
    return target


def test_start_track_runs_and_records_on_target() -> None:
    target = _pinned_target()
    target_repo = _FakeTargetRepository({target.id: target})
    run_repo = _FakeTrackRunRepository()

    result = start_track(
        target_repository=target_repo, track_run_repository=run_repo, track_orchestrator=_orchestrator(run_repo),
        target_id=target.id, id_factory=_id_factory(), now=lambda: _NOW,
    )

    assert result.status == TrackStatus.COMPLETED
    assert target_repo.get(target.id).last_status == TrackStatus.COMPLETED.value  # type: ignore[union-attr]


def test_start_track_refuses_unauthorized_target() -> None:
    target = Target(id=TargetId("t1"), value=DomainName.parse("example.com"), created_at=_NOW, updated_at=_NOW)
    target_repo = _FakeTargetRepository({target.id: target})
    run_repo = _FakeTrackRunRepository()

    with pytest.raises(TargetNotAuthorizedError):
        start_track(
            target_repository=target_repo, track_run_repository=run_repo, track_orchestrator=_orchestrator(run_repo),
            target_id=target.id, id_factory=_id_factory(), now=lambda: _NOW,
        )


def test_start_track_allows_unauthorized_target_with_explicit_flag() -> None:
    target = Target(id=TargetId("t1"), value=DomainName.parse("example.com"), created_at=_NOW, updated_at=_NOW)
    target_repo = _FakeTargetRepository({target.id: target})
    run_repo = _FakeTrackRunRepository()

    result = start_track(
        target_repository=target_repo, track_run_repository=run_repo, track_orchestrator=_orchestrator(run_repo),
        target_id=target.id, explicit_authorization=True, id_factory=_id_factory(), now=lambda: _NOW,
    )
    assert result.status == TrackStatus.COMPLETED


def test_start_track_raises_when_target_missing() -> None:
    target_repo = _FakeTargetRepository()
    run_repo = _FakeTrackRunRepository()
    with pytest.raises(TargetNotFoundError):
        start_track(
            target_repository=target_repo, track_run_repository=run_repo, track_orchestrator=_orchestrator(run_repo),
            target_id=TargetId("missing"), id_factory=_id_factory(), now=lambda: _NOW,
        )


def test_replay_track_reuses_original_profile_snapshot() -> None:
    target = _pinned_target()
    target_repo = _FakeTargetRepository({target.id: target})
    run_repo = _FakeTrackRunRepository()

    original = start_track(
        target_repository=target_repo, track_run_repository=run_repo, track_orchestrator=_orchestrator(run_repo),
        target_id=target.id, modules={"dns"}, id_factory=_id_factory(), now=lambda: _NOW,
    )

    replayed = replay_track(
        target_repository=target_repo, track_run_repository=run_repo, track_orchestrator=_orchestrator(run_repo),
        original_track_run_id=original.id, id_factory=_id_factory(), now=lambda: _NOW,
    )

    assert replayed.id != original.id
    assert replayed.profile_snapshot.modules == {"dns"}


def test_replay_track_raises_when_original_missing() -> None:
    target_repo = _FakeTargetRepository()
    run_repo = _FakeTrackRunRepository()
    with pytest.raises(TrackRunNotFoundError):
        replay_track(
            target_repository=target_repo, track_run_repository=run_repo, track_orchestrator=_orchestrator(run_repo),
            original_track_run_id=TrackRunId("missing"), id_factory=_id_factory(), now=lambda: _NOW,
        )


def test_cancel_track_marks_running_run_cancelled() -> None:
    run_repo = _FakeTrackRunRepository()
    profile = TrackProfile(id=TrackProfileId("p1"), name="p", modules=set(), created_at=_NOW, updated_at=_NOW)
    run = TrackRun(id=TrackRunId("r1"), target_id=TargetId("t1"), profile_snapshot=profile, status=TrackStatus.QUEUED, created_at=_NOW)
    run.start(now=_NOW)
    run_repo.save(run)

    result = cancel_track(track_run_repository=run_repo, track_run_id=run.id, now=lambda: _NOW)
    assert result.status == TrackStatus.CANCELLED


def test_cancel_track_is_a_no_op_on_terminal_run() -> None:
    run_repo = _FakeTrackRunRepository()
    profile = TrackProfile(id=TrackProfileId("p1"), name="p", modules=set(), created_at=_NOW, updated_at=_NOW)
    run = TrackRun(id=TrackRunId("r1"), target_id=TargetId("t1"), profile_snapshot=profile, status=TrackStatus.QUEUED, created_at=_NOW)
    run.start(now=_NOW)
    run.finish(status=TrackStatus.COMPLETED, now=_NOW)
    run_repo.save(run)

    result = cancel_track(track_run_repository=run_repo, track_run_id=run.id, now=lambda: _NOW)
    assert result.status == TrackStatus.COMPLETED


def test_cancel_track_raises_when_missing() -> None:
    run_repo = _FakeTrackRunRepository()
    with pytest.raises(TrackRunNotFoundError):
        cancel_track(track_run_repository=run_repo, track_run_id=TrackRunId("missing"), now=lambda: _NOW)
