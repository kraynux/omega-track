# Copyright (c) 2026 kraynux - Licence MIT
from datetime import datetime, timezone

import pytest

from omega_track.domain.entities.track_profile import TrackProfile
from omega_track.domain.entities.track_run import ModuleRun, TrackRun
from omega_track.domain.exceptions.track import InvalidTrackTransitionError
from omega_track.domain.value_objects.collection_mode import CollectionMode
from omega_track.domain.value_objects.identifiers import (
    ModuleRunId,
    TargetId,
    TrackProfileId,
    TrackRunId,
)
from omega_track.domain.value_objects.statuses import ModuleStatus, TrackStatus

_NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)
_LATER = datetime(2026, 1, 1, 0, 5, tzinfo=timezone.utc)


def _profile() -> TrackProfile:
    return TrackProfile(
        id=TrackProfileId("p1"), name="default", modules={"dns"}, created_at=_NOW, updated_at=_NOW,
    )


def _run(**overrides) -> TrackRun:
    defaults = {
        "id": TrackRunId("run-1"),
        "target_id": TargetId("target-1"),
        "profile_snapshot": _profile(),
        "status": TrackStatus.QUEUED,
        "created_at": _NOW,
    }
    defaults.update(overrides)
    return TrackRun(**defaults)


def test_queued_to_running_is_valid() -> None:
    run = _run()
    run.start(now=_LATER)
    assert run.status == TrackStatus.RUNNING
    assert run.started_at == _LATER


def test_queued_to_cancelled_is_valid() -> None:
    run = _run()
    run.cancel(now=_LATER)
    assert run.status == TrackStatus.CANCELLED
    assert run.completed_at == _LATER


def test_running_to_completed_is_valid() -> None:
    run = _run(status=TrackStatus.RUNNING)
    run.finish(status=TrackStatus.COMPLETED, now=_LATER)
    assert run.status == TrackStatus.COMPLETED


def test_running_to_partial_is_valid() -> None:
    run = _run(status=TrackStatus.RUNNING)
    run.finish(status=TrackStatus.PARTIAL, now=_LATER)
    assert run.status == TrackStatus.PARTIAL


def test_queued_to_completed_directly_is_invalid() -> None:
    run = _run()
    with pytest.raises(InvalidTrackTransitionError):
        run.finish(status=TrackStatus.COMPLETED, now=_LATER)


def test_completed_is_terminal() -> None:
    run = _run(status=TrackStatus.COMPLETED)
    with pytest.raises(InvalidTrackTransitionError):
        run.start(now=_LATER)


def test_cancelled_cannot_restart() -> None:
    run = _run(status=TrackStatus.CANCELLED)
    with pytest.raises(InvalidTrackTransitionError):
        run.start(now=_LATER)


def test_progress_out_of_range_rejected() -> None:
    run = _run()
    with pytest.raises(ValueError):
        run.update_progress(1.5)


def test_module_run_transition_valid() -> None:
    module_run = ModuleRun(
        id=ModuleRunId("mr-1"), module_name="dns", status=ModuleStatus.PENDING,
        collection_mode=CollectionMode.ACTIVE_LIGHT,
    )
    module_run.transition_to(ModuleStatus.RUNNING, now=_NOW)
    assert module_run.status == ModuleStatus.RUNNING
    assert module_run.started_at == _NOW


def test_module_run_invalid_transition_raises() -> None:
    module_run = ModuleRun(
        id=ModuleRunId("mr-1"), module_name="dns", status=ModuleStatus.COMPLETED,
        collection_mode=CollectionMode.ACTIVE_LIGHT,
    )
    with pytest.raises(InvalidTrackTransitionError):
        module_run.transition_to(ModuleStatus.RUNNING, now=_NOW)


def test_set_module_status_via_track_run() -> None:
    run = _run()
    run.module_runs["dns"] = ModuleRun(
        id=ModuleRunId("mr-1"), module_name="dns", status=ModuleStatus.PENDING,
        collection_mode=CollectionMode.ACTIVE_LIGHT,
    )
    run.set_module_status("dns", ModuleStatus.RUNNING, now=_NOW)
    assert run.module_runs["dns"].status == ModuleStatus.RUNNING
