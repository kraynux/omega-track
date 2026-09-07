# Copyright (c) 2026 kraynux - Licence MIT
"""Use case CreateTarget (plan de dev §9 `target add`) - n'implique
aucune autorisation, ajouter une cible n'est pas l'observer (le garde
D-010 ne s'applique qu'a `track run`/`track replay`)."""
from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from omega_track.domain.entities.target import Target
from omega_track.domain.exceptions.target import DuplicateTargetError
from omega_track.domain.services.target_validator import validate_alias, validate_tag
from omega_track.domain.value_objects.identifiers import TargetId
from omega_track.domain.value_objects.target_value import parse_target_value
from omega_track.ports.repositories.target_repository import TargetRepository
from omega_track.shared.typing import IdFactory


def create_target(
    *,
    target_repository: TargetRepository,
    raw_value: str,
    alias: str | None = None,
    tags: set[str] | None = None,
    id_factory: IdFactory,
    now: Callable[[], datetime],
) -> Target:
    value = parse_target_value(raw_value)
    if target_repository.find_by_value(value) is not None:
        raise DuplicateTargetError(f"cible deja existante : {value}")

    moment = now()
    target = Target(
        id=TargetId(id_factory()),
        value=value,
        created_at=moment,
        updated_at=moment,
        alias=validate_alias(alias),
        tags={validate_tag(tag) for tag in (tags or set())},
    )
    target_repository.save(target)
    return target
