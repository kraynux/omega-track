# Copyright (c) 2026 kraynux - Licence MIT
"""Use case UpdateTarget (plan de dev §9 `target edit`) - alias et tags
uniquement, jamais la valeur de cible elle-meme (changer d'IP/domaine
sur une cible existante n'a pas de sens metier, ce serait une nouvelle
cible - voir CreateTarget)."""
from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from omega_track.application.exceptions import TargetNotFoundError
from omega_track.domain.entities.target import Target
from omega_track.domain.services.target_validator import validate_alias, validate_tag
from omega_track.domain.value_objects.identifiers import TargetId
from omega_track.ports.repositories.target_repository import TargetRepository


def update_target(
    *,
    target_repository: TargetRepository,
    target_id: TargetId,
    alias: str | None = None,
    add_tags: set[str] | None = None,
    remove_tags: set[str] | None = None,
    now: Callable[[], datetime],
) -> Target:
    target = target_repository.get(target_id)
    if target is None:
        raise TargetNotFoundError(target_id)

    if alias is not None:
        target.rename(validate_alias(alias), now=now())
    for tag in add_tags or set():
        target.add_tag(validate_tag(tag), now=now())
    for tag in remove_tags or set():
        target.remove_tag(tag, now=now())

    target_repository.save(target)
    return target
