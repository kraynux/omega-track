# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat de collecte de reputation (plan de dev §12) - une seule
methode generique, partagee par les DEUX sources a cle reelles
(VirusTotal/HIBP, chacune avec sa propre instance de ce port, comme
`dns_collector`/`rdap_collector` sont deux instances distinctes d'un
concept proche) : chaque implementation retourne des CollectedRecord
avec son propre finding_type/payload adapte a sa donnee (verdict VT,
breach HIBP), meme discipline que DnsCollector (une methode generique
`resolve` couvrant A/AAAA/MX/... heterogenes)."""
from __future__ import annotations

from typing import Protocol

from omega_track.domain.value_objects.collected_record import CollectedRecord
from omega_track.domain.value_objects.domain_name import DomainName


class ReputationCollector(Protocol):
    def collect_domain_reputation(self, domain: DomainName) -> list[CollectedRecord]: ...
