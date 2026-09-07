# Copyright (c) 2026 kraynux - Licence MIT
"""Use case GetTarget (plan de dev §9)."""
from __future__ import annotations

from omega_track.application.exceptions import TargetNotFoundError
from omega_track.domain.entities.target import Target
from omega_track.domain.value_objects.identifiers import TargetId
from omega_track.ports.repositories.target_repository import TargetRepository


def get_target(*, target_repository: TargetRepository, target_id: TargetId) -> Target:
    target = target_repository.get(target_id)
    if target is None:
        raise TargetNotFoundError(target_id)
    return target
