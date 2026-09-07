# Copyright (c) 2026 kraynux - Licence MIT
"""Use case GetTrackRun (plan de dev §9 `track status <run-id>`) - statut
et progression seuls, sans reconstruire le rapport complet (voir
get_identity_report.py pour `track show`, plus couteux)."""
from __future__ import annotations

from omega_track.application.exceptions import TrackRunNotFoundError
from omega_track.domain.entities.track_run import TrackRun
from omega_track.domain.value_objects.identifiers import TrackRunId
from omega_track.ports.repositories.track_run_repository import TrackRunRepository


def get_track_run(*, track_run_repository: TrackRunRepository, track_run_id: TrackRunId) -> TrackRun:
    track_run = track_run_repository.get(track_run_id)
    if track_run is None:
        raise TrackRunNotFoundError(track_run_id)
    return track_run
