# Copyright (c) 2026 kraynux - Licence MIT
"""Phase "sources de reputation a cle" (plan de dev §12) : modules
`virustotal`/`hibp`, meme patron que extended_modules_phase.py (Phase 10)
etendu d'une pre-verification cle/quota AVANT tout appel reseau -
jamais un simple `collector is None` : une source peut etre cablee mais
sa cle absente, ou cablee-et-cle-presente mais en periode de backoff
suite a un quota deja depasse sur un run precedent
(application/policies/quota_backoff.py).

Ordre de verification (chacune AVANT de passer le ModuleRun a RUNNING,
jamais apres - la machine a etats de ModuleRun n'autorise SKIPPED que
depuis PENDING, voir domain/value_objects/statuses.py) :
1. collecteur non cable (racine de composition n'a pas construit cette
   source) -> SKIPPED "aucun collecteur configure" (meme message que
   Phase 10 pour CT/archives/BGP).
2. cle API absente -> SKIPPED + Finding `collection.not_executed_no_key`
   (plan §12 "statut non exécuté faute de clé, jamais une erreur
   bloquante").
3. backoff actif (quota deja depasse recemment) -> SKIPPED + Finding
   `collection.quota_exceeded`, sans jamais appeler le collecteur.
4. sinon appel reel : `QuotaExceededError` -> FAILED (le module a
   vraiment ete tente) + backoff enregistre pour le prochain run ;
   `CollectorUnavailableError` -> FAILED generique."""
from __future__ import annotations

from dataclasses import dataclass

from omega_track.application.exceptions import CollectorUnavailableError, QuotaExceededError
from omega_track.application.orchestrators._context import (
    PhaseContext,
    build_findings,
    publish_module_status,
    skip_module,
)
from omega_track.application.policies.quota_backoff import is_in_backoff, record_quota_exceeded
from omega_track.application.queries.get_source_disclosure import secret_name_for
from omega_track.core.enums import ConfidenceLevel
from omega_track.domain.entities.findings.base import Finding
from omega_track.domain.entities.findings.collection import CollectionFindingType
from omega_track.domain.entities.track_run import ModuleRun
from omega_track.domain.value_objects.collected_record import CollectedRecord
from omega_track.domain.value_objects.collection_mode import CollectionMode
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.domain.value_objects.statuses import ModuleStatus
from omega_track.domain.value_objects.target_value import TargetValue
from omega_track.ports.collectors.reputation_collector import ReputationCollector
from omega_track.ports.repositories.settings_repository import SettingsRepository
from omega_track.ports.services.secret_store import SecretStore
from omega_track.shared.i18n import _

_VIRUSTOTAL_MODULE = "virustotal"
_HIBP_MODULE = "hibp"


@dataclass(frozen=True, slots=True)
class ReputationPhaseResult:
    findings: list[Finding]
    degraded: bool


def run_reputation_phase(
    *,
    context: PhaseContext,
    module_runs: dict[str, ModuleRun],
    target_value: TargetValue,
    virustotal_collector: ReputationCollector | None,
    hibp_collector: ReputationCollector | None,
    secret_store: SecretStore | None,
    settings_repository: SettingsRepository | None,
) -> ReputationPhaseResult:
    domain = target_value if isinstance(target_value, DomainName) else None
    findings: list[Finding] = []
    degraded = False

    if _VIRUSTOTAL_MODULE in module_runs:
        vt_findings, vt_ok = _run_keyed_module(
            module_runs[_VIRUSTOTAL_MODULE],
            context,
            virustotal_collector,
            secret_store=secret_store,
            settings_repository=settings_repository,
            source_name=_VIRUSTOTAL_MODULE,
            domain=domain,
        )
        findings += vt_findings
        degraded = degraded or not vt_ok

    if _HIBP_MODULE in module_runs:
        hibp_findings, hibp_ok = _run_keyed_module(
            module_runs[_HIBP_MODULE],
            context,
            hibp_collector,
            secret_store=secret_store,
            settings_repository=settings_repository,
            source_name=_HIBP_MODULE,
            domain=domain,
        )
        findings += hibp_findings
        degraded = degraded or not hibp_ok

    return ReputationPhaseResult(findings=findings, degraded=degraded)


def _run_keyed_module(
    module_run: ModuleRun,
    context: PhaseContext,
    collector: ReputationCollector | None,
    *,
    secret_store: SecretStore | None,
    settings_repository: SettingsRepository | None,
    source_name: str,
    domain: DomainName | None,
) -> tuple[list[Finding], bool]:
    if domain is None:
        skip_module(module_run, context, reason=_("cible IP : {source_name} non applicable").format(source_name=source_name))
        return [], True
    if collector is None:
        skip_module(module_run, context, reason=_("aucun collecteur {source_name} configuré").format(source_name=source_name))
        return [], True
    if context.cancellation_token.is_cancelled:
        skip_module(module_run, context, reason=_("annulé avant démarrage"))
        return [], True

    if (
        secret_store is None
        or settings_repository is None
        or not secret_store.get_secret(secret_name_for(source_name))
    ):
        skip_module(module_run, context, reason=_("clé API {source_name} non configurée").format(source_name=source_name))
        finding = _collection_finding(
            module_run, context, CollectionFindingType.NOT_EXECUTED_NO_KEY, source_name
        )
        return [finding], True

    if is_in_backoff(settings_repository=settings_repository, source_name=source_name, now=context.now):
        skip_module(module_run, context, reason=_("quota {source_name} dépassé (en attente de "
                                                  "réessai)").format(source_name=source_name))
        finding = _collection_finding(
            module_run, context, CollectionFindingType.QUOTA_EXCEEDED, source_name
        )
        return [finding], True

    module_run.transition_to(ModuleStatus.RUNNING, now=context.now())
    publish_module_status(context, module_run)
    try:
        records = collector.collect_domain_reputation(domain)
    except QuotaExceededError as exc:
        record_quota_exceeded(settings_repository=settings_repository, source_name=source_name, now=context.now)
        module_run.transition_to(ModuleStatus.FAILED, now=context.now())
        module_run.error_code = "quota_exceeded"
        module_run.error_detail = str(exc)
        publish_module_status(context, module_run)
        finding = _collection_finding(
            module_run, context, CollectionFindingType.QUOTA_EXCEEDED, source_name
        )
        return [finding], False
    except CollectorUnavailableError as exc:
        module_run.transition_to(ModuleStatus.FAILED, now=context.now())
        module_run.error_code = "collector_unavailable"
        module_run.error_detail = str(exc)
        publish_module_status(context, module_run)
        return [], False

    findings = build_findings(
        records, context=context, module_run_id=module_run.id, collection_mode=CollectionMode.API_KEY
    )
    module_run.transition_to(ModuleStatus.COMPLETED, now=context.now())
    publish_module_status(context, module_run)
    return findings, True


def _collection_finding(
    module_run: ModuleRun, context: PhaseContext, finding_type: CollectionFindingType, source_name: str
) -> Finding:
    record = CollectedRecord(
        finding_type=finding_type.value,
        payload={"source": source_name},
        confidence=ConfidenceLevel.UNKNOWN,
        source_name=source_name,
        observed_at=context.now(),
    )
    return build_findings(
        [record], context=context, module_run_id=module_run.id, collection_mode=CollectionMode.API_KEY
    )[0]
