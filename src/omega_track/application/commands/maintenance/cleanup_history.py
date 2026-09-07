# Copyright (c) 2026 kraynux - Licence MIT
"""Purge de l'historique (plan de dev §9 `cleanup preview`/`cleanup run
--older-than <days>`) - jamais sans `--older-than` explicite ni
confirmation (impose par la CLI, pas ici) : `preview_history_cleanup`
est un apercu pur (aucune ecriture), `cleanup_history` effectue la
suppression reelle - toujours deux fonctions distinctes pour qu'un
appelant puisse afficher l'apercu avant de demander confirmation."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timedelta

from omega_track.application.commands.maintenance.cleanup_exports import delete_exports_for_runs
from omega_track.domain.value_objects.identifiers import TrackRunId
from omega_track.ports.repositories.export_repository import ExportRepository
from omega_track.ports.repositories.finding_repository import FindingRepository
from omega_track.ports.repositories.track_run_repository import TrackRunRepository


@dataclass(frozen=True, slots=True)
class HistoryCleanupPreview:
    track_run_ids: list[TrackRunId]

    @property
    def count(self) -> int:
        return len(self.track_run_ids)


def preview_history_cleanup(
    *, track_run_repository: TrackRunRepository, older_than: timedelta, now: Callable[[], datetime]
) -> HistoryCleanupPreview:
    cutoff = now() - older_than
    runs = track_run_repository.list_recent(until=cutoff)
    return HistoryCleanupPreview(track_run_ids=[run.id for run in runs])


def cleanup_history(
    *,
    track_run_repository: TrackRunRepository,
    finding_repository: FindingRepository,
    export_repository: ExportRepository,
    older_than: timedelta,
    now: Callable[[], datetime],
) -> HistoryCleanupPreview:
    preview = preview_history_cleanup(track_run_repository=track_run_repository, older_than=older_than, now=now)
    delete_exports_for_runs(export_repository=export_repository, track_run_ids=preview.track_run_ids)
    for track_run_id in preview.track_run_ids:
        finding_repository.delete_for_run(track_run_id)
        track_run_repository.delete(track_run_id)
    return preview
