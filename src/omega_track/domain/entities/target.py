# Copyright (c) 2026 kraynux - Licence MIT
"""Cible persistante (plan de dev §4.1) - IP ou domaine, alias, tags,
epinglage. `pinned=True` EST le mecanisme d'autorisation persistante
(D-010, angle mort 1) : une cible epinglee n'a plus besoin de
`--authorize` sur ses futurs TrackRun."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from omega_track.domain.value_objects.identifiers import TargetId
from omega_track.domain.value_objects.target_value import TargetKind, TargetValue, target_kind_of


@dataclass
class Target:
    id: TargetId
    value: TargetValue
    created_at: datetime
    updated_at: datetime
    alias: str | None = None
    tags: set[str] = field(default_factory=set)
    pinned: bool = False
    last_track_at: datetime | None = None
    last_status: str | None = None

    @property
    def kind(self) -> TargetKind:
        return target_kind_of(self.value)

    def rename(self, alias: str | None, *, now: datetime) -> None:
        self.alias = alias
        self.updated_at = now

    def add_tag(self, tag: str, *, now: datetime) -> None:
        self.tags.add(tag)
        self.updated_at = now

    def remove_tag(self, tag: str, *, now: datetime) -> None:
        self.tags.discard(tag)
        self.updated_at = now

    def pin(self, *, now: datetime) -> None:
        """Epingler = autoriser (D-010) - plus besoin de --authorize sur
        les futurs track run/replay contre cette cible."""
        self.pinned = True
        self.updated_at = now

    def unpin(self, *, now: datetime) -> None:
        self.pinned = False
        self.updated_at = now

    def record_track(self, *, status: str, now: datetime) -> None:
        """Appele par l'orchestrateur (Phase 7) a la fin d'un TrackRun -
        le domaine se contente d'enregistrer le fait, jamais de decider
        quand un track se termine."""
        self.last_track_at = now
        self.last_status = status
        self.updated_at = now

    def is_authorized(self) -> bool:
        """D-010 : une cible epinglee est deja autorisee. Le garde
        applicatif (application/guards/authorization_guard.py, Phase 3)
        consulte cette methode plutot que de relire `pinned` directement,
        pour que la regle d'autorisation reste au meme endroit si elle
        se complexifie un jour (ex. expiration d'autorisation)."""
        return self.pinned
