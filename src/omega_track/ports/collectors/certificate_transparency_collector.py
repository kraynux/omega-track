# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat de collecte Certificate Transparency (plan de dev, Phase 3/10).
Traitee avec le meme quota/cache/backoff qu'une source a cle malgre
l'absence de cle (docs/DATA_SOURCES.md : crt.sh sans SLA publie)."""
from __future__ import annotations

from typing import Protocol

from omega_track.domain.value_objects.collected_record import CollectedRecord
from omega_track.domain.value_objects.domain_name import DomainName


class CertificateTransparencyCollector(Protocol):
    def collect_certificates(self, domain: DomainName) -> list[CollectedRecord]:
        """Retourne aussi les sous-domaines observes passivement
        (dns.passive_subdomain) - jamais via brute-force (hors perimetre,
        §1.2)."""
        ...

    def distinct_log_count(self, domain: DomainName) -> int:
        """Nombre de logs CT distincts ayant observe des certificats pour
        ce domaine - necessaire a D-011 (2+ logs -> CORROBORATED)."""
        ...
