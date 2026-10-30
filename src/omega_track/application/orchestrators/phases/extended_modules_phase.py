# Copyright (c) 2026 kraynux - Licence MIT
"""Phase "modules etendus gratuits" (plan de dev §10) : modules
`certificate_transparency`, `archives`, `bgp` - meme patron que
identity_phase.py/network_path_phase.py (Phase 7), chaque module a son
propre ModuleRun. Les collecteurs recus ici sont deja les objets
concrets cables par app/bootstrap.py (potentiellement des plugins,
plugins/certificates/ct_plugin.py etc. - satisfaisant structurellement
les memes ports que les collecteurs bruts) : cette fonction ne connait
que les ports (ports/collectors/*.py), jamais `plugins.*` par son nom -
Dependency Rule, `plugins/` est tier-2, `application/` tier-3, plugins
ne peut etre importe par application (voir plugins/descriptor.py).

`ct_collector`/`archive_collector`/`bgp_collector` sont optionnels : un
module active dans le profil mais sans collecteur cable (racine de
composition n'ayant pas branche cette source) est SKIPPED avec une raison
explicite - distinct d'un module simplement absent du profil (jamais de
ModuleRun du tout) et d'une source reellement indisponible
(CollectorUnavailableError -> FAILED), exactement la distinction exigee
par le plan §10 ("un plugin sans cle et indisponible... est distingue
d'un plugin desactive par configuration")."""
from __future__ import annotations

from dataclasses import dataclass

from omega_track.application.exceptions import CollectorUnavailableError
from omega_track.application.orchestrators._context import (
    PhaseContext,
    build_findings,
    publish_module_status,
    skip_module,
)
from omega_track.domain.entities.findings.base import Finding
from omega_track.domain.entities.track_run import ModuleRun
from omega_track.domain.value_objects.collection_mode import CollectionMode
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.domain.value_objects.ip_address import IPAddress
from omega_track.domain.value_objects.statuses import ModuleStatus
from omega_track.domain.value_objects.target_value import TargetValue
from omega_track.ports.collectors.archive_collector import ArchiveCollector
from omega_track.ports.collectors.bgp_collector import BgpCollector
from omega_track.ports.collectors.certificate_transparency_collector import (
    CertificateTransparencyCollector,
)
from omega_track.shared.i18n import _

_CT_MODULE = "certificate_transparency"
_ARCHIVES_MODULE = "archives"
_BGP_MODULE = "bgp"


@dataclass(frozen=True, slots=True)
class ExtendedModulesPhaseResult:
    findings: list[Finding]
    degraded: bool


def run_extended_modules_phase(
    *,
    context: PhaseContext,
    module_runs: dict[str, ModuleRun],
    target_value: TargetValue,
    enriched_ips: list[IPAddress],
    ct_collector: CertificateTransparencyCollector | None,
    archive_collector: ArchiveCollector | None,
    bgp_collector: BgpCollector | None,
) -> ExtendedModulesPhaseResult:
    domain = target_value if isinstance(target_value, DomainName) else None
    findings: list[Finding] = []
    degraded = False

    if _CT_MODULE in module_runs:
        ct_findings, ct_ok = _run_ct_module(module_runs[_CT_MODULE], context, ct_collector, domain=domain)
        findings += ct_findings
        degraded = degraded or not ct_ok

    if _ARCHIVES_MODULE in module_runs:
        archive_findings, archive_ok = _run_archive_module(
            module_runs[_ARCHIVES_MODULE], context, archive_collector, domain=domain
        )
        findings += archive_findings
        degraded = degraded or not archive_ok

    if _BGP_MODULE in module_runs:
        bgp_findings, bgp_ok = _run_bgp_module(
            module_runs[_BGP_MODULE], context, bgp_collector, ips=enriched_ips
        )
        findings += bgp_findings
        degraded = degraded or not bgp_ok

    return ExtendedModulesPhaseResult(findings=findings, degraded=degraded)


