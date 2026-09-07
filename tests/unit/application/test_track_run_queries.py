# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from omega_track.application.exceptions import TrackRunNotFoundError
from omega_track.application.queries.get_track_run import get_track_run
from omega_track.application.queries.list_track_runs import list_track_runs
from omega_track.domain.entities.track_profile import TrackProfile
from omega_track.domain.entities.track_run import TrackRun
from omega_track.domain.value_objects.identifiers import TargetId, TrackProfileId, TrackRunId
from omega_track.domain.value_objects.statuses import TrackStatus

_NOW = datetime(2026, 9, 6, tzinfo=timezone.utc)


class _FakeTrackRunRepository:
    def __init__(self, runs: list[TrackRun]) -> None:
        self._runs = {r.id: r for r in runs}

    def save(self, run: TrackRun) -> None:
        self._runs[run.id] = run

    def get(self, track_run_id: TrackRunId) -> TrackRun | None:
        return self._runs.get(track_run_id)

    def list_for_target(self, target_id: TargetId) -> list[TrackRun]:
        return [r for r in self._runs.values() if r.target_id == target_id]

    def list_recent(
        self, *, status: str | None = None, tag: str | None = None,
        since: datetime | None = None, until: datetime | None = None,
    ) -> list[TrackRun]:
        return [
            r for r in self._runs.values()
            if (status is None or r.status.value == status)
            and (tag is None or tag in r.tags)
        ]

    def delete(self, track_run_id: TrackRunId) -> None:
        pass


def _profile() -> TrackProfile:
    return TrackProfile(id=TrackProfileId("p1"), name="p", modules=set(), created_at=_NOW, updated_at=_NOW)


def _run(run_id: str, target_id: str, *, status: TrackStatus = TrackStatus.QUEUED, tags: set[str] | None = None) -> TrackRun:
    return TrackRun(
        id=TrackRunId(run_id), target_id=TargetId(target_id), profile_snapshot=_profile(), status=status,
        created_at=_NOW, tags=tags or set(),
    )


def test_get_track_run_returns_existing() -> None:
    repo = _FakeTrackRunRepository([_run("r1", "t1")])
    assert get_track_run(track_run_repository=repo, track_run_id=TrackRunId("r1")).id == TrackRunId("r1")


def test_get_track_run_raises_when_missing() -> None:
    repo = _FakeTrackRunRepository([])
    with pytest.raises(TrackRunNotFoundError):
        get_track_run(track_run_repository=repo, track_run_id=TrackRunId("missing"))


def test_list_track_runs_filters_by_target_and_status_combined() -> None:
    repo = _FakeTrackRunRepository(
        [
            _run("r1", "t1", status=TrackStatus.COMPLETED),
            _run("r2", "t1", status=TrackStatus.FAILED),
            _run("r3", "t2", status=TrackStatus.COMPLETED),
        ]
    )
    result = list_track_runs(track_run_repository=repo, target_id=TargetId("t1"), status="completed")
    assert [r.id for r in result] == [TrackRunId("r1")]


def test_list_track_runs_without_target_delegates_to_list_recent() -> None:
    repo = _FakeTrackRunRepository([_run("r1", "t1", tags={"prod"})])
    result = list_track_runs(track_run_repository=repo, tag="prod")
    assert [r.id for r in result] == [TrackRunId("r1")]
