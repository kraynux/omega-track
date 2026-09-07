# Copyright (c) 2026 kraynux - Licence MIT
"""Use case PinTarget (plan de dev §9 `target pin`) - epingler = autoriser
(D-010) : plus besoin de `--authorize` sur les futurs `track run`/
`track replay` contre cette cible (application/guards/
authorization_guard.py::ensure_target_authorized)."""
from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from omega_track.application.exceptions import TargetNotFoundError
from omega_track.domain.entities.target import Target
from omega_track.domain.value_objects.identifiers import TargetId
from omega_track.ports.repositories.target_repository import TargetRepository


def pin_target(
    *, target_repository: TargetRepository, target_id: TargetId, now: Callable[[], datetime]
) -> Target:
    target = target_repository.get(target_id)
    if target is None:
        raise TargetNotFoundError(target_id)
    target.pin(now=now())
    target_repository.save(target)
    return target
