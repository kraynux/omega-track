# Copyright (c) 2026 kraynux - Licence MIT
"""Validation pure des attributs d'une cible (plan de dev §4). La
normalisation de la valeur de cible elle-meme vit dans
value_objects/target_value.py::parse_target_value - ce module ne valide
que ce qui est propre a l'entite Target (alias, tags)."""
from __future__ import annotations

from omega_track.domain.exceptions.target import InvalidTargetValueError
from omega_track.shared.i18n import _

_MAX_ALIAS_LENGTH = 128
_MAX_TAG_LENGTH = 64


def validate_alias(alias: str | None) -> str | None:
    if alias is None:
        return None
    stripped = alias.strip()
    if not stripped:
        return None
    if len(stripped) > _MAX_ALIAS_LENGTH:
        raise InvalidTargetValueError(_("alias trop long (max {MAX_ALIAS_LENGTH}) : {alias!r}").format(MAX_ALIAS_LENGTH=_MAX_ALIAS_LENGTH, alias=alias))
    return stripped


def validate_tag(tag: str) -> str:
    normalized = tag.strip().lower()
    if not normalized:
        raise InvalidTargetValueError(_("tag vide"))
    if len(normalized) > _MAX_TAG_LENGTH:
        raise InvalidTargetValueError(_("tag trop long (max {MAX_TAG_LENGTH}) : {tag!r}").format(MAX_TAG_LENGTH=_MAX_TAG_LENGTH, tag=tag))
    return normalized
