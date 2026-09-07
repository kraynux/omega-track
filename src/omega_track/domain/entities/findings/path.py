# Copyright (c) 2026 kraynux - Licence MIT
"""Famille de findings 'path' (plan de dev §4.1/§4.3) : traceroute, hops,
RTT, perte, route et anomalies de chemin - seule famille avec de vraies
entites dediees (NetworkHop/NetworkPath) plutot que de simples constantes
de type, le plan de dev l'exige explicitement (§4.1)."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from omega_track.domain.value_objects.asn import Asn
from omega_track.domain.value_objects.geo_location import GeoLocation
from omega_track.domain.value_objects.ip_address import IPAddress


class PathFindingType(str, Enum):
    HOP = "path.hop"
    ANOMALY = "path.anomaly"
    """Route inhabituelle detectee (ex. saut RTT anormal) - Phase 6+,
    jamais construit avant que le chemin nominal soit stable."""


@dataclass(frozen=True, slots=True)
class NetworkHop:
    """Un saut de traceroute. `ip is None` represente un hop non
    repondant ('*' dans la sortie brute) - toujours conserve explicitement,
    jamais supprime silencieusement (plan de dev, Phase 6 NeoTrace MVP)."""

    sequence: int
    ip: IPAddress | None
    hostname: str | None = None
    rtt_ms: float | None = None
    geo: GeoLocation | None = None
    asn: Asn | None = None

    @property
    def is_responding(self) -> bool:
        return self.ip is not None


@dataclass
class NetworkPath:
    """Chemin complet vers une cible (une IP effectivement utilisee par
    le client, D-012 : NeoTrace limite par defaut a 3 IPs par TrackRun)."""

    target_ip: IPAddress
    protocol: str
    hops: list[NetworkHop] = field(default_factory=list)

    @property
    def reached_target(self) -> bool:
        return bool(self.hops) and self.hops[-1].ip == self.target_ip

    @property
    def non_responding_count(self) -> int:
        return sum(1 for hop in self.hops if not hop.is_responding)

    @property
    def average_rtt_ms(self) -> float | None:
        rtts = [hop.rtt_ms for hop in self.hops if hop.rtt_ms is not None]
        return sum(rtts) / len(rtts) if rtts else None
