# Copyright (c) 2026 kraynux - Licence MIT
"""Use case ListTargets (plan de dev §9 `target list`)."""
from __future__ import annotations

from omega_track.domain.entities.target import Target
from omega_track.ports.repositories.target_repository import TargetRepository


def list_targets(*, target_repository: TargetRepository) -> list[Target]:
    return target_repository.list_all()
