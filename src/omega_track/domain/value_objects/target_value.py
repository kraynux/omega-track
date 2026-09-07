# Copyright (c) 2026 kraynux - Licence MIT
"""Union metier IP | domaine (plan de dev §4.2, `TargetValue`)."""
from __future__ import annotations

from enum import Enum

from omega_track.domain.exceptions.target import InvalidTargetValueError
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.domain.value_objects.ip_address import IPAddress

TargetValue = DomainName | IPAddress


class TargetKind(str, Enum):
    IP = "ip"
    DOMAIN = "domain"


def parse_target_value(raw: str) -> TargetValue:
    """Essaie IP d'abord (plus stricte, aucune ambiguite possible), puis
    domaine. Une chaine qui echoue aux deux leve `InvalidTargetValueError`
    avec le message du domaine (le plus specifique des deux echecs)."""
    stripped = raw.strip()
    if not stripped:
        raise InvalidTargetValueError("cible vide")

    try:
        return IPAddress.parse(stripped)
    except InvalidTargetValueError:
        pass

    return DomainName.parse(stripped)


def target_kind_of(value: TargetValue) -> TargetKind:
    if isinstance(value, IPAddress):
        return TargetKind.IP
    return TargetKind.DOMAIN
