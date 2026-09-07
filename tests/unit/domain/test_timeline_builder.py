# Copyright (c) 2026 kraynux - Licence MIT
from datetime import datetime, timezone

from omega_track.core.enums import ConfidenceLevel
from omega_track.domain.entities.findings.base import Finding
from omega_track.domain.services.timeline_builder import build_field_changes
from omega_track.domain.value_objects.collection_mode import CollectionMode
from omega_track.domain.value_objects.identifiers import FindingId, ModuleRunId, TrackRunId

_NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def _finding(finding_type: str, payload: dict) -> Finding:
    return Finding(
        id=FindingId("f1"), track_run_id=TrackRunId("run-1"), module_run_id=ModuleRunId("mr-1"),
        finding_type=finding_type, payload=payload, confidence=ConfidenceLevel.VERIFIED,
        collection_mode=CollectionMode.ACTIVE_LIGHT, source_name="dns",
        observed_at=_NOW, collected_at=_NOW,
    )


def test_no_changes_between_identical_runs() -> None:
    findings = [_finding("dns.a_record", {"value": "1.1.1.1"})]
    assert build_field_changes(findings, findings) == []


def test_changed_value_detected() -> None:
    previous = [_finding("dns.a_record", {"value": "1.1.1.1"})]
    current = [_finding("dns.a_record", {"value": "2.2.2.2"})]
    changes = build_field_changes(previous, current)
    assert len(changes) == 1
    assert changes[0].finding_type == "dns.a_record"


def test_addition_detected() -> None:
    current = [_finding("dns.aaaa_record", {"value": "::1"})]
    changes = build_field_changes([], current)
    assert len(changes) == 1
    assert changes[0].is_addition


def test_removal_detected() -> None:
    previous = [_finding("dns.aaaa_record", {"value": "::1"})]
    changes = build_field_changes(previous, [])
    assert len(changes) == 1
    assert changes[0].is_removal
