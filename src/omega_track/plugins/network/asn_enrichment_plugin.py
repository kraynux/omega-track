# Copyright (c) 2026 kraynux - Licence MIT
"""Plugin ASN/BGP publics (plan de dev §10, point 3) - meme patron que
ct_plugin.py. Ne construit jamais de Relation lui-meme (D-011) : produit
uniquement des Finding bruts `network.asn` via le collecteur enveloppe,
la promotion en Relation (si corroboree) reste l'exclusivite de
domain/services/correlation_engine.py."""
from __future__ import annotations

from omega_track.domain.value_objects.collected_record import CollectedRecord
from omega_track.domain.value_objects.collection_mode import CollectionMode
from omega_track.domain.value_objects.ip_address import IPAddress
from omega_track.plugins.descriptor import PluginDescriptor
from omega_track.ports.collectors.bgp_collector import BgpCollector

DESCRIPTOR = PluginDescriptor(
    name="bgp",
    category="network",
    version="1.0",
    required_capabilities=frozenset({"requires_network"}),
    default_enabled=False,
    collection_mode=CollectionMode.PASSIVE_PUBLIC,
    dependencies=frozenset(),
    output_finding_types=frozenset({"network.asn"}),
)


class AsnEnrichmentPlugin:
    """Implemente ports/collectors/bgp_collector.py::BgpCollector."""

    descriptor = DESCRIPTOR

    def __init__(self, collector: BgpCollector) -> None:
        self._collector = collector

    def collect_announcements(self, ip: IPAddress) -> list[CollectedRecord]:
        return self._collector.collect_announcements(ip)
