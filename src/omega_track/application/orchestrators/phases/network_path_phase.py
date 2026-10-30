# Copyright (c) 2026 kraynux - Licence MIT
"""Phase "chemin reseau" (plan de dev §7) : module `neotrace` unique.
Trace vers chaque IP retenue par le budget NeoTrace (D-012, cap par
defaut 3 - application/policies/execution_budget.py::select_neotrace_targets),
jamais au-dela : chaque hop devient un Finding `path.hop` (les hops non
repondants, deja representes explicitement par NetworkHop(ip=None) depuis
la Phase 6, restent absents de findings - un hop muet n'apporte aucune
donnee a persister, seul `NetworkPath.hops` complet compte pour l'affichage)."""
from __future__ import annotations

from dataclasses import dataclass

from omega_track.application.exceptions import CollectorUnavailableError
from omega_track.application.orchestrators._context import (
    PhaseContext,
    build_findings,
    publish_module_status,
    skip_module,
)
from omega_track.core.enums import ConfidenceLevel
from omega_track.domain.entities.findings.base import Finding
from omega_track.domain.entities.findings.path import NetworkPath, PathFindingType
from omega_track.domain.entities.track_profile import NeoTraceOptions
from omega_track.domain.entities.track_run import ModuleRun
from omega_track.domain.value_objects.collected_record import CollectedRecord
from omega_track.domain.value_objects.collection_mode import CollectionMode
from omega_track.domain.value_objects.identifiers import ModuleRunId
from omega_track.domain.value_objects.ip_address import IPAddress
from omega_track.domain.value_objects.statuses import ModuleStatus
from omega_track.ports.collectors.traceroute_collector import TracerouteCollector
from omega_track.shared.i18n import _

_NEOTRACE_MODULE = "neotrace"


@dataclass(frozen=True, slots=True)
class NetworkPathPhaseResult:
    findings: list[Finding]
    paths: list[NetworkPath]
    degraded: bool


def run_network_path_phase(
    *,
    context: PhaseContext,
    module_runs: dict[str, ModuleRun],
    targets: list[IPAddress],
    options: NeoTraceOptions,
    traceroute_collector: TracerouteCollector,
) -> NetworkPathPhaseResult:
    if _NEOTRACE_MODULE not in module_runs:
        return NetworkPathPhaseResult(findings=[], paths=[], degraded=False)

    module_run = module_runs[_NEOTRACE_MODULE]

    if not targets:
        skip_module(module_run, context, reason=_("aucune IP disponible pour NeoTrace"))
        return NetworkPathPhaseResult(findings=[], paths=[], degraded=False)
    if context.cancellation_token.is_cancelled:
        skip_module(module_run, context, reason=_("annulé avant démarrage"))
        return NetworkPathPhaseResult(findings=[], paths=[], degraded=False)
    if not traceroute_collector.is_available():
        skip_module(module_run, context, reason=_("traceroute indisponible (binaire absent ou "
                                                  "capacité insuffisante)"))
        return NetworkPathPhaseResult(findings=[], paths=[], degraded=False)

    module_run.transition_to(ModuleStatus.RUNNING, now=context.now())
    publish_module_status(context, module_run)

    findings: list[Finding] = []
    paths: list[NetworkPath] = []
    any_success = False
    any_failure = False
    cancelled_mid_run = False

    for target_ip in targets:
        if context.cancellation_token.is_cancelled:
            cancelled_mid_run = True
            break
        try:
            path = traceroute_collector.trace(target_ip, options)
        except CollectorUnavailableError:
            any_failure = True
            continue
        paths.append(path)
        findings += _hops_to_findings(path, context=context, module_run_id=module_run.id)
        any_success = True

    if cancelled_mid_run:
        module_run.transition_to(ModuleStatus.CANCELLED, now=context.now())
        ok = True
    elif any_failure and any_success:
        module_run.transition_to(ModuleStatus.PARTIAL, now=context.now())
        module_run.error_detail = _("au moins une trace NeoTrace indisponible")
        ok = False
    elif any_failure and not any_success:
        module_run.transition_to(ModuleStatus.FAILED, now=context.now())
        module_run.error_code = "collector_unavailable"
        module_run.error_detail = _("aucune trace NeoTrace disponible")
        ok = False
    else:
        module_run.transition_to(ModuleStatus.COMPLETED, now=context.now())
        ok = True

    publish_module_status(context, module_run)
    return NetworkPathPhaseResult(findings=findings, paths=paths, degraded=not ok)


def _hops_to_findings(path: NetworkPath, *, context: PhaseContext, module_run_id: ModuleRunId) -> list[Finding]:
    """Persiste TOUS les hops, y compris non repondants (`ip=None`) - un
    hop muet reste une information reelle du chemin ("hops non repondants
    representes explicitement, jamais supprimes silencieusement", plan de
    dev Phase 6 NeoTrace MVP) : l'omettre a l'ecriture rendrait
    impossible de reconstruire un NetworkPath fidele a la lecture
    (application/orchestrators/report_builder.py, Phase 8). `target_ip`/
    `protocol` sont necessaires pour regrouper les hops d'un meme chemin
    a la relecture - plusieurs cibles NeoTrace dans un meme TrackRun
    produisent sinon des hops indiscernables entre eux."""
    records = [
        CollectedRecord(
            finding_type=PathFindingType.HOP.value,
            payload={
                "target_ip": str(path.target_ip),
                "protocol": path.protocol,
                "sequence": hop.sequence,
                "ip": str(hop.ip) if hop.ip is not None else None,
                "hostname": hop.hostname,
                "rtt_ms": hop.rtt_ms,
                "asn": {"number": hop.asn.number, "organization": hop.asn.organization} if hop.asn else None,
                "geo": (
                    {
                        "country": hop.geo.country,
                        "region": hop.geo.region,
                        "city": hop.geo.city,
                        "latitude": hop.geo.latitude,
                        "longitude": hop.geo.longitude,
                        "timezone": hop.geo.timezone,
                        "precision": hop.geo.precision,
                        "source": hop.geo.source,
                    }
                    if hop.geo
                    else None
                ),
            },
            confidence=ConfidenceLevel.VERIFIED,
            source_name="neotrace",
            observed_at=context.now(),
        )
        for hop in path.hops
    ]
    return build_findings(
        records, context=context, module_run_id=module_run_id, collection_mode=CollectionMode.ACTIVE_LIGHT
    )
