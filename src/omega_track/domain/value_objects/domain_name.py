# Copyright (c) 2026 kraynux - Licence MIT
"""Nom de domaine normalise : lowercase, IDNA/punycode, sans point final,
valide (plan de dev §4.2). Seul le codec stdlib `idna` est utilise (charte :
domaine sans dependance technique) - le codec stdlib implemente IDNA 2003
(limites connues sur certains caracteres IDNA2008), acceptable ici car
TRACK ne fait jamais la difference entre les deux pour la seule chose qui
compte : produire une forme ASCII stable et comparable pour la
correlation/deduplication (domain/services/correlation_engine.py)."""
from __future__ import annotations

import re
from dataclasses import dataclass

from omega_track.domain.exceptions.target import InvalidTargetValueError

_MAX_TOTAL_LENGTH = 253
_MAX_LABEL_LENGTH = 63
_LDH_LABEL_RE = re.compile(r"^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$")


@dataclass(frozen=True, slots=True)
class DomainName:
    """`ascii_form` (punycode, comparable/deduplicable) est la valeur
    normalisee de reference ; `display_form` (Unicode d'origine, lowercase)
    n'est conservee que pour l'affichage TUI/exports."""

    ascii_form: str
    display_form: str

    @classmethod
    def parse(cls, raw: str) -> DomainName:
        normalized = raw.strip().rstrip(".").lower()
        if not normalized:
            raise InvalidTargetValueError("nom de domaine vide")
        if len(normalized) > _MAX_TOTAL_LENGTH:
            raise InvalidTargetValueError(f"nom de domaine trop long : {raw!r}")

        labels = normalized.split(".")
        if any(not label for label in labels):
            raise InvalidTargetValueError(f"nom de domaine avec un label vide : {raw!r}")

        ascii_labels = []
        for label in labels:
            ascii_labels.append(cls._to_ascii_label(label, raw))

        return cls(ascii_form=".".join(ascii_labels), display_form=normalized)

    @staticmethod
    def _to_ascii_label(label: str, original_raw: str) -> str:
        try:
            ascii_label = label if label.isascii() else label.encode("idna").decode("ascii")
        except UnicodeError as exc:
            raise InvalidTargetValueError(f"label IDNA invalide dans {original_raw!r} : {label!r}") from exc

        if len(ascii_label) > _MAX_LABEL_LENGTH or not _LDH_LABEL_RE.match(ascii_label):
            raise InvalidTargetValueError(f"label invalide dans {original_raw!r} : {label!r}")
        return ascii_label

    def __str__(self) -> str:
        return self.ascii_form
