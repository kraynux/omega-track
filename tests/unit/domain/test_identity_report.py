# Copyright (c) 2026 kraynux - Licence MIT
from datetime import datetime, timezone

from omega_track.core.enums import ConfidenceLevel
from omega_track.domain.entities.findings.base import Finding
from omega_track.domain.entities.identity_report import IdentityReport
from omega_track.domain.entities.track_profile import TrackProfile
from omega_track.domain.value_objects.collection_mode import CollectionMode
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.domain.value_objects.identifiers import (
    FindingId,
    ModuleRunId,
    TargetId,
    TrackProfileId,
    TrackRunId,
)

_NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)
_TARGET_VALUE = DomainName.parse("example.com")
_PROFILE = TrackProfile(
    id=TrackProfileId("profile-1"), name="default", modules=set(), created_at=_NOW, updated_at=_NOW
)


def _finding(finding_type: str, confidence: ConfidenceLevel = ConfidenceLevel.VERIFIED) -> Finding:
    return Finding(
        id=FindingId("f1"), track_run_id=TrackRunId("run-1"), module_run_id=ModuleRunId("mr-1"),
        finding_type=finding_type, payload={}, confidence=confidence,
        collection_mode=CollectionMode.ACTIVE_LIGHT, source_name="dns",
        observed_at=_NOW, collected_at=_NOW,
    )


def test_findings_by_type_prefix_filters_family() -> None:
    report = IdentityReport(
        track_run_id=TrackRunId("run-1"), target_id=TargetId("t1"), target_value=_TARGET_VALUE,
        profile_snapshot=_PROFILE, generated_at=_NOW,
        findings=[_finding("dns.a_record"), _finding("identity.registrar")],
    )
    dns_findings = report.findings_by_type_prefix("dns.")
    assert len(dns_findings) == 1
    assert dns_findings[0].finding_type == "dns.a_record"


def test_summarize_counts_by_confidence() -> None:
    report = IdentityReport(
        track_run_id=TrackRunId("run-1"), target_id=TargetId("t1"), target_value=_TARGET_VALUE,
        profile_snapshot=_PROFILE, generated_at=_NOW,
        findings=[
            _finding("dns.a_record", ConfidenceLevel.VERIFIED),
            _finding("dns.aaaa_record", ConfidenceLevel.VERIFIED),
            _finding("identity.registrar", ConfidenceLevel.DECLARED),
        ],
    )
    summary = report.summarize()
    assert summary["verified"] == 2
    assert summary["declared"] == 1
    assert summary["unknown"] == 0
