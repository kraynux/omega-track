# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat de persistance des cibles (plan de dev, Phase 3/4)."""
from __future__ import annotations

from typing import Protocol

from omega_track.domain.entities.target import Target
from omega_track.domain.value_objects.identifiers import TargetId
from omega_track.domain.value_objects.target_value import TargetValue


class TargetRepository(Protocol):
    def save(self, target: Target) -> None: ...

    def get(self, target_id: TargetId) -> Target | None: ...

    def find_by_value(self, value: TargetValue) -> Target | None:
        """Necessaire pour rejeter les doublons a la creation (meme
        `(normalized_value, target_kind)`, schema Phase 4)."""
        ...

    def list_all(self) -> list[Target]: ...

    def delete(self, target_id: TargetId) -> None: ...
