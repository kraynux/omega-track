# Copyright (c) 2026 kraynux - Licence MIT
"""Resolution PTR legere pour l'annotation des hops NeoTrace (plan de
dev, Phase 3/6) - distinct de `DnsCollector.reverse_lookup` (collectors/)
qui produit un Finding persiste pour la cible elle-meme. Ici, le resultat
n'est jamais persiste independamment, seulement attache a un
`NetworkHop.hostname` transitoirement."""
from __future__ import annotations

from typing import Protocol

from omega_track.domain.value_objects.ip_address import IPAddress


class ReverseDnsResolver(Protocol):
    def resolve_ptr(self, ip: IPAddress) -> str | None: ...
