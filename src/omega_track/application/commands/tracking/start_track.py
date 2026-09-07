# Copyright (c) 2026 kraynux - Licence MIT
"""Use case StartTrack (plan de dev §9 `track run`) - applique
TargetAuthorizationGuard en tout premier, avant toute I/O reseau (D-010).

Construit un TrackProfile ad hoc (pas de profil nomme persiste requis
pour le MVP - aucune commande `profile save/list` n'existe dans la liste
"Commandes minimales" du plan §9, cette gestion de profils nommes reste
hors perimetre). Le bookkeeping du Target (`record_track`) est fait ici,
pas dans TrackOrchestrator (Phase 7) : malgre le docstring de
`Target.record_track` anticipant "l'orchestrateur (Phase 7)", garder
TrackOrchestrator concentre sur le seul TrackRun (pas de dependance
TargetRepository ajoutee a une classe deja testee) et faire ce
bookkeeping au niveau du use case, qui a deja les deux entites en main,
est moins invasif - meme raisonnement que les autres references de
phase anticipees deja corrigees cette session (Phases 5/6)."""
from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from omega_track.application.exceptions import TargetNotFoundError
from omega_track.application.guards.authorization_guard import ensure_target_authorized
from omega_track.application.orchestrators.cancellation import CancellationToken
from omega_track.application.orchestrators.track_orchestrator import TrackOrchestrator
from omega_track.domain.entities.track_profile import TrackProfile
from omega_track.domain.entities.track_run import TrackRun
from omega_track.domain.value_objects.identifiers import TargetId, TrackProfileId, TrackRunId
from omega_track.domain.value_objects.statuses import TrackStatus
from omega_track.ports.repositories.target_repository import TargetRepository
from omega_track.ports.repositories.track_run_repository import TrackRunRepository
from omega_track.shared.typing import IdFactory

DEFAULT_MVP_MODULES: frozenset[str] = frozenset({"dns", "reverse_dns", "rdap", "neotrace"})


def start_track(
    *,
    target_repository: TargetRepository,
    track_run_repository: TrackRunRepository,
    track_orchestrator: TrackOrchestrator,
    target_id: TargetId,
    modules: set[str] | None = None,
    tags: set[str] | None = None,
    explicit_authorization: bool = False,
    cancellation_token: CancellationToken | None = None,
    id_factory: IdFactory,
    now: Callable[[], datetime],
) -> TrackRun:
    target = target_repository.get(target_id)
    if target is None:
        raise TargetNotFoundError(target_id)
    ensure_target_authorized(target, explicit_authorization=explicit_authorization)

    moment = now()
    profile = TrackProfile(
        id=TrackProfileId(id_factory()),
        name="ad-hoc",
        modules=set(modules) if modules else set(DEFAULT_MVP_MODULES),
        created_at=moment,
        updated_at=moment,
    )
    track_run = TrackRun(
        id=TrackRunId(id_factory()),
        target_id=target_id,
        profile_snapshot=profile,
        status=TrackStatus.QUEUED,
        created_at=moment,
        tags=set(tags) if tags else set(),
    )

    result = track_orchestrator.run(
        track_run=track_run, target_value=target.value, cancellation_token=cancellation_token
    )

    target.record_track(status=result.status.value, now=now())
    target_repository.save(target)
    return result
