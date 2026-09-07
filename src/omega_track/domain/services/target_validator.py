# Copyright (c) 2026 kraynux - Licence MIT
"""Validation pure des attributs d'une cible (plan de dev §4). La
normalisation de la valeur de cible elle-meme vit dans
value_objects/target_value.py::parse_target_value - ce module ne valide
que ce qui est propre a l'entite Target (alias, tags)."""
from __future__ import annotations

from omega_track.domain.exceptions.target import InvalidTargetValueError

_MAX_ALIAS_LENGTH = 128
_MAX_TAG_LENGTH = 64


def validate_alias(alias: str | None) -> str | None:
    if alias is None:
        return None
    stripped = alias.strip()
    if not stripped:
        return None
    if len(stripped) > _MAX_ALIAS_LENGTH:
        raise InvalidTargetValueError(f"alias trop long (max {_MAX_ALIAS_LENGTH}) : {alias!r}")
    return stripped


def validate_tag(tag: str) -> str:
    normalized = tag.strip().lower()
    if not normalized:
        raise InvalidTargetValueError("tag vide")
    if len(normalized) > _MAX_TAG_LENGTH:
        raise InvalidTargetValueError(f"tag trop long (max {_MAX_TAG_LENGTH}) : {tag!r}")
    return normalized
