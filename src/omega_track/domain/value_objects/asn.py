# Copyright (c) 2026 kraynux - Licence MIT
"""Numero ASN valide (plan de dev §4.2). Plage 32 bits complete (RFC 7300),
pas seulement l'ancienne plage 16 bits."""
from __future__ import annotations

from dataclasses import dataclass, field

from omega_track.domain.exceptions.target import InvalidTargetValueError

_MAX_ASN = 4_294_967_295


@dataclass(frozen=True, slots=True)
class Asn:
    number: int
    organization: str | None = None
    prefixes: tuple[str, ...] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        if not (0 <= self.number <= _MAX_ASN):
            raise InvalidTargetValueError(f"ASN hors plage 32 bits : {self.number}")

    def __str__(self) -> str:
        return f"AS{self.number}"
