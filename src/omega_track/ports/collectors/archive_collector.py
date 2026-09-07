# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat de collecte d'archives web publiques (plan de dev, Phase 3/10,
Wayback Machine). Meme prudence de robustesse que CT (docs/DATA_SOURCES.md)."""
from __future__ import annotations

from typing import Protocol

from omega_track.domain.value_objects.collected_record import CollectedRecord
from omega_track.domain.value_objects.domain_name import DomainName


class ArchiveCollector(Protocol):
    def collect_snapshots(self, domain: DomainName) -> list[CollectedRecord]: ...
