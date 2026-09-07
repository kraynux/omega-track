# Copyright (c) 2026 kraynux - Licence MIT
"""Plugin Certificate Transparency (plan de dev §10, point 1) - enveloppe
un CertificateTransparencyCollector reel (infrastructure/, injecte par
app/bootstrap.py) avec des metadonnees decouvrables
(`plugins/registry.py`). Satisfait structurellement le meme port que le
collecteur qu'il enveloppe : consommable par application/orchestrators/
phases/extended_modules_phase.py exactement comme le collecteur brut,
sans jamais que la couche application n'importe `plugins.*` (Dependency
Rule - voir descriptor.py)."""
from __future__ import annotations

from omega_track.domain.value_objects.collected_record import CollectedRecord
from omega_track.domain.value_objects.collection_mode import CollectionMode
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.plugins.descriptor import PluginDescriptor
from omega_track.ports.collectors.certificate_transparency_collector import (
    CertificateTransparencyCollector,
)

DESCRIPTOR = PluginDescriptor(
    name="certificate_transparency",
    category="certificates",
    version="1.0",
    required_capabilities=frozenset({"requires_network"}),
    default_enabled=False,
    collection_mode=CollectionMode.PASSIVE_PUBLIC,
    dependencies=frozenset(),
    output_finding_types=frozenset(
        {"certificate.observed", "certificate.san", "dns.passive_subdomain"}
    ),
)


class CtPlugin:
    """Implemente ports/collectors/certificate_transparency_collector.py::
    CertificateTransparencyCollector."""

    descriptor = DESCRIPTOR

    def __init__(self, collector: CertificateTransparencyCollector) -> None:
        self._collector = collector

    def collect_certificates(self, domain: DomainName) -> list[CollectedRecord]:
        return self._collector.collect_certificates(domain)

    def distinct_log_count(self, domain: DomainName) -> int:
        return self._collector.distinct_log_count(domain)
