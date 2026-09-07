# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from datetime import datetime, timezone

from omega_track.core.enums import ConfidenceLevel
from omega_track.domain.value_objects.collected_record import CollectedRecord
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.domain.value_objects.ip_address import IPAddress
from omega_track.plugins.certificates.ct_plugin import CtPlugin
from omega_track.plugins.history.archive_plugin import ArchivePlugin
from omega_track.plugins.network.asn_enrichment_plugin import AsnEnrichmentPlugin
from omega_track.plugins.registry import PLUGIN_DESCRIPTORS, get_plugin_descriptor

_NOW = datetime(2026, 9, 6, tzinfo=timezone.utc)


def _record(finding_type: str) -> CollectedRecord:
    return CollectedRecord(
        finding_type=finding_type, payload={}, confidence=ConfidenceLevel.DECLARED,
        source_name="test", observed_at=_NOW,
    )


class _FakeCtCollector:
    def collect_certificates(self, domain: DomainName) -> list[CollectedRecord]:
        return [_record("certificate.observed")]

    def distinct_log_count(self, domain: DomainName) -> int:
        return 2


class _FakeArchiveCollector:
    def collect_snapshots(self, domain: DomainName) -> list[CollectedRecord]:
        return [_record("history.archive_snapshot")]


class _FakeBgpCollector:
    def collect_announcements(self, ip: IPAddress) -> list[CollectedRecord]:
        return [_record("network.asn")]


def test_ct_plugin_delegates_to_wrapped_collector() -> None:
    plugin = CtPlugin(_FakeCtCollector())
    records = plugin.collect_certificates(DomainName.parse("example.com"))
    assert len(records) == 1
    assert plugin.distinct_log_count(DomainName.parse("example.com")) == 2
    assert plugin.descriptor.name == "certificate_transparency"


def test_archive_plugin_delegates_to_wrapped_collector() -> None:
    plugin = ArchivePlugin(_FakeArchiveCollector())
    records = plugin.collect_snapshots(DomainName.parse("example.com"))
    assert len(records) == 1
    assert plugin.descriptor.name == "archives"


def test_asn_enrichment_plugin_delegates_to_wrapped_collector() -> None:
    plugin = AsnEnrichmentPlugin(_FakeBgpCollector())
    records = plugin.collect_announcements(IPAddress.parse("1.1.1.1"))
    assert len(records) == 1
    assert plugin.descriptor.name == "bgp"


def test_all_extended_module_descriptors_default_disabled() -> None:
    assert {"certificate_transparency", "archives", "bgp"} <= set(PLUGIN_DESCRIPTORS)
    for descriptor in PLUGIN_DESCRIPTORS.values():
        assert descriptor.default_enabled is False
        assert "requires_network" in descriptor.required_capabilities


def test_get_plugin_descriptor_returns_none_for_unknown_name() -> None:
    assert get_plugin_descriptor("does-not-exist") is None
