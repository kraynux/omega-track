# Copyright (c) 2026 kraynux - Licence MIT
"""Phase "identite/DNS" (plan de dev §7) : modules `dns`, `reverse_dns`,
`rdap`. Chaque module a son propre ModuleRun (etat + explication en cas
d'echec) meme s'ils partagent cette phase - "identité/DNS" designe une
categorie d'execution, pas un module unique.

Le budget d'enrichissement (D-012, application/policies/
execution_budget.py) est applique ici, juste apres la resolution DNS :
c'est le point naturel ou les IPs candidates a un enrichissement complet
(RDAP+GeoIP) sont connues pour la premiere fois."""
from __future__ import annotations

from dataclasses import dataclass

from omega_track.application.exceptions import CollectorUnavailableError
from omega_track.application.orchestrators._context import (
    PhaseContext,
    build_findings,
    publish_module_status,
    skip_module,
)
from omega_track.application.policies.execution_budget import (
    EnrichmentBudget,
    allocate_enrichment_budget,
)
from omega_track.core.enums import ConfidenceLevel
from omega_track.domain.entities.findings.base import Finding
from omega_track.domain.entities.findings.network import NetworkFindingType
from omega_track.domain.entities.track_profile import ExecutionLimits
from omega_track.domain.entities.track_run import ModuleRun
from omega_track.domain.value_objects.collected_record import CollectedRecord
from omega_track.domain.value_objects.collection_mode import CollectionMode
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.domain.value_objects.identifiers import ModuleRunId
from omega_track.domain.value_objects.ip_address import IPAddress
from omega_track.domain.value_objects.statuses import ModuleStatus
from omega_track.domain.value_objects.target_value import TargetValue
from omega_track.ports.collectors.dns_collector import DnsCollector
from omega_track.ports.collectors.rdap_collector import RdapCollector
from omega_track.shared.i18n import _

_DNS_MODULE = "dns"
_REVERSE_DNS_MODULE = "reverse_dns"
_RDAP_MODULE = "rdap"


@dataclass(frozen=True, slots=True)
class IdentityPhaseResult:
    findings: list[Finding]
    resolved_ips: list[IPAddress]
    budget: EnrichmentBudget
    degraded: bool


def run_identity_phase(
    *,
    context: PhaseContext,
    module_runs: dict[str, ModuleRun],
    target_value: TargetValue,
    limits: ExecutionLimits,
    dns_collector: DnsCollector,
    rdap_collector: RdapCollector,
) -> IdentityPhaseResult:
    findings: list[Finding] = []
    degraded = False
    domain = target_value if isinstance(target_value, DomainName) else None
    representative_ip = target_value if isinstance(target_value, IPAddress) else None

    resolved_ips: list[IPAddress] = []
    if _DNS_MODULE in module_runs:
        dns_findings, resolved_ips, dns_ok = _run_dns_module(
            module_runs[_DNS_MODULE], context, dns_collector, domain=domain
        )
        findings += dns_findings
        degraded = degraded or not dns_ok

    if representative_ip is not None:
        resolved_ips = [representative_ip]

    if _REVERSE_DNS_MODULE in module_runs:
        reverse_findings, reverse_ok = _run_reverse_dns_module(
            module_runs[_REVERSE_DNS_MODULE], context, dns_collector, target_ip=resolved_ips[0] if resolved_ips else None
        )
        findings += reverse_findings
        degraded = degraded or not reverse_ok

    budget = allocate_enrichment_budget(resolved_ips, limits=limits)
    if budget.excess:
        excess_module_run_id = module_runs[_DNS_MODULE].id if _DNS_MODULE in module_runs else None
        for excess_ip in budget.excess:
            findings.append(_ip_observed_finding(excess_ip, context=context, module_run_id=excess_module_run_id))

    if _RDAP_MODULE in module_runs:
        rdap_findings, rdap_ok = _run_rdap_module(
            module_runs[_RDAP_MODULE], context, rdap_collector, domain=domain, ips=budget.enriched
        )
        findings += rdap_findings
        degraded = degraded or not rdap_ok

    return IdentityPhaseResult(findings=findings, resolved_ips=resolved_ips, budget=budget, degraded=degraded)


