# Copyright (c) 2026 kraynux - Licence MIT
from omega_track.domain.value_objects.statuses import (
    ModuleStatus,
    TrackStatus,
    is_terminal_track_status,
    is_valid_module_transition,
    is_valid_track_transition,
)


def test_queued_can_run_or_cancel() -> None:
    assert is_valid_track_transition(TrackStatus.QUEUED, TrackStatus.RUNNING)
    assert is_valid_track_transition(TrackStatus.QUEUED, TrackStatus.CANCELLED)


def test_queued_cannot_complete_directly() -> None:
    assert not is_valid_track_transition(TrackStatus.QUEUED, TrackStatus.COMPLETED)


def test_terminal_statuses_have_no_outgoing_transition() -> None:
    for status in (TrackStatus.COMPLETED, TrackStatus.PARTIAL, TrackStatus.FAILED, TrackStatus.CANCELLED):
        assert is_terminal_track_status(status)
        assert not is_valid_track_transition(status, TrackStatus.RUNNING)


def test_module_pending_can_run_or_be_skipped() -> None:
    assert is_valid_module_transition(ModuleStatus.PENDING, ModuleStatus.RUNNING)
    assert is_valid_module_transition(ModuleStatus.PENDING, ModuleStatus.SKIPPED)


def test_module_completed_is_terminal() -> None:
    assert not is_valid_module_transition(ModuleStatus.COMPLETED, ModuleStatus.RUNNING)
