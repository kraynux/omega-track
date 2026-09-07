# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat de collecte DNS (plan de dev, Phase 3/6). Resolveur systeme par
defaut (D-014, angle mort 5), jamais un resolveur public code en dur -
regle appliquee par l'implementation infra, pas visible dans ce contrat."""
from __future__ import annotations

from typing import Protocol

from omega_track.domain.value_objects.collected_record import CollectedRecord
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.domain.value_objects.ip_address import IPAddress


class DnsCollector(Protocol):
    def resolve(self, domain: DomainName) -> list[CollectedRecord]:
        """A/AAAA/CNAME/MX/TXT/CAA/DNSSEC selon disponibilite - un
        CollectedRecord par enregistrement trouve."""
        ...

    def reverse_lookup(self, ip: IPAddress) -> CollectedRecord | None:
        """PTR de la cible elle-meme (si le profil l'autorise) - distinct
        de `ReverseDnsResolver` (services/) qui annote les hops NeoTrace
        sans produire de Finding persiste."""
        ...
