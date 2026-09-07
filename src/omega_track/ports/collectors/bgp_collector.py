# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat de collecte BGP/annonces reseau (plan de dev, Phase 3/10,
RIPEstat). Un ASN commun reste un CollectedRecord brut - ne devient
jamais une Relation automatique (D-011, applique par
domain/services/correlation_engine.py, pas ici)."""
from __future__ import annotations

from typing import Protocol

from omega_track.domain.value_objects.collected_record import CollectedRecord
from omega_track.domain.value_objects.ip_address import IPAddress


class BgpCollector(Protocol):
    def collect_announcements(self, ip: IPAddress) -> list[CollectedRecord]: ...
