# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat de collecte de donnees d'organisation (plan de dev, Phase 3/13).
`observed`/`inferred` restent deux `finding_type` distincts sur les
CollectedRecord retournes (jamais confondus, Phase 13)."""
from __future__ import annotations

from typing import Protocol

from omega_track.domain.value_objects.collected_record import CollectedRecord
from omega_track.domain.value_objects.domain_name import DomainName


class OrganizationCollector(Protocol):
    def collect_organization_data(self, domain: DomainName) -> list[CollectedRecord]: ...
