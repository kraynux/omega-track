# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from datetime import datetime, timezone

from omega_track.application.orchestrators.phases.correlation_phase import run_correlation_phase
from omega_track.core.enums import ConfidenceLevel
from omega_track.domain.entities.findings.base import Finding
from omega_track.domain.entities.relation import RelationType
from omega_track.domain.value_objects.collection_mode import CollectionMode
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.domain.value_objects.identifiers import FindingId, ModuleRunId, TrackRunId
from omega_track.domain.value_objects.ip_address import IPAddress

_RUN_ID = TrackRunId("run-1")
_NOW = datetime(2026, 9, 6, tzinfo=timezone.utc)


def _certificate_finding(serial: str) -> Finding:
    return Finding(
        id=FindingId(f"f-{serial}"), track_run_id=_RUN_ID, module_run_id=ModuleRunId("mr-ct"),
        finding_type="certificate.observed", payload={"serial_number": serial}, confidence=ConfidenceLevel.DECLARED,
        collection_mode=CollectionMode.PASSIVE_PUBLIC, source_name="crt.sh", observed_at=_NOW, collected_at=_NOW,
    )


def _id_factory() -> str:
    return "relation-1"


def test_builds_verified_resolves_to_relation_for_each_resolved_ip() -> None:
    relations = run_correlation_phase(
        track_run_id=_RUN_ID,
        target_value=DomainName.parse("example.com"),
        resolved_ips=[IPAddress.parse("1.1.1.1"), IPAddress.parse("2606:4700:4700::1111")],
        id_factory=_id_factory,
    )
    assert len(relations) == 2
    assert all(r.relation_type == RelationType.RESOLVES_TO for r in relations)
    assert all(r.confidence == ConfidenceLevel.VERIFIED for r in relations)
    assert {r.target_entity_ref for r in relations} == {"1.1.1.1", "2606:4700:4700::1111"}
    assert all(r.source_entity_ref == "example.com" for r in relations)


def test_returns_nothing_when_target_is_an_ip() -> None:
    relations = run_correlation_phase(
        track_run_id=_RUN_ID,
        target_value=IPAddress.parse("1.1.1.1"),
        resolved_ips=[IPAddress.parse("1.1.1.1")],
        id_factory=_id_factory,
    )
    assert relations == []


def test_returns_nothing_when_no_ips_resolved() -> None:
    relations = run_correlation_phase(
        track_run_id=_RUN_ID,
        target_value=DomainName.parse("example.com"),
        resolved_ips=[],
        id_factory=_id_factory,
    )
    assert relations == []


def test_builds_declared_certificate_san_relation_for_single_ct_log() -> None:
    relations = run_correlation_phase(
        track_run_id=_RUN_ID,
        target_value=DomainName.parse("example.com"),
        resolved_ips=[],
        certificate_findings=[_certificate_finding("abc123")],
        distinct_ct_log_count=1,
        id_factory=_id_factory,
    )
    assert len(relations) == 1
    assert relations[0].relation_type == RelationType.CERTIFICATE_SAN
    assert relations[0].confidence == ConfidenceLevel.DECLARED
    assert relations[0].source_entity_ref == "cert:abc123"
    assert relations[0].target_entity_ref == "example.com"


def test_certificate_san_relation_is_corroborated_when_two_distinct_logs() -> None:
    relations = run_correlation_phase(
        track_run_id=_RUN_ID,
        target_value=DomainName.parse("example.com"),
        resolved_ips=[],
        certificate_findings=[_certificate_finding("abc123")],
        distinct_ct_log_count=2,
        id_factory=_id_factory,
    )
    assert relations[0].confidence == ConfidenceLevel.CORROBORATED


def test_deduplicates_relations_by_distinct_certificate_serial() -> None:
    relations = run_correlation_phase(
        track_run_id=_RUN_ID,
        target_value=DomainName.parse("example.com"),
        resolved_ips=[],
        certificate_findings=[_certificate_finding("abc123"), _certificate_finding("abc123")],
        distinct_ct_log_count=1,
        id_factory=_id_factory,
    )
    assert len(relations) == 1


def test_no_certificate_relations_when_no_certificate_findings() -> None:
    relations = run_correlation_phase(
        track_run_id=_RUN_ID,
        target_value=DomainName.parse("example.com"),
        resolved_ips=[],
        id_factory=_id_factory,
    )
    assert relations == []
