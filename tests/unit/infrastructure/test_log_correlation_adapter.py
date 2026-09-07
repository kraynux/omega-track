# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from omega_track.infrastructure.logging.config import _current_track_run_id
from omega_track.infrastructure.logging.log_correlation_adapter import ContextVarLogCorrelation


def test_set_then_reset_restores_previous_value() -> None:
    adapter = ContextVarLogCorrelation()
    before = _current_track_run_id.get()

    token = adapter.set_current_track_run_id("run-1")
    assert _current_track_run_id.get() == "run-1"

    adapter.reset_current_track_run_id(token)
    assert _current_track_run_id.get() == before
