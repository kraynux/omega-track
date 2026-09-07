# Copyright (c) 2026 kraynux - Licence MIT
"""Use case ReplayTrack (plan de dev §9 `track replay`, D-013) - lance un
NOUVEAU TrackRun reutilisant le `profile_snapshot` du run d'origine
contre la resolution ACTUELLE de la cible (jamais un simple reaffichage,
voir `track show` pour ca) : la resolution "actuelle" est simplement ce
que le TrackOrchestrator produit a chaque execution (DNS/RDAP/NeoTrace
sont toujours re-interroges en direct, jamais mis en cache d'un run a
l'autre) - aucun traitement special requis ici pour satisfaire D-013.

Meme garde d'autorisation que `start_track.py` (D-010, "meme garde que
track run", plan §9)."""
from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from omega_track.application.exceptions import TargetNotFoundError, TrackRunNotFoundError
from omega_track.application.guards.authorization_guard import ensure_target_authorized
from omega_track.application.orchestrators.cancellation import CancellationToken
from omega_track.application.orchestrators.track_orchestrator import TrackOrchestrator
from omega_track.domain.entities.track_run import TrackRun
from omega_track.domain.value_objects.identifiers import TrackRunId
from omega_track.domain.value_objects.statuses import TrackStatus
from omega_track.ports.repositories.target_repository import TargetRepository
from omega_track.ports.repositories.track_run_repository import TrackRunRepository
from omega_track.shared.typing import IdFactory


def replay_track(
    *,
    target_repository: TargetRepository,
    track_run_repository: TrackRunRepository,
    track_orchestrator: TrackOrchestrator,
    original_track_run_id: TrackRunId,
    explicit_authorization: bool = False,
    cancellation_token: CancellationToken | None = None,
    id_factory: IdFactory,
    now: Callable[[], datetime],
) -> TrackRun:
    original = track_run_repository.get(original_track_run_id)
    if original is None:
        raise TrackRunNotFoundError(original_track_run_id)
    target = target_repository.get(original.target_id)
    if target is None:
        raise TargetNotFoundError(original.target_id)
    ensure_target_authorized(target, explicit_authorization=explicit_authorization)

    new_run = TrackRun(
        id=TrackRunId(id_factory()),
        target_id=target.id,
        profile_snapshot=original.profile_snapshot,
        status=TrackStatus.QUEUED,
        created_at=now(),
        tags=set(original.tags),
    )

    result = track_orchestrator.run(
        track_run=new_run, target_value=target.value, cancellation_token=cancellation_token
    )

    target.record_track(status=result.status.value, now=now())
    target_repository.save(target)
    return result
