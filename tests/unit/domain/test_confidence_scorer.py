# Copyright (c) 2026 kraynux - Licence MIT
"""Score de confiance et non-regression sur les entrees incompletes
(plan de dev, Phase 2 "Tests")."""
from datetime import datetime, timezone

from omega_track.core.enums import ConfidenceLevel
from omega_track.domain.entities.findings.base import Finding
from omega_track.domain.services.confidence_scorer import score_findings
from omega_track.domain.value_objects.collection_mode import CollectionMode
from omega_track.domain.value_objects.identifiers import FindingId, ModuleRunId, TrackRunId

_NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def _finding(confidence: ConfidenceLevel) -> Finding:
    return Finding(
        id=FindingId("f1"), track_run_id=TrackRunId("run-1"), module_run_id=ModuleRunId("mr-1"),
        finding_type="dns.a_record", payload={}, confidence=confidence,
        collection_mode=CollectionMode.ACTIVE_LIGHT, source_name="dns",
        observed_at=_NOW, collected_at=_NOW,
    )


def test_empty_findings_score_zero_no_division_error() -> None:
    assert score_findings([]) == 0.0


def test_all_verified_scores_one() -> None:
    findings = [_finding(ConfidenceLevel.VERIFIED) for _ in range(3)]
    assert score_findings(findings) == 1.0


def test_all_unknown_scores_zero() -> None:
    findings = [_finding(ConfidenceLevel.UNKNOWN) for _ in range(3)]
    assert score_findings(findings) == 0.0


def test_mixed_confidence_between_zero_and_one() -> None:
    findings = [_finding(ConfidenceLevel.VERIFIED), _finding(ConfidenceLevel.UNKNOWN)]
    score = score_findings(findings)
    assert 0.0 < score < 1.0
