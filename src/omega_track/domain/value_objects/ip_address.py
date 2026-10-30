# Copyright (c) 2026 kraynux - Licence MIT
"""IP normalisee - jamais une simple chaine libre (plan de dev §4.2).
Seule la stdlib `ipaddress` est utilisee (charte : domaine sans
dependance technique)."""
from __future__ import annotations

import ipaddress
from dataclasses import dataclass

from omega_track.domain.exceptions.target import InvalidTargetValueError
from omega_track.shared.i18n import _

_AddressT = ipaddress.IPv4Address | ipaddress.IPv6Address


@dataclass(frozen=True, slots=True)
class IPAddress:
    """Enveloppe immuable autour d'une adresse IPv4/IPv6 deja validee -
    utiliser `IPAddress.parse()`, jamais le constructeur directement avec
    une chaine non verifiee."""

    value: _AddressT

    @classmethod
    def parse(cls, raw: str) -> IPAddress:
        try:
            return cls(ipaddress.ip_address(raw.strip()))
        except ValueError as exc:
            raise InvalidTargetValueError(_("adresse IP invalide : {raw!r}").format(raw=raw)) from exc

    @property
    def version(self) -> int:
        return self.value.version

    @property
    def is_private(self) -> bool:
        return self.value.is_private

    @property
    def is_loopback(self) -> bool:
        return self.value.is_loopback

    @property
    def is_link_local(self) -> bool:
        return self.value.is_link_local

    @property
    def is_reserved(self) -> bool:
        return self.value.is_reserved

    @property
    def is_multicast(self) -> bool:
        return self.value.is_multicast

    @property
    def is_public(self) -> bool:
        """Ni prive, ni loopback, ni link-local, ni reserve, ni multicast -
        seules les IPs publiques declenchent un lookup GeoIP/RDAP externe
        (Phase 6 : "les IPs privees... identifiees localement sans lookup
        externe")."""
        return not (
            self.is_private
            or self.is_loopback
            or self.is_link_local
            or self.is_reserved
            or self.is_multicast
        )

    def __str__(self) -> str:
        return str(self.value)
