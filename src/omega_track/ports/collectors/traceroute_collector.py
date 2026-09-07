# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat NeoTrace (plan de dev, Phase 3/6) - la seule action reseau
active du MVP (D-008, CollectionMode.ACTIVE_LIGHT). Retourne directement
`NetworkPath` (deja un type domain riche, contrairement aux autres
collecteurs qui retournent des CollectedRecord bruts) : le chemin reseau
merite sa propre entite depuis la Phase 2, pas une re-derivation ici."""
from __future__ import annotations

from typing import Protocol

from omega_track.domain.entities.findings.path import NetworkPath
from omega_track.domain.entities.track_profile import NeoTraceOptions
from omega_track.domain.value_objects.ip_address import IPAddress


class TracerouteCollector(Protocol):
    def trace(self, target_ip: IPAddress, options: NeoTraceOptions) -> NetworkPath: ...

    def is_available(self) -> bool:
        """Detection de capacites au bootstrap (binaire absent/capacite
        insuffisante) - etat degrade nomme "traceroute indisponible"
        (D-016, angle mort 7), jamais confondu avec un hop non repondant."""
        ...
