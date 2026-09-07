# Copyright (c) 2026 kraynux - Licence MIT
"""Redaction d'un ensemble de findings pour l'export (docs/PRIVACY.md §3) -
s'applique uniquement a l'export, jamais au stockage local (la base garde
toujours la donnee complete, choix explicite documente dans PRIVACY.md).

MVP (Phase 2) : seuls les types de finding "contact" sont reellement
identifies (`identity.registrant_contact`,
`organization.public_email_observed/_inferred`) - `SENSITIVE_ONLY` se
comporte comme `CONTACTS_ONLY` tant qu'aucune autre categorie de donnee
sensible n'existe reellement dans le domaine (Phase 13 introduira le
reste de la famille organization) ; a affiner a ce moment-la, pas
invente par anticipation ici."""
from __future__ import annotations

from dataclasses import replace

from omega_track.domain.entities.findings.base import Finding
from omega_track.domain.value_objects.statuses import RedactionPolicy

_REDACTED_PLACEHOLDER = "[redacted]"

_CONTACT_FINDING_TYPES = frozenset({
    "identity.registrant_contact",
    "organization.public_email_observed",
    "organization.public_email_inferred",
})


def redact_findings(findings: list[Finding], policy: RedactionPolicy) -> list[Finding]:
    if policy == RedactionPolicy.NONE:
        return findings

    if policy in (RedactionPolicy.CONTACTS_ONLY, RedactionPolicy.SENSITIVE_ONLY):
        return [_redact(f) if f.finding_type in _CONTACT_FINDING_TYPES else f for f in findings]

    if policy == RedactionPolicy.STRICT:
        return [
            _redact(f) if f.finding_type in _CONTACT_FINDING_TYPES else f
            for f in findings
        ]

    raise ValueError(f"politique de redaction inconnue : {policy}")


def _redact(finding: Finding) -> Finding:
    redacted_payload = {key: _REDACTED_PLACEHOLDER for key in finding.payload}
    return replace(finding, payload=redacted_payload, evidences=[])
