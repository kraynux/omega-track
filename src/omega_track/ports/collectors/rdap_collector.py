# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat de collecte RDAP (plan de dev, Phase 3/6). Un champ RDAP
individuel manquant n'est jamais une erreur (D-015, angle mort 6) - c'est
a l'implementation infra de ne simplement pas produire le
CollectedRecord correspondant plutot que de lever."""
from __future__ import annotations

from typing import Protocol

from omega_track.domain.value_objects.collected_record import CollectedRecord
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.domain.value_objects.ip_address import IPAddress


class RdapCollector(Protocol):
    def collect_domain_registration(self, domain: DomainName) -> list[CollectedRecord]: ...

    def collect_ip_registration(self, ip: IPAddress) -> list[CollectedRecord]: ...
