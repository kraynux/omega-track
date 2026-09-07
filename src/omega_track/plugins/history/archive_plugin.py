# Copyright (c) 2026 kraynux - Licence MIT
"""Plugin Archives web publiques (plan de dev §10, point 2) - meme
patron que ct_plugin.py."""
from __future__ import annotations

from omega_track.domain.value_objects.collected_record import CollectedRecord
from omega_track.domain.value_objects.collection_mode import CollectionMode
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.plugins.descriptor import PluginDescriptor
from omega_track.ports.collectors.archive_collector import ArchiveCollector

DESCRIPTOR = PluginDescriptor(
    name="archives",
    category="history",
    version="1.0",
    required_capabilities=frozenset({"requires_network"}),
    default_enabled=False,
    collection_mode=CollectionMode.PASSIVE_PUBLIC,
    dependencies=frozenset(),
    output_finding_types=frozenset({"history.archive_snapshot"}),
)


class ArchivePlugin:
    """Implemente ports/collectors/archive_collector.py::ArchiveCollector."""

    descriptor = DESCRIPTOR

    def __init__(self, collector: ArchiveCollector) -> None:
        self._collector = collector

    def collect_snapshots(self, domain: DomainName) -> list[CollectedRecord]:
        return self._collector.collect_snapshots(domain)
