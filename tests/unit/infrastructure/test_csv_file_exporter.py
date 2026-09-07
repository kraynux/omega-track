# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

import io
import zipfile
from datetime import datetime, timezone

from omega_track.core.enums import ConfidenceLevel
from omega_track.domain.entities.findings.base import Finding
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
from omega_track.infrastructure.exporters.csv_file_exporter import CsvFileExporter

_NOW = datetime(2026, 9, 6, tzinfo=timezone.utc)


def _profile() -> TrackProfile:
    return TrackProfile(
        id=TrackProfileId("profile-1"), name="default", modules={"dns"}, created_at=_NOW, updated_at=_NOW
    )


def _finding(finding_type: str) -> Finding:
    return Finding(
        id=FindingId(f"f-{finding_type}"), track_run_id=TrackRunId("run-1"), module_run_id=ModuleRunId("mr-1"),
        finding_type=finding_type, payload={"x": 1}, confidence=ConfidenceLevel.VERIFIED,
        collection_mode=CollectionMode.ACTIVE_LIGHT, source_name="dns", observed_at=_NOW, collected_at=_NOW,
    )


def test_produces_a_zip_with_one_csv_per_finding_family() -> None:
    report = IdentityReport(
        track_run_id=TrackRunId("run-1"), target_id=TargetId("target-1"),
        target_value=DomainName.parse("example.com"), profile_snapshot=_profile(), generated_at=_NOW,
        findings=[_finding("dns.a_record"), _finding("identity.registrar")],
    )
    content = CsvFileExporter().export(report, ExportOptions())

    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        names = set(archive.namelist())
        assert names == {"findings_dns.csv", "findings_identity.csv"}
        dns_csv = archive.read("findings_dns.csv").decode("utf-8")
        assert "dns.a_record" in dns_csv


def test_includes_relations_csv_only_when_relations_exist() -> None:
    profile = _profile()
    report_without = IdentityReport(
        track_run_id=TrackRunId("run-1"), target_id=TargetId("target-1"),
        target_value=DomainName.parse("example.com"), profile_snapshot=profile, generated_at=_NOW,
    )
    with zipfile.ZipFile(io.BytesIO(CsvFileExporter().export(report_without, ExportOptions()))) as archive:
        assert "relations.csv" not in archive.namelist()

    relation = Relation(
        id=RelationId("rel-1"), track_run_id=TrackRunId("run-1"), source_entity_ref="example.com",
        target_entity_ref="1.1.1.1", relation_type=RelationType.RESOLVES_TO, confidence=ConfidenceLevel.VERIFIED,
    )
    report_with = IdentityReport(
        track_run_id=TrackRunId("run-1"), target_id=TargetId("target-1"),
        target_value=DomainName.parse("example.com"), profile_snapshot=profile, generated_at=_NOW,
        relations=[relation],
    )
    with zipfile.ZipFile(io.BytesIO(CsvFileExporter().export(report_with, ExportOptions()))) as archive:
        assert "relations.csv" in archive.namelist()
        assert "resolves_to" in archive.read("relations.csv").decode("utf-8")
