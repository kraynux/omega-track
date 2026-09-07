# Copyright (c) 2026 kraynux - Licence MIT
"""Construction d'un IdentityReport a partir des donnees deja persistees
d'un TrackRun (plan de dev §8, deja anticipe par le docstring de
domain/entities/identity_report.py en Phase 2 : "la collecte des donnees
source... reste une responsabilite de report_builder.py"). Appele par
export_orchestrator.py (Phase 8) et par toute future commande d'affichage
d'un rapport deja termine (Phase 9 `track show`) - jamais par
TrackOrchestrator (Phase 7) lui-meme, qui travaille en memoire pendant
l'execution, pas en relisant la base."""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from datetime import datetime

from omega_track.application.exceptions import TrackRunNotFoundError
from omega_track.domain.entities.findings.base import Finding
from omega_track.domain.entities.findings.path import NetworkHop, NetworkPath, PathFindingType
from omega_track.domain.entities.identity_report import IdentityReport
from omega_track.domain.services.cluster_identifier import identify_clusters
from omega_track.domain.value_objects.asn import Asn
from omega_track.domain.value_objects.geo_location import GeoLocation
from omega_track.domain.value_objects.identifiers import TrackRunId
from omega_track.domain.value_objects.ip_address import IPAddress
from omega_track.ports.repositories.finding_repository import FindingRepository
from omega_track.ports.repositories.target_repository import TargetRepository
from omega_track.ports.repositories.track_run_repository import TrackRunRepository


def build_identity_report(
    *,
    track_run_id: TrackRunId,
    track_run_repository: TrackRunRepository,
    target_repository: TargetRepository,
    finding_repository: FindingRepository,
    now: Callable[[], datetime],
) -> IdentityReport:
    track_run = track_run_repository.get(track_run_id)
    if track_run is None:
        raise TrackRunNotFoundError(track_run_id)
    target = target_repository.get(track_run.target_id)
    if target is None:
        raise TrackRunNotFoundError(track_run_id)

    findings = finding_repository.list_findings_for_run(track_run_id)
    relations = finding_repository.list_relations_for_run(track_run_id)

    return IdentityReport(
        track_run_id=track_run_id,
        target_id=track_run.target_id,
        target_value=target.value,
        profile_snapshot=track_run.profile_snapshot,
        generated_at=now(),
        findings=findings,
        relations=relations,
        clusters=identify_clusters(relations),
        paths=_rebuild_network_paths(findings),
    )


def _rebuild_network_paths(findings: list[Finding]) -> list[NetworkPath]:
    hop_findings_by_target: dict[str, list[Finding]] = defaultdict(list)
    for finding in findings:
        if finding.finding_type == PathFindingType.HOP.value:
            hop_findings_by_target[finding.payload["target_ip"]].append(finding)

    paths = []
    for target_ip_text, hop_findings in hop_findings_by_target.items():
        ordered = sorted(hop_findings, key=lambda f: f.payload["sequence"])
        paths.append(
            NetworkPath(
                target_ip=IPAddress.parse(target_ip_text),
                protocol=ordered[0].payload["protocol"],
                hops=[_finding_to_hop(f) for f in ordered],
            )
        )
    return paths


def _finding_to_hop(finding: Finding) -> NetworkHop:
    payload = finding.payload
    ip_text = payload["ip"]
    asn_payload = payload["asn"]
    geo_payload = payload["geo"]
    return NetworkHop(
        sequence=payload["sequence"],
        ip=IPAddress.parse(ip_text) if ip_text is not None else None,
        hostname=payload["hostname"],
        rtt_ms=payload["rtt_ms"],
        asn=Asn(number=asn_payload["number"], organization=asn_payload["organization"]) if asn_payload else None,
        geo=GeoLocation(**geo_payload) if geo_payload else None,
    )
