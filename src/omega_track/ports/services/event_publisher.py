# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat de publication d'evenements de progression (plan de dev,
Phase 3/7) - consomme par la TUI (Phase 11, ecran Progression) et le
relais de log CLI, sans coupler l'orchestrateur a Textual ni au module
logging directement."""
from __future__ import annotations

from typing import Protocol

from omega_track.domain.value_objects.identifiers import TrackRunId
from omega_track.domain.value_objects.statuses import ModuleStatus


class EventPublisher(Protocol):
    def publish_progress(self, track_run_id: TrackRunId, message: str, percentage: float) -> None: ...

    def publish_module_status(
        self, track_run_id: TrackRunId, module_name: str, status: ModuleStatus
    ) -> None: ...
