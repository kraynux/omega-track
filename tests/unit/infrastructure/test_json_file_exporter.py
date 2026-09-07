# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

import json
from datetime import datetime, timezone

from omega_track.core.constants import APP_VERSION, EXPORT_SCHEMA_VERSION
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
from omega_track.infrastructure.exporters.json_file_exporter import JsonFileExporter

_NOW = datetime(2026, 9, 6, tzinfo=timezone.utc)


def _report() -> IdentityReport:
    profile = TrackProfile(
        id=TrackProfileId("profile-1"), name="default", modules={"dns", "rdap"}, created_at=_NOW, updated_at=_NOW
    )
    finding = Finding(
        id=FindingId("f1"), track_run_id=TrackRunId("run-1"), module_run_id=ModuleRunId("mr-1"),
        finding_type="dns.a_record", payload={"address": "1.1.1.1"}, confidence=ConfidenceLevel.VERIFIED,
        collection_mode=CollectionMode.ACTIVE_LIGHT, source_name="dns", observed_at=_NOW, collected_at=_NOW,
    )
    relation = Relation(
        id=RelationId("rel-1"), track_run_id=TrackRunId("run-1"), source_entity_ref="example.com",
        target_entity_ref="1.1.1.1", relation_type=RelationType.RESOLVES_TO, confidence=ConfidenceLevel.VERIFIED,
    )
    return IdentityReport(
        track_run_id=TrackRunId("run-1"), target_id=TargetId("target-1"),
        target_value=DomainName.parse("example.com"), profile_snapshot=profile, generated_at=_NOW,
        findings=[finding], relations=[relation],
    )


def test_export_produces_valid_json_with_expected_header() -> None:
    payload = json.loads(JsonFileExporter().export(_report(), ExportOptions()))

    assert payload["header"]["schema_version"] == EXPORT_SCHEMA_VERSION
    assert payload["header"]["app_version"] == APP_VERSION
    assert payload["header"]["target"] == "example.com"
    assert payload["header"]["profile"] == "default"
    assert payload["header"]["modules"] == ["dns", "rdap"]
    assert payload["header"]["sources"] == ["dns"]
    assert payload["header"]["redaction_policy"] == "none"


def test_export_includes_findings_and_relations() -> None:
    payload = json.loads(JsonFileExporter().export(_report(), ExportOptions()))

    assert len(payload["findings"]) == 1
    assert payload["findings"][0]["finding_type"] == "dns.a_record"
    assert payload["findings"][0]["payload"] == {"address": "1.1.1.1"}

    assert len(payload["relations"]) == 1
    assert payload["relations"][0]["relation_type"] == "resolves_to"


def test_export_is_canonical_and_deterministic() -> None:
    first = JsonFileExporter().export(_report(), ExportOptions())
    second = JsonFileExporter().export(_report(), ExportOptions())
    assert first == second