def _run_ct_module(
    module_run: ModuleRun,
    context: PhaseContext,
    collector: CertificateTransparencyCollector | None,
    *,
    domain: DomainName | None,
) -> tuple[list[Finding], bool]:
    if domain is None:
        skip_module(module_run, context, reason=_("cible IP : Certificate Transparency non "
                                                  "applicable"))
        return [], True
    if collector is None:
        skip_module(module_run, context, reason=_("aucun collecteur Certificate Transparency "
                                                  "configuré"))
        return [], True
    if context.cancellation_token.is_cancelled:
        skip_module(module_run, context, reason=_("annulé avant démarrage"))
        return [], True

    module_run.transition_to(ModuleStatus.RUNNING, now=context.now())
    publish_module_status(context, module_run)
    try:
        records = collector.collect_certificates(domain)
    except CollectorUnavailableError as exc:
        module_run.transition_to(ModuleStatus.FAILED, now=context.now())
        module_run.error_code = "collector_unavailable"
        module_run.error_detail = str(exc)
        publish_module_status(context, module_run)
        return [], False

    findings = build_findings(
        records, context=context, module_run_id=module_run.id, collection_mode=CollectionMode.PASSIVE_PUBLIC
    )
    module_run.transition_to(ModuleStatus.COMPLETED, now=context.now())
    publish_module_status(context, module_run)
    return findings, True


def _run_archive_module(
    module_run: ModuleRun,
    context: PhaseContext,
    collector: ArchiveCollector | None,
    *,
    domain: DomainName | None,
) -> tuple[list[Finding], bool]:
    if domain is None:
        skip_module(module_run, context, reason=_("cible IP : archives web non applicables"))
        return [], True
    if collector is None:
        skip_module(module_run, context, reason=_("aucun collecteur d'archives configuré"))
        return [], True
    if context.cancellation_token.is_cancelled:
        skip_module(module_run, context, reason=_("annulé avant démarrage"))
        return [], True

    module_run.transition_to(ModuleStatus.RUNNING, now=context.now())
    publish_module_status(context, module_run)
    try:
        records = collector.collect_snapshots(domain)
    except CollectorUnavailableError as exc:
        module_run.transition_to(ModuleStatus.FAILED, now=context.now())
        module_run.error_code = "collector_unavailable"
        module_run.error_detail = str(exc)
        publish_module_status(context, module_run)
        return [], False

    findings = build_findings(
        records, context=context, module_run_id=module_run.id, collection_mode=CollectionMode.PASSIVE_PUBLIC
    )
    module_run.transition_to(ModuleStatus.COMPLETED, now=context.now())
    publish_module_status(context, module_run)
    return findings, True


def _run_bgp_module(
    module_run: ModuleRun,
    context: PhaseContext,
    collector: BgpCollector | None,
    *,
    ips: list[IPAddress],
) -> tuple[list[Finding], bool]:
    if not ips:
        skip_module(module_run, context, reason=_("aucune IP disponible pour BGP"))
        return [], True
    if collector is None:
        skip_module(module_run, context, reason=_("aucun collecteur BGP configuré"))
        return [], True
    if context.cancellation_token.is_cancelled:
        skip_module(module_run, context, reason=_("annulé avant démarrage"))
        return [], True

    module_run.transition_to(ModuleStatus.RUNNING, now=context.now())
    publish_module_status(context, module_run)

    findings: list[Finding] = []
    any_success = False
    any_failure = False
    cancelled_mid_run = False

    for ip in ips:
        if context.cancellation_token.is_cancelled:
            cancelled_mid_run = True
            break
        try:
            records = collector.collect_announcements(ip)
            findings += build_findings(
                records, context=context, module_run_id=module_run.id, collection_mode=CollectionMode.PASSIVE_PUBLIC
            )
            any_success = True
        except CollectorUnavailableError:
            any_failure = True

    if cancelled_mid_run:
        module_run.transition_to(ModuleStatus.CANCELLED, now=context.now())
        ok = True
    elif any_failure and any_success:
        module_run.transition_to(ModuleStatus.PARTIAL, now=context.now())
        module_run.error_detail = _("au moins une requête BGP indisponible")
        ok = False
    elif any_failure and not any_success:
        module_run.transition_to(ModuleStatus.FAILED, now=context.now())
        module_run.error_code = "collector_unavailable"
        module_run.error_detail = _("aucune réponse BGP disponible")
        ok = False
    else:
        module_run.transition_to(ModuleStatus.COMPLETED, now=context.now())
        ok = True

    publish_module_status(context, module_run)
    return findings, ok
