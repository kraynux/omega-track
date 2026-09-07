# Copyright (c) 2026 kraynux - Licence MIT
"""Use case CancelTrack (plan de dev §9 `track cancel <run-id>`) -
best-effort au niveau base : TrackOrchestrator (Phase 7) est synchrone/
bloquant par choix assume (pas de threads), donc un `track run` en cours
occupe deja le seul processus qui pourrait verifier un
CancellationToken - une annulation "en direct" passe par SIGINT sur ce
meme processus (interfaces/cli/commands/track.py, code de sortie 130),
pas par cette commande separee. `track cancel <run-id>` reste utile pour
marquer proprement CANCELLED un run reste bloque a QUEUED/RUNNING suite
a un crash/kill du processus qui l'executait - jamais un echec si le run
est deja dans un etat terminal (idempotent, pas d'erreur)."""
from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from omega_track.application.exceptions import TrackRunNotFoundError
from omega_track.domain.entities.track_run import TrackRun
from omega_track.domain.value_objects.identifiers import TrackRunId
from omega_track.domain.value_objects.statuses import TrackStatus
from omega_track.ports.repositories.track_run_repository import TrackRunRepository


def cancel_track(
    *, track_run_repository: TrackRunRepository, track_run_id: TrackRunId, now: Callable[[], datetime]
) -> TrackRun:
    track_run = track_run_repository.get(track_run_id)
    if track_run is None:
        raise TrackRunNotFoundError(track_run_id)

    if track_run.status in (TrackStatus.QUEUED, TrackStatus.RUNNING):
        track_run.cancel(now=now())
        track_run_repository.save(track_run)
    return track_run