def _run_dns_module(
    module_run: ModuleRun,
    context: PhaseContext,
    dns_collector: DnsCollector,
    *,
    domain: DomainName | None,
) -> tuple[list[Finding], list[IPAddress], bool]:
    if domain is None:
        skip_module(module_run, context, reason=_("cible IP : résolution DNS non applicable"))
        return [], [], True
    if context.cancellation_token.is_cancelled:
        skip_module(module_run, context, reason=_("annulé avant démarrage"))
        return [], [], True

    module_run.transition_to(ModuleStatus.RUNNING, now=context.now())
    publish_module_status(context, module_run)
    try:
        records = dns_collector.resolve(domain)
    except CollectorUnavailableError as exc:
        module_run.transition_to(ModuleStatus.FAILED, now=context.now())
        module_run.error_code = "collector_unavailable"
        module_run.error_detail = str(exc)
        publish_module_status(context, module_run)
        return [], [], False

    findings = build_findings(
        records, context=context, module_run_id=module_run.id, collection_mode=CollectionMode.ACTIVE_LIGHT
    )
    resolved_ips = [
        IPAddress.parse(record.payload["address"])
        for record in records
        if record.finding_type in ("dns.a_record", "dns.aaaa_record")
    ]
    module_run.transition_to(ModuleStatus.COMPLETED, now=context.now())
    publish_module_status(context, module_run)
    return findings, resolved_ips, True


def _run_reverse_dns_module(
    module_run: ModuleRun,
    context: PhaseContext,
    dns_collector: DnsCollector,
    *,
    target_ip: IPAddress | None,
) -> tuple[list[Finding], bool]:
    if target_ip is None:
        skip_module(module_run, context, reason=_("aucune IP résolue pour effectuer un PTR"))
        return [], True
    if context.cancellation_token.is_cancelled:
        skip_module(module_run, context, reason=_("annulé avant démarrage"))
        return [], True

    module_run.transition_to(ModuleStatus.RUNNING, now=context.now())
    publish_module_status(context, module_run)
    try:
        record = dns_collector.reverse_lookup(target_ip)
    except CollectorUnavailableError as exc:
        module_run.transition_to(ModuleStatus.FAILED, now=context.now())
        module_run.error_code = "collector_unavailable"
        module_run.error_detail = str(exc)
        publish_module_status(context, module_run)
        return [], False

    records = [record] if record is not None else []
    findings = build_findings(
        records, context=context, module_run_id=module_run.id, collection_mode=CollectionMode.ACTIVE_LIGHT
    )
    module_run.transition_to(ModuleStatus.COMPLETED, now=context.now())
    publish_module_status(context, module_run)
    return findings, True


def _run_rdap_module(
    module_run: ModuleRun,
    context: PhaseContext,
    rdap_collector: RdapCollector,
    *,
    domain: DomainName | None,
    ips: list[IPAddress],
) -> tuple[list[Finding], bool]:
    if context.cancellation_token.is_cancelled:
        skip_module(module_run, context, reason=_("annulé avant démarrage"))
        return [], True

    module_run.transition_to(ModuleStatus.RUNNING, now=context.now())
    publish_module_status(context, module_run)

    findings: list[Finding] = []
    any_success = False
    any_failure = False
    cancelled_mid_run = False

    if domain is not None:
        try:
            records = rdap_collector.collect_domain_registration(domain)
            findings += build_findings(
                records, context=context, module_run_id=module_run.id, collection_mode=CollectionMode.PASSIVE_PUBLIC
            )
            any_success = True
        except CollectorUnavailableError:
            any_failure = True

    for ip in ips:
        if context.cancellation_token.is_cancelled:
            cancelled_mid_run = True
            break
        try:
            records = rdap_collector.collect_ip_registration(ip)
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
        module_run.error_detail = _("au moins une requête RDAP indisponible")
        ok = False
    elif any_failure and not any_success:
        module_run.transition_to(ModuleStatus.FAILED, now=context.now())
        module_run.error_code = "collector_unavailable"
        module_run.error_detail = _("aucune réponse RDAP disponible")
        ok = False
    else:
        module_run.transition_to(ModuleStatus.COMPLETED, now=context.now())
        ok = True

    publish_module_status(context, module_run)
    return findings, ok


def _ip_observed_finding(
    ip: IPAddress, *, context: PhaseContext, module_run_id: ModuleRunId | None
) -> Finding:
    assert module_run_id is not None, "budget.excess non vide implique que le module dns a resolu des IPs"
    record = CollectedRecord(
        finding_type=NetworkFindingType.IP_OBSERVED.value,
        payload={"address": str(ip)},
        confidence=ConfidenceLevel.VERIFIED,
        source_name=_DNS_MODULE,
        observed_at=context.now(),
    )
    return build_findings(
        [record], context=context, module_run_id=module_run_id, collection_mode=CollectionMode.ACTIVE_LIGHT
    )[0]
