# Copyright (c) 2026 kraynux - Licence MIT
"""Implementation de LogCorrelation au dessus du contextvar deja
construit en Phase 1 (`infrastructure/logging/config.py`)."""
from __future__ import annotations

import contextvars
from typing import cast

from omega_track.infrastructure.logging.config import (
    reset_current_track_run_id,
    set_current_track_run_id,
)


class ContextVarLogCorrelation:
    """Implemente ports/services/log_correlation.py::LogCorrelation."""

    def set_current_track_run_id(self, track_run_id: str) -> object:
        return set_current_track_run_id(track_run_id)

    def reset_current_track_run_id(self, token: object) -> None:
        reset_current_track_run_id(cast("contextvars.Token[str]", token))
