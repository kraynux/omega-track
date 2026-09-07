# Copyright (c) 2026 kraynux - Licence MIT
from datetime import datetime, timezone

from omega_track.core.enums import ConfidenceLevel
from omega_track.domain.entities.findings.base import Finding
from omega_track.domain.value_objects.collection_mode import CollectionMode
from omega_track.domain.value_objects.evidence import Evidence
from omega_track.domain.value_objects.identifiers import FindingId, ModuleRunId, TrackRunId

_NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def _finding() -> Finding:
    return Finding(
        id=FindingId("f1"),
        track_run_id=TrackRunId("run-1"),
        module_run_id=ModuleRunId("mr-1"),
        finding_type="dns.a_record",
        payload={"value": "203.0.113.10"},
        confidence=ConfidenceLevel.VERIFIED,
        collection_mode=CollectionMode.ACTIVE_LIGHT,
        source_name="dns",
        observed_at=_NOW,
        collected_at=_NOW,
    )


def test_add_evidence_appends() -> None:
    finding = _finding()
    finding.add_evidence(Evidence(source="crt.sh", collected_at=_NOW, reference="log-a"))
    finding.add_evidence(Evidence(source="crt.sh", collected_at=_NOW, reference="log-b"))
    assert len(finding.evidences) == 2


def test_add_evidence_deduplicates_same_source_and_reference() -> None:
    finding = _finding()
    finding.add_evidence(Evidence(source="crt.sh", collected_at=_NOW, reference="log-a"))
    finding.add_evidence(Evidence(source="crt.sh", collected_at=_NOW, reference="log-a"))
    assert len(finding.evidences) == 1


def test_distinct_sources_counts_unique_sources() -> None:
    finding = _finding()
    finding.add_evidence(Evidence(source="crt.sh", collected_at=_NOW, reference="log-a"))
    finding.add_evidence(Evidence(source="wayback", collected_at=_NOW, reference="snap-1"))
    assert finding.distinct_sources == {"crt.sh", "wayback"}
