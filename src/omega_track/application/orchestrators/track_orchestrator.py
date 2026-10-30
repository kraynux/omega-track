# Copyright (c) 2026 kraynux - Licence MIT
"""TrackOrchestrator (plan de dev §7) - pilote un TrackRun a partir de
son TrackProfile : sequence les phases (identite -> chemin reseau ->
correlation, toujours dans cet ordre puisque le chemin reseau et la
correlation dependent des IPs resolues par la phase identite - "phases
dependantes sequentielles", aucun parallelisme entre phases), persiste
progressivement (findings + etat du TrackRun apres chaque phase, pas
seulement a la toute fin - critere de sortie "annulation propre sans
donnees corrompues" : tout ce qui est deja termine reste acquis meme si
la suite est annulee/interrompue), publie la progression via
EventPublisher, et respecte un budget de temps global cooperatif
(ExecutionLimits.global_timeout_seconds, verifie entre les phases).

Parallelisme delibere hors perimetre de cette implementation : les
collecteurs de la Phase 6 sont tous synchrones/bloquants et n'ont jamais
ete concus/testes pour un appel concurrent - "enrichissements par IP
parallelisables avec limite" (plan de dev §7) reste une propriete
d'architecture possible (rien n'empeche de paralleliser
identity_phase.py plus tard), pas un mecanisme de threads livre ici."""
from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from omega_track.application.orchestrators._context import PhaseContext, skip_module
from omega_track.application.orchestrators.cancellation import CancellationToken
from omega_track.application.orchestrators.phases.correlation_phase import run_correlation_phase
from omega_track.application.orchestrators.phases.extended_modules_phase import (
    run_extended_modules_phase,
)
from omega_track.application.orchestrators.phases.identity_phase import run_identity_phase
from omega_track.application.orchestrators.phases.network_path_phase import run_network_path_phase
from omega_track.application.orchestrators.phases.reputation_phase import run_reputation_phase
from omega_track.application.policies.execution_budget import select_neotrace_targets
from omega_track.domain.entities.findings.base import Finding
from omega_track.domain.entities.findings.certificate import CertificateFindingType
from omega_track.domain.entities.track_profile import ExecutionLimits
from omega_track.domain.entities.track_run import ModuleRun, TrackRun
from omega_track.domain.value_objects.collection_mode import CollectionMode
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.domain.value_objects.identifiers import ModuleRunId
from omega_track.domain.value_objects.ip_address import IPAddress
from omega_track.domain.value_objects.statuses import ModuleStatus, TrackStatus
from omega_track.domain.value_objects.target_value import TargetValue
from omega_track.ports.collectors.archive_collector import ArchiveCollector
from omega_track.ports.collectors.bgp_collector import BgpCollector
from omega_track.ports.collectors.certificate_transparency_collector import (
    CertificateTransparencyCollector,
)
from omega_track.ports.collectors.dns_collector import DnsCollector
from omega_track.ports.collectors.rdap_collector import RdapCollector
from omega_track.ports.collectors.reputation_collector import ReputationCollector
from omega_track.ports.collectors.traceroute_collector import TracerouteCollector
from omega_track.ports.repositories.finding_repository import FindingRepository
from omega_track.ports.repositories.settings_repository import SettingsRepository
from omega_track.ports.repositories.track_run_repository import TrackRunRepository
from omega_track.ports.services.event_publisher import EventPublisher
from omega_track.ports.services.log_correlation import LogCorrelation
from omega_track.ports.services.secret_store import SecretStore
from omega_track.shared.i18n import _
from omega_track.shared.typing import IdFactory

_MODULE_COLLECTION_MODES: dict[str, CollectionMode] = {
    "dns": CollectionMode.ACTIVE_LIGHT,
    "reverse_dns": CollectionMode.ACTIVE_LIGHT,
    "rdap": CollectionMode.PASSIVE_PUBLIC,
    "neotrace": CollectionMode.ACTIVE_LIGHT,
    "certificate_transparency": CollectionMode.PASSIVE_PUBLIC,
    "archives": CollectionMode.PASSIVE_PUBLIC,
    "bgp": CollectionMode.PASSIVE_PUBLIC,
    "virustotal": CollectionMode.API_KEY,
    "hibp": CollectionMode.API_KEY,
}
_SUPPORTED_EXTENDED_MODULES: frozenset[str] = frozenset(
    {"certificate_transparency", "archives", "bgp", "virustotal", "hibp"}
)
"""Modules etendus (Phases 10/12) reellement executables par cet
orchestrateur - `reputation_free`/`organization` sont des noms valides de
TrackProfile.KNOWN_MODULES (Phase 2) mais n'ont pas encore de collecteur
reel (Phases 10/13) : un profil qui les active recoit quand meme un
ModuleRun, immediatement SKIPPED avec une raison explicite ("module non
encore implemente"), jamais silencieusement ignore."""


