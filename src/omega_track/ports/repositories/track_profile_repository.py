# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat de persistance des profils de track - absent de la liste
"Ports a creer" du plan de dev (Phase 3) mais present dans
ARBORESCENCE.md, et necessaire (la table `track_profiles`, Phase 4, et
la commande `save_profile.py` l'exigent). Ajoute en coherence."""
from __future__ import annotations

from typing import Protocol

from omega_track.domain.entities.track_profile import TrackProfile
from omega_track.domain.value_objects.identifiers import TrackProfileId


class TrackProfileRepository(Protocol):
    def save(self, profile: TrackProfile) -> None: ...

    def get(self, profile_id: TrackProfileId) -> TrackProfile | None: ...

    def get_default(self) -> TrackProfile | None: ...

    def list_all(self) -> list[TrackProfile]: ...

    def delete(self, profile_id: TrackProfileId) -> None: ...
