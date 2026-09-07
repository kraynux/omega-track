# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat de persistance des TrackRun (plan de dev, Phase 3/4/7). Ne
porte que TrackRun + ModuleRun (l'aggregat "execution") - findings et
relations, potentiellement nombreux, ont leur propre port
(finding_repository.py) plutot que d'alourdir cet aggregat root."""
from __future__ import annotations

from datetime import datetime
from typing import Protocol

from omega_track.domain.entities.track_run import TrackRun
from omega_track.domain.value_objects.identifiers import TargetId, TrackRunId


class TrackRunRepository(Protocol):
    def save(self, run: TrackRun) -> None: ...

    def get(self, track_run_id: TrackRunId) -> TrackRun | None: ...

    def list_for_target(self, target_id: TargetId) -> list[TrackRun]: ...

    def list_recent(
        self,
        *,
        status: str | None = None,
        tag: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> list[TrackRun]:
        """Filtre combinable (CLI `history list [--target] [--status]
        [--tag] [--since] [--until]`, Phase 9)."""
        ...

    def delete(self, track_run_id: TrackRunId) -> None: ...
