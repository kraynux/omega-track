# Copyright (c) 2026 kraynux - Licence MIT
"""Phase "correlation" (plan de dev §7/§10) - pure, aucun ModuleRun
dedie : "correlation" n'est pas un nom present dans
TrackProfile.KNOWN_MODULES, ce n'est pas un module activable/
desactivable mais un post-traitement systematique des donnees deja
produites par les autres phases. Domaine -> IP directe (D-011, VERIFIED)
et certificat (SAN observe via CT log, Phase 10) -> domaine sont les 2
regles applicables a partir des donnees reellement produites par ce
projet - le nameserver partage exige de comparer plusieurs domaines
entre eux (hors perimetre d'un seul TrackRun sur une seule cible)."""
from __future__ import annotations

from omega_track.domain.entities.findings.base import Finding
from omega_track.domain.entities.findings.certificate import CertificateFindingType
from omega_track.domain.entities.relation import Relation
from omega_track.domain.services.correlation_engine import (
    infer_certificate_san_relation,
    infer_resolution_relation,
)
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.domain.value_objects.identifiers import TrackRunId
from omega_track.domain.value_objects.ip_address import IPAddress
from omega_track.domain.value_objects.target_value import TargetValue
from omega_track.shared.typing import IdFactory


def run_correlation_phase(
    *,
    track_run_id: TrackRunId,
    target_value: TargetValue,
    resolved_ips: list[IPAddress],
    certificate_findings: list[Finding] | None = None,
    distinct_ct_log_count: int = 0,
    id_factory: IdFactory,
) -> list[Relation]:
    if not isinstance(target_value, DomainName):
        return []
    domain_ref = str(target_value)

    relations = [
        infer_resolution_relation(track_run_id, domain_ref, str(ip), id_factory=id_factory) for ip in resolved_ips
    ]

    if certificate_findings:
        serials = sorted(
            {
                finding.payload["serial_number"]
                for finding in certificate_findings
                if finding.finding_type == CertificateFindingType.CERTIFICATE_OBSERVED.value
            }
        )
        relations += [
            infer_certificate_san_relation(
                track_run_id,
                f"cert:{serial}",
                domain_ref,
                distinct_ct_log_count=distinct_ct_log_count,
                id_factory=id_factory,
            )
            for serial in serials
        ]

    return relations
