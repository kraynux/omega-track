# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat de resolution GeoIP/ASN locale (plan de dev, Phase 3/5). DB-IP
et MaxMind implementent tous deux ce meme port (plan §5, "les deux
sources implementent le meme GeoIpResolver")."""
from __future__ import annotations

from typing import Protocol

from omega_track.domain.value_objects.asn import Asn
from omega_track.domain.value_objects.geo_location import GeoLocation
from omega_track.domain.value_objects.ip_address import IPAddress


class GeoIpResolver(Protocol):
    def locate(self, ip: IPAddress) -> GeoLocation | None: ...

    def lookup_asn(self, ip: IPAddress) -> Asn | None: ...
