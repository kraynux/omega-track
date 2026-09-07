# Copyright (c) 2026 kraynux - Licence MIT
"""Plugin HIBP (plan de dev §12) - enveloppe un ReputationCollector reel
(infrastructure/collectors/reputation/hibp_collector.py, injecte par
app/bootstrap.py). **Source payante** (docs/DATA_SOURCES.md, depuis le
changement de politique HIBP de 2022) - `default_enabled=False` comme
VirusTotal, mais jamais presente comme "juste une cle gratuite" dans
l'ecran de configuration (application/queries/get_source_disclosure.py)."""
from __future__ import annotations

from omega_track.domain.value_objects.collected_record import CollectedRecord
from omega_track.domain.value_objects.collection_mode import CollectionMode
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.plugins.descriptor import PluginDescriptor
from omega_track.ports.collectors.reputation_collector import ReputationCollector

DESCRIPTOR = PluginDescriptor(
    name="hibp",
    category="reputation",
    version="1.0",
    required_capabilities=frozenset({"requires_network", "requires_api_key"}),
    default_enabled=False,
    collection_mode=CollectionMode.API_KEY,
    dependencies=frozenset(),
    output_finding_types=frozenset({"reputation.verdict"}),
)


class HibpPlugin:
    """Implemente ports/collectors/reputation_collector.py::ReputationCollector."""

    descriptor = DESCRIPTOR

    def __init__(self, collector: ReputationCollector) -> None:
        self._collector = collector

    def collect_domain_reputation(self, domain: DomainName) -> list[CollectedRecord]:
        return self._collector.collect_domain_reputation(domain)