class TrackOrchestrator:
    def __init__(
        self,
        *,
        dns_collector: DnsCollector,
        rdap_collector: RdapCollector,
        traceroute_collector: TracerouteCollector,
        finding_repository: FindingRepository,
        track_run_repository: TrackRunRepository,
        event_publisher: EventPublisher,
        id_factory: IdFactory,
        now: Callable[[], datetime],
        log_correlation: LogCorrelation | None = None,
        ct_collector: CertificateTransparencyCollector | None = None,
        archive_collector: ArchiveCollector | None = None,
        bgp_collector: BgpCollector | None = None,
        virustotal_collector: ReputationCollector | None = None,
        hibp_collector: ReputationCollector | None = None,
        secret_store: SecretStore | None = None,
        settings_repository: SettingsRepository | None = None,
    ) -> None:
        self._dns_collector = dns_collector
        self._rdap_collector = rdap_collector
        self._traceroute_collector = traceroute_collector
        self._finding_repository = finding_repository
        self._track_run_repository = track_run_repository
        self._event_publisher = event_publisher
        self._id_factory = id_factory
        self._now = now
        self._log_correlation = log_correlation
        self._ct_collector = ct_collector
        self._archive_collector = archive_collector
        self._bgp_collector = bgp_collector
        self._virustotal_collector = virustotal_collector
        self._hibp_collector = hibp_collector
        self._secret_store = secret_store
        self._settings_repository = settings_repository

    def run(
        self,
        *,
        track_run: TrackRun,
        target_value: TargetValue,
        cancellation_token: CancellationToken | None = None,
    ) -> TrackRun:
        token = cancellation_token if cancellation_token is not None else CancellationToken()
        limits = track_run.profile_snapshot.limits

        profile = track_run.profile_snapshot
        extended_modules = profile.enabled_extended_modules()
        unsupported_extended_modules = extended_modules - _SUPPORTED_EXTENDED_MODULES

        for module_name in profile.enabled_mvp_modules() | extended_modules:
            track_run.module_runs[module_name] = ModuleRun(
                id=ModuleRunId(self._id_factory()),
                module_name=module_name,
                status=ModuleStatus.PENDING,
                collection_mode=_MODULE_COLLECTION_MODES.get(module_name, CollectionMode.PASSIVE_PUBLIC),
            )

        track_run.start(now=self._now())
        self._track_run_repository.save(track_run)

        log_token = (
            self._log_correlation.set_current_track_run_id(str(track_run.id))
            if self._log_correlation is not None
            else None
        )
        try:
            return self._run_phases(track_run, target_value, limits, token, unsupported_extended_modules)
        finally:
            if self._log_correlation is not None:
                self._log_correlation.reset_current_track_run_id(log_token)

    def _run_phases(
        self,
        track_run: TrackRun,
        target_value: TargetValue,
        limits: ExecutionLimits,
        token: CancellationToken,
        unsupported_extended_modules: set[str],
    ) -> TrackRun:
        context = PhaseContext(
            track_run_id=track_run.id,
            id_factory=self._id_factory,
            now=self._now,
            event_publisher=self._event_publisher,
            cancellation_token=token,
        )
        for module_name in unsupported_extended_modules:
            skip_module(track_run.module_runs[module_name], context, reason=_("module non encore implémenté"))

        self._event_publisher.publish_progress(track_run.id, "demarrage", 0.0)
        start_time = self._now()

        all_findings: list[Finding] = []
        degraded = False
        timed_out = False
        resolved_ips: list[IPAddress] = []

        if self._budget_exceeded(start_time, limits):
            timed_out = True
            self._skip_pending(track_run.module_runs, context, reason=_("budget de temps global dépassé"))
        else:
            identity_result = run_identity_phase(
                context=context,
                module_runs=track_run.module_runs,
                target_value=target_value,
                limits=limits,
                dns_collector=self._dns_collector,
                rdap_collector=self._rdap_collector,
            )
            all_findings += identity_result.findings
            degraded = degraded or identity_result.degraded
            resolved_ips = identity_result.resolved_ips
            self._persist_progress(track_run, identity_result.findings, _("identité terminée"), 0.5)

            if self._budget_exceeded(start_time, limits):
                timed_out = True
                self._skip_pending(track_run.module_runs, context, reason=_("budget de temps global dépassé"))
            else:
                neotrace_targets = select_neotrace_targets(identity_result.budget, limits=limits)
                path_result = run_network_path_phase(
                    context=context,
                    module_runs=track_run.module_runs,
                    targets=neotrace_targets,
                    options=track_run.profile_snapshot.neotrace,
                    traceroute_collector=self._traceroute_collector,
                )
                all_findings += path_result.findings
                degraded = degraded or path_result.degraded
                self._persist_progress(track_run, path_result.findings, _("chemin réseau terminé"), 0.85)

            if self._budget_exceeded(start_time, limits):
                timed_out = True
                self._skip_pending(track_run.module_runs, context, reason=_("budget de temps global dépassé"))
            else:
                extended_result = run_extended_modules_phase(
                    context=context,
                    module_runs=track_run.module_runs,
                    target_value=target_value,
                    enriched_ips=identity_result.budget.enriched,
                    ct_collector=self._ct_collector,
                    archive_collector=self._archive_collector,
                    bgp_collector=self._bgp_collector,
                )
                all_findings += extended_result.findings
                degraded = degraded or extended_result.degraded
                self._persist_progress(track_run, extended_result.findings, _("modules étendus terminés"), 0.9)

            if self._budget_exceeded(start_time, limits):
                timed_out = True
                self._skip_pending(track_run.module_runs, context, reason=_("budget de temps global dépassé"))
            else:
                reputation_result = run_reputation_phase(
                    context=context,
                    module_runs=track_run.module_runs,
                    target_value=target_value,
                    virustotal_collector=self._virustotal_collector,
                    hibp_collector=self._hibp_collector,
                    secret_store=self._secret_store,
                    settings_repository=self._settings_repository,
                )
                all_findings += reputation_result.findings
                degraded = degraded or reputation_result.degraded
                self._persist_progress(track_run, reputation_result.findings, _("sources à clé terminées"), 0.95)

            certificate_findings = [
                finding
                for finding in all_findings
                if finding.finding_type == CertificateFindingType.CERTIFICATE_OBSERVED.value
            ]
            distinct_ct_log_count = 0
            if certificate_findings and isinstance(target_value, DomainName) and self._ct_collector is not None:
                distinct_ct_log_count = self._ct_collector.distinct_log_count(target_value)

            relations = run_correlation_phase(
                track_run_id=track_run.id,
                target_value=target_value,
                resolved_ips=resolved_ips,
                certificate_findings=certificate_findings,
                distinct_ct_log_count=distinct_ct_log_count,
                id_factory=self._id_factory,
            )
            if relations:
                self._finding_repository.save_relations(relations)

        self._finalize(track_run, token=token, degraded=degraded, timed_out=timed_out, has_findings=bool(all_findings))
        return track_run

    def _finalize(
        self,
        track_run: TrackRun,
        *,
        token: CancellationToken,
        degraded: bool,
        timed_out: bool,
        has_findings: bool,
    ) -> None:
        if token.is_cancelled:
            track_run.cancel(now=self._now())
        elif not has_findings and degraded:
            track_run.finish(status=TrackStatus.FAILED, now=self._now())
        elif degraded or timed_out:
            track_run.finish(status=TrackStatus.PARTIAL, now=self._now())
        else:
            track_run.finish(status=TrackStatus.COMPLETED, now=self._now())

        track_run.update_progress(1.0)
        self._track_run_repository.save(track_run)
        self._event_publisher.publish_progress(track_run.id, _("terminé"), 1.0)

    def _budget_exceeded(self, start_time: datetime, limits: ExecutionLimits) -> bool:
        return (self._now() - start_time).total_seconds() >= limits.global_timeout_seconds

    def _persist_progress(
        self, track_run: TrackRun, findings: list[Finding], message: str, percentage: float
    ) -> None:
        if findings:
            self._finding_repository.save_findings(findings)
        track_run.update_progress(percentage)
        self._track_run_repository.save(track_run)
        self._event_publisher.publish_progress(track_run.id, message, percentage)

    def _skip_pending(
        self, module_runs: dict[str, ModuleRun], context: PhaseContext, *, reason: str
    ) -> None:
        for module_run in module_runs.values():
            if module_run.status == ModuleStatus.PENDING:
                skip_module(module_run, context, reason=reason)
