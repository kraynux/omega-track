# Copyright (c) 2026 kraynux - Licence MIT
"""Plugin VirusTotal (plan de dev §12) - enveloppe un ReputationCollector
reel (infrastructure/collectors/reputation/virustotal_collector.py,
injecte par app/bootstrap.py) avec des metadonnees decouvrables
(`plugins/registry.py`), premier usage reel de la capacite
"requires_api_key" (prevue par descriptor.py depuis la Phase 10, jamais
exercee avant Phase 12 - aucune source a cle construite jusqu'ici)."""
from __future__ import annotations

from omega_track.domain.value_objects.collected_record import CollectedRecord
from omega_track.domain.value_objects.collection_mode import CollectionMode
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.plugins.descriptor import PluginDescriptor
from omega_track.ports.collectors.reputation_collector import ReputationCollector

DESCRIPTOR = PluginDescriptor(
    name="virustotal",
    category="reputation",
    version="1.0",
    required_capabilities=frozenset({"requires_network", "requires_api_key"}),
    default_enabled=False,
    collection_mode=CollectionMode.API_KEY,
    dependencies=frozenset(),
    output_finding_types=frozenset({"reputation.verdict"}),
)


class VirusTotalPlugin:
    """Implemente ports/collectors/reputation_collector.py::ReputationCollector."""

    descriptor = DESCRIPTOR

    def __init__(self, collector: ReputationCollector) -> None:
        self._collector = collector

    def collect_domain_reputation(self, domain: DomainName) -> list[CollectedRecord]:
        return self._collector.collect_domain_reputation(domain)
