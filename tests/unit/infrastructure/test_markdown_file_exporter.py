# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from datetime import datetime, timezone

from omega_track.core.enums import ConfidenceLevel
from omega_track.domain.entities.findings.base import Finding
from omega_track.domain.entities.findings.path import NetworkHop, NetworkPath
from omega_track.domain.entities.identity_report import IdentityReport
from omega_track.domain.entities.relation import Relation, RelationType
from omega_track.domain.entities.track_profile import TrackProfile
from omega_track.domain.value_objects.collection_mode import CollectionMode
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.domain.value_objects.export_options import ExportOptions
from omega_track.domain.value_objects.identifiers import (
    FindingId,
    ModuleRunId,
    RelationId,
    TargetId,
    TrackProfileId,
    TrackRunId,
)
from omega_track.domain.value_objects.ip_address import IPAddress
from omega_track.infrastructure.exporters.markdown_file_exporter import MarkdownFileExporter

_NOW = datetime(2026, 9, 6, tzinfo=timezone.utc)


def _profile() -> TrackProfile:
    return TrackProfile(
        id=TrackProfileId("profile-1"), name="default", modules={"dns"}, created_at=_NOW, updated_at=_NOW
    )


def _finding() -> Finding:
    return Finding(
        id=FindingId("f1"), track_run_id=TrackRunId("run-1"), module_run_id=ModuleRunId("mr-1"),
        finding_type="dns.a_record", payload={"address": "1.1.1.1"}, confidence=ConfidenceLevel.VERIFIED,
        collection_mode=CollectionMode.ACTIVE_LIGHT, source_name="dns", observed_at=_NOW, collected_at=_NOW,
    )


def test_markdown_includes_header_and_findings_table() -> None:
    report = IdentityReport(
        track_run_id=TrackRunId("run-1"), target_id=TargetId("target-1"),
        target_value=DomainName.parse("example.com"), profile_snapshot=_profile(), generated_at=_NOW,
        findings=[_finding()],
    )
    markdown = MarkdownFileExporter().export(report, ExportOptions()).decode("utf-8")

    assert "# Rapport OMEGA-TRACK - example.com" in markdown
    assert "## Dns" in markdown
    assert "dns.a_record" in markdown


def test_markdown_includes_relations_and_clusters_sections_only_when_present() -> None:
    report_without = IdentityReport(
        track_run_id=TrackRunId("run-1"), target_id=TargetId("target-1"),
        target_value=DomainName.parse("example.com"), profile_snapshot=_profile(), generated_at=_NOW,
    )
    markdown_without = MarkdownFileExporter().export(report_without, ExportOptions()).decode("utf-8")
    assert "## Relations" not in markdown_without
    assert "## Clusters" not in markdown_without

    relation = Relation(
        id=RelationId("rel-1"), track_run_id=TrackRunId("run-1"), source_entity_ref="example.com",
        target_entity_ref="1.1.1.1", relation_type=RelationType.RESOLVES_TO, confidence=ConfidenceLevel.VERIFIED,
    )
    report_with = IdentityReport(
        track_run_id=TrackRunId("run-1"), target_id=TargetId("target-1"),
        target_value=DomainName.parse("example.com"), profile_snapshot=_profile(), generated_at=_NOW,
        relations=[relation],
    )
    markdown_with = MarkdownFileExporter().export(report_with, ExportOptions()).decode("utf-8")
    assert "## Relations" in markdown_with
    assert "resolves_to" in markdown_with


def test_markdown_includes_network_path_table() -> None:
    ip = IPAddress.parse("1.1.1.1")
    path = NetworkPath(target_ip=ip, protocol="icmp", hops=[NetworkHop(sequence=1, ip=ip, rtt_ms=1.5)])
    report = IdentityReport(
        track_run_id=TrackRunId("run-1"), target_id=TargetId("target-1"),
        target_value=DomainName.parse("example.com"), profile_snapshot=_profile(), generated_at=_NOW,
        paths=[path],
    )
    markdown = MarkdownFileExporter().export(report, ExportOptions()).decode("utf-8")
    assert "## Chemin réseau (NeoTrace)" in markdown
    assert "1.1.1.1" in markdown
    assert "atteinte" in markdown
