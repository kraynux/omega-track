# Copyright (c) 2026 kraynux - Licence MIT
from datetime import datetime, timezone

from omega_track.core.enums import ConfidenceLevel
from omega_track.domain.entities.findings.base import Finding
from omega_track.domain.services.redaction_service import redact_findings
from omega_track.domain.value_objects.collection_mode import CollectionMode
from omega_track.domain.value_objects.identifiers import FindingId, ModuleRunId, TrackRunId
from omega_track.domain.value_objects.statuses import RedactionPolicy

_NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def _finding(finding_type: str) -> Finding:
    return Finding(
        id=FindingId("f1"), track_run_id=TrackRunId("run-1"), module_run_id=ModuleRunId("mr-1"),
        finding_type=finding_type, payload={"email": "contact@example.com"},
        confidence=ConfidenceLevel.DECLARED, collection_mode=CollectionMode.PASSIVE_PUBLIC,
        source_name="rdap", observed_at=_NOW, collected_at=_NOW,
    )


def test_none_policy_leaves_findings_untouched() -> None:
    findings = [_finding("identity.registrant_contact")]
    assert redact_findings(findings, RedactionPolicy.NONE) == findings


def test_contacts_only_redacts_contact_findings() -> None:
    findings = [_finding("identity.registrant_contact"), _finding("dns.a_record")]
    redacted = redact_findings(findings, RedactionPolicy.CONTACTS_ONLY)
    assert redacted[0].payload["email"] == "[redacted]"
    assert redacted[1].payload["email"] == "contact@example.com"


def test_redaction_clears_evidences() -> None:
    finding = _finding("organization.public_email_observed")
    redacted = redact_findings([finding], RedactionPolicy.STRICT)
    assert redacted[0].evidences == []


def test_non_contact_finding_untouched_by_strict() -> None:
    findings = [_finding("dns.a_record")]
    redacted = redact_findings(findings, RedactionPolicy.STRICT)
    assert redacted[0].payload["email"] == "contact@example.com"
