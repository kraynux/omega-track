# Copyright (c) 2026 kraynux - Licence MIT
"""Use case DeleteTargets (plan de dev §9 `target delete`) - pluriel car
la CLI/TUI peuvent supprimer plusieurs cibles en un appel (ex. selection
multiple dans un tableau, Phase 11) - idempotent, une suppression d'un
id deja absent ne leve jamais (voir TargetRepository.delete, Phase 4)."""
from __future__ import annotations

from omega_track.domain.value_objects.identifiers import TargetId
from omega_track.ports.repositories.target_repository import TargetRepository


def delete_targets(*, target_repository: TargetRepository, target_ids: list[TargetId]) -> None:
    for target_id in target_ids:
        target_repository.delete(target_id)
