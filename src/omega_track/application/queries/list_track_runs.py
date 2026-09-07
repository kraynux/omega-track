# Copyright (c) 2026 kraynux - Licence MIT
"""Use case ListTrackRuns (plan de dev §9 `history list [--target]
[--status] [--tag] [--since] [--until]`) - filtre combinable. Le port
TrackRunRepository (Phase 3/4) expose `list_for_target` et `list_recent`
separement (`list_for_target` ne prend pas les autres filtres) : quand
`--target` est fourni avec d'autres filtres, ce use case les recombine
lui-meme en memoire plutot que d'ignorer silencieusement les filtres
non supportes par `list_for_target`."""
from __future__ import annotations

from datetime import datetime

from omega_track.domain.entities.track_run import TrackRun
from omega_track.domain.value_objects.identifiers import TargetId
from omega_track.ports.repositories.track_run_repository import TrackRunRepository


def list_track_runs(
    *,
    track_run_repository: TrackRunRepository,
    target_id: TargetId | None = None,
    status: str | None = None,
    tag: str | None = None,
    since: datetime | None = None,
    until: datetime | None = None,
) -> list[TrackRun]:
    if target_id is not None:
        runs = track_run_repository.list_for_target(target_id)
        return [run for run in runs if _matches(run, status=status, tag=tag, since=since, until=until)]
    return track_run_repository.list_recent(status=status, tag=tag, since=since, until=until)


def _matches(
    run: TrackRun, *, status: str | None, tag: str | None, since: datetime | None, until: datetime | None
) -> bool:
    if status is not None and run.status.value != status:
        return False
    if tag is not None and tag not in run.tags:
        return False
    if since is not None and run.created_at < since:
        return False
    return not (until is not None and run.created_at > until)
