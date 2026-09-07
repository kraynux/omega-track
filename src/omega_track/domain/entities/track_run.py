# Copyright (c) 2026 kraynux - Licence MIT
"""Execution d'un profil sur une cible (plan de dev §4.1) - machine a
etats explicite (Phase 7 "Etats attendus"), jamais une simple chaine de
statut mutee sans controle."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from omega_track.domain.entities.track_profile import TrackProfile
from omega_track.domain.exceptions.track import InvalidTrackTransitionError
from omega_track.domain.value_objects.collection_mode import CollectionMode
from omega_track.domain.value_objects.identifiers import ModuleRunId, TargetId, TrackRunId
from omega_track.domain.value_objects.statuses import (
    ModuleStatus,
    TrackStatus,
    is_terminal_track_status,
    is_valid_module_transition,
    is_valid_track_transition,
)


@dataclass
class ModuleRun:
    """Etat d'un module au sein d'un TrackRun (table `module_runs`,
    Phase 4)."""

    id: ModuleRunId
    module_name: str
    status: ModuleStatus
    collection_mode: CollectionMode
    started_at: datetime | None = None
    completed_at: datetime | None = None
    source_name: str | None = None
    error_code: str | None = None
    error_detail: str | None = None

    def transition_to(self, new_status: ModuleStatus, *, now: datetime) -> None:
        if not is_valid_module_transition(self.status, new_status):
            raise InvalidTrackTransitionError(self.status.value, new_status.value)
        self.status = new_status
        if new_status == ModuleStatus.RUNNING:
            self.started_at = now
        elif new_status not in (ModuleStatus.PENDING,):
            self.completed_at = now


@dataclass
class TrackRun:
    id: TrackRunId
    target_id: TargetId
    profile_snapshot: TrackProfile
    """Copie du profil au moment du lancement (pas une reference vivante) -
    condition de `track replay` (D-013) : rejouer un run doit reutiliser
    EXACTEMENT le profil d'origine, meme si le profil nomme a change
    depuis."""
    status: TrackStatus
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    progress: float = 0.0
    error_summary: str | None = None
    tags: set[str] = field(default_factory=set)
    module_runs: dict[str, ModuleRun] = field(default_factory=dict)

    def start(self, *, now: datetime) -> None:
        self._transition(TrackStatus.RUNNING, now=now)
        self.started_at = now

    def cancel(self, *, now: datetime) -> None:
        self._transition(TrackStatus.CANCELLED, now=now)
        self.completed_at = now

    def finish(self, *, status: TrackStatus, now: datetime, error_summary: str | None = None) -> None:
        """`status` doit etre un statut terminal (COMPLETED/PARTIAL/FAILED) -
        CANCELLED passe par `cancel()`, pas par ici."""
        if not is_terminal_track_status(status):
            raise InvalidTrackTransitionError(self.status.value, status.value)
        self._transition(status, now=now)
        self.completed_at = now
        self.error_summary = error_summary

    def update_progress(self, value: float) -> None:
        if not (0.0 <= value <= 1.0):
            raise ValueError(f"progression hors plage [0,1] : {value}")
        self.progress = value

    def set_module_status(self, module_name: str, status: ModuleStatus, *, now: datetime) -> None:
        self.module_runs[module_name].transition_to(status, now=now)

    def _transition(self, new_status: TrackStatus, *, now: datetime) -> None:
        if not is_valid_track_transition(self.status, new_status):
            raise InvalidTrackTransitionError(self.status.value, new_status.value)
        self.status = new_status
