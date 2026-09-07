# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from datetime import datetime, timezone

from omega_track.core.enums import ConfidenceLevel
from omega_track.domain.services.finding_builder import build_finding
from omega_track.domain.value_objects.collected_record import CollectedRecord
from omega_track.domain.value_objects.collection_mode import CollectionMode
from omega_track.domain.value_objects.identifiers import ModuleRunId, TrackRunId

_OBSERVED_AT = datetime(2026, 9, 6, 10, 0, tzinfo=timezone.utc)
_COLLECTED_AT = datetime(2026, 9, 6, 10, 5, tzinfo=timezone.utc)


def _record(**overrides: object) -> CollectedRecord:
    defaults: dict[str, object] = {
        "finding_type": "dns.a_record",
        "payload": {"address": "1.2.3.4"},
        "confidence": ConfidenceLevel.VERIFIED,
        "source_name": "dns",
        "observed_at": _OBSERVED_AT,
        "evidence_reference": None,
    }
    defaults.update(overrides)
    return CollectedRecord(**defaults)  # type: ignore[arg-type]


def test_build_finding_copies_record_fields() -> None:
    finding = build_finding(
        _record(),
        track_run_id=TrackRunId("run-1"),
        module_run_id=ModuleRunId("module-1"),
        collection_mode=CollectionMode.ACTIVE_LIGHT,
        id_factory=lambda: "finding-1",
        now=lambda: _COLLECTED_AT,
    )
    assert finding.id == "finding-1"
    assert finding.track_run_id == "run-1"
    assert finding.module_run_id == "module-1"
    assert finding.finding_type == "dns.a_record"
    assert finding.payload == {"address": "1.2.3.4"}
    assert finding.confidence == ConfidenceLevel.VERIFIED
    assert finding.collection_mode == CollectionMode.ACTIVE_LIGHT
    assert finding.source_name == "dns"
    assert finding.observed_at == _OBSERVED_AT
    assert finding.collected_at == _COLLECTED_AT


def test_build_finding_adds_one_evidence_from_the_record() -> None:
    finding = build_finding(
        _record(evidence_reference="https://example.org/ref"),
        track_run_id=TrackRunId("run-1"),
        module_run_id=ModuleRunId("module-1"),
        collection_mode=CollectionMode.PASSIVE_PUBLIC,
        id_factory=lambda: "finding-2",
        now=lambda: _COLLECTED_AT,
    )
    assert len(finding.evidences) == 1
    evidence = finding.evidences[0]
    assert evidence.source == "dns"
    assert evidence.reference == "https://example.org/ref"
    assert evidence.collected_at == _COLLECTED_AT
