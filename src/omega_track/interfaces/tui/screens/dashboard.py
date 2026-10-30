# Copyright (c) 2026 kraynux - Licence MIT
"""Ecran Dashboard : vue d'ensemble en lecture seule - premier ecran de
contenu apres l'accueil (plan de dev §11, ordre d'implementation des
ecrans). Aucun use case dedie n'existe pour un "dashboard" (absent du
plan de dev §9, apparu seulement dans l'ordre des ecrans TUI) : cet
ecran recompose une vue synthetique a partir des memes queries que les
autres ecrans, plutot que d'inventer une nouvelle couche applicative
pour un simple resume.

Ne reproduit PLUS le tableau des observations recentes (retour
utilisateur Phase 12 : "j'ai du mal a faire la difference entre le
dashboard et l'historique, c'est les memes donnees") - ce tableau
detaille avec filtres vit deja dans screens/history.py, jamais duplique
ici.

Retour utilisateur ulterieur ("dashboard vraiment pauvre... ca doit
etre complet et visuel, mets en un maximum") : enrichi avec tout ce qui
est deja disponible sans nouvelle methode de port - `Target.last_track_at`/
`last_status` (deja portes par le domaine, jamais exploites nulle part
avant cet ecran), agregation des `ModuleRun` de tous les `TrackRun` deja
charges en memoire (aucune requete supplementaire), etat de backoff des
sources a cle (`SourceStatusView.in_backoff`, deja calcule par
`get_source_status` mais jamais affiche). Seule exception qui interroge
un peu plus que le strict minimum : la typologie des derniers findings,
bornee aux 15 observations terminees les plus recentes (pas toutes -
`FindingRepository` n'a pas de requete d'agregation globale et ne doit
pas en gagner une pour un simple resume, voir son en-tete)."""
from __future__ import annotations

from collections import Counter
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Button, Footer, Header, Static

from omega_track.application.policies.provider_selection import resolve_active_geoip_provider
from omega_track.application.queries.get_geoip_status import get_geoip_database_status
from omega_track.application.queries.get_source_disclosure import list_known_reputation_sources
from omega_track.application.queries.get_source_status import get_source_status
from omega_track.application.queries.list_targets import list_targets
from omega_track.application.queries.list_track_runs import list_track_runs
from omega_track.domain.entities.track_profile import KNOWN_MODULES
from omega_track.domain.value_objects.identifiers import TargetId
from omega_track.domain.value_objects.statuses import ModuleStatus, TrackStatus
from omega_track.domain.value_objects.target_value import TargetKind
from omega_track.interfaces.tui.screens._base import OmegaScreen
from omega_track.interfaces.tui.screens.history import HistoryScreen
from omega_track.shared.i18n import _

if TYPE_CHECKING:
    from omega_track.app.container import DependencyContainer
    from omega_track.domain.entities.target import Target
    from omega_track.domain.entities.track_run import TrackRun

_FINDINGS_SAMPLE_SIZE = 15
"""Nombre d'observations terminees les plus recentes utilisees pour la
typologie des findings - un compromis, pas un maximum theorique (voir
note du module) : agreger TOUTES les observations exigerait soit une
nouvelle requete d'agregation en base, soit charger l'integralite des
findings de l'historique en memoire a chaque ouverture de l'ecran."""

_STATUS_COLOR = {
    TrackStatus.COMPLETED: "green",
    TrackStatus.PARTIAL: "yellow",
    TrackStatus.FAILED: "red",
    TrackStatus.CANCELLED: "grey62",
    TrackStatus.RUNNING: "cyan",
    TrackStatus.QUEUED: "grey62",
}

_MODULE_STATUS_COLOR = {
    ModuleStatus.COMPLETED: "green",
    ModuleStatus.PARTIAL: "yellow",
    ModuleStatus.FAILED: "red",
    ModuleStatus.SKIPPED: "grey62",
    ModuleStatus.CANCELLED: "grey62",
}


def _bar(count: int, maximum: int, width: int = 20) -> str:
    if maximum <= 0 or count <= 0:
        return ""
    filled = max(1, round(count / maximum * width))
    return "█" * filled


class DashboardScreen(OmegaScreen):
    """Vue d'ensemble : la synthese la plus complete possible de l'etat
    actuel de l'application, sans dupliquer le tableau detaille de
    l'ecran Historique."""

    def __init__(self, *, container: DependencyContainer) -> None:
        super().__init__()
        self._container = container

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(classes="omega-panel"):
            yield Static(_("DASHBOARD"), classes="omega-title")

            yield Static(_("Cibles"), classes="omega-subtitle")
            yield Static("", id="targets-text")

            yield Static(_("Dernière activité"), classes="omega-subtitle")
            yield Static("", id="last-activity-text")

            yield Static(_("Observations par statut"), classes="omega-subtitle")
            yield Static("", id="status-breakdown-text")

            yield Static(_("Fiabilité par module (sur l'historique complet)"), classes="omega-subtitle")
            yield Static("", id="module-reliability-text")

            yield Static(_("Typologie des derniers findings"), classes="omega-subtitle")
            yield Static("", id="findings-typology-text")

            yield Static("GeoIP", classes="omega-subtitle")
            yield Static("", id="geoip-text")

            yield Static(_("Sources à clé"), classes="omega-subtitle")
            yield Static("", id="sources-text")

            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Voir l'historique complet"), id="open-history", variant="primary")
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Retour"), id="back")
        yield Footer()

    def on_mount(self) -> None:
        targets = list_targets(target_repository=self._container.target_repository)
        targets_by_id = {t.id: t for t in targets}
        runs = list_track_runs(track_run_repository=self._container.track_run_repository)

        self._refresh_targets(targets)
        self._refresh_last_activity(runs, targets_by_id)
        self._refresh_status_breakdown(runs)
        self._refresh_module_reliability(runs)
        self._refresh_findings_typology(runs)
        self._refresh_geoip()
        self._refresh_sources()

    def _refresh_targets(self, targets: list[Target]) -> None:
        pinned_count = sum(1 for t in targets if t.pinned)
        ip_count = sum(1 for t in targets if t.kind == TargetKind.IP)
        domain_count = len(targets) - ip_count
        never_scanned = sum(1 for t in targets if t.last_track_at is None)
        self.query_one("#targets-text", Static).update(
            _("{count} cible(s) enregistrée(s) ({ip_count} IP, {domain_count} domaine(s)), "
              "{pinned_count} épinglée(s) (autorisées durablement)\n{never_scanned} cible(s) "
              "jamais observée(s)").format(count=len(targets), ip_count=ip_count, domain_count=domain_count, pinned_count=pinned_count, never_scanned=never_scanned)
        )

    def _refresh_last_activity(self, runs: list[TrackRun], targets_by_id: dict[TargetId, Target]) -> None:
        if not runs:
            self.query_one("#last-activity-text", Static).update(_("Aucune observation pour le moment."))
            return
        last = runs[0]
        target = targets_by_id.get(last.target_id)
        target_label = (target.alias or str(target.value)) if target else str(last.target_id)
        color = _STATUS_COLOR.get(last.status, "white")
        when = last.completed_at or last.started_at or last.created_at
        self.query_one("#last-activity-text", Static).update(
            f"{target_label} — {when:%Y-%m-%d %H:%M} — [{color}]{last.status.value}[/{color}]"
        )

    def _refresh_status_breakdown(self, runs: list[TrackRun]) -> None:
        counts = {status: 0 for status in TrackStatus}
        for run in runs:
            counts[run.status] += 1
        maximum = max(counts.values(), default=0)
        lines = []
        for status, count in counts.items():
            if not count:
                continue
            color = _STATUS_COLOR.get(status, "white")
            lines.append(f"[{color}]{status.value:<10}[/{color}] {count:>4}  {_bar(count, maximum)}")
        text = "\n".join(lines) if lines else _("(aucune observation)")
        self.query_one("#status-breakdown-text", Static).update(_("{count} observation(s) au "
                                                                  "total\n{text}").format(count=len(runs), text=text))

    def _refresh_module_reliability(self, runs: list[TrackRun]) -> None:
        per_module: dict[str, Counter[ModuleStatus]] = {name: Counter() for name in sorted(KNOWN_MODULES)}
        for run in runs:
            for module_name, module_run in run.module_runs.items():
                per_module.setdefault(module_name, Counter())[module_run.status] += 1

        lines = []
        for module_name in sorted(per_module):
            tally = per_module[module_name]
            attempted = tally[ModuleStatus.COMPLETED] + tally[ModuleStatus.PARTIAL] + tally[ModuleStatus.FAILED]
            if attempted == 0:
                lines.append(_("{module_name:<24} jamais exécuté").format(module_name=module_name))
                continue
            success = tally[ModuleStatus.COMPLETED] + tally[ModuleStatus.PARTIAL]
            rate = round(100 * success / attempted)
            color = "green" if rate >= 80 else "yellow" if rate >= 50 else "red"
            lines.append(_("{module_name:<24} [{color}]{rate:>3}%[/{color}] de succès  "
                           "({attempted} tentative(s))").format(module_name=module_name, color=color, rate=rate, attempted=attempted))
        self.query_one("#module-reliability-text", Static).update("\n".join(lines))

    def _refresh_findings_typology(self, runs: list[TrackRun]) -> None:
        finished = [r for r in runs if r.status not in (TrackStatus.QUEUED, TrackStatus.RUNNING)]
        sample = finished[:_FINDINGS_SAMPLE_SIZE]
        prefix_counts: Counter[str] = Counter()
        for run in sample:
            findings = self._container.finding_repository.list_findings_for_run(run.id)
            for finding in findings:
                prefix_counts[finding.finding_type.split(".", 1)[0]] += 1

        if not prefix_counts:
            self.query_one("#findings-typology-text", Static).update(
                _("(aucun finding sur les observations récentes)")
            )
            return
        maximum = max(prefix_counts.values())
        lines = [f"{prefix:<12} {count:>4}  {_bar(count, maximum)}" for prefix, count in prefix_counts.most_common()]
        self.query_one("#findings-typology-text", Static).update(
            _("sur les {count} observation(s) terminée(s) les plus récentes\n").format(count=len(sample)) + "\n".join(lines)
        )

    def _refresh_geoip(self) -> None:
        provider = resolve_active_geoip_provider(self._container.settings_repository.get("geoip_provider"))
        geoip_view = get_geoip_database_status(
            geoip_database_repository=self._container.geoip_database_repository,
            provider=provider,
            now=self._container.clock,
        )
        geoip_text = _("absente") if geoip_view.status is None else geoip_view.status.status
        self.query_one("#geoip-text", Static).update(_("fournisseur actif : {provider} — base "
                                                       ": {geoip_text}").format(provider=provider, geoip_text=geoip_text))

    def _refresh_sources(self) -> None:
        lines = []
        for source_name in list_known_reputation_sources():
            status = get_source_status(
                secret_store=self._container.secret_store,
                settings_repository=self._container.settings_repository,
                source_name=source_name,
                now=self._container.clock,
            )
            if not status.key_configured:
                lines.append(_("{source_name:<12} [grey62]absente[/grey62]").format(source_name=source_name))
            elif status.in_backoff:
                until = f"{status.backoff_until:%H:%M}" if status.backoff_until else "?"
                lines.append(_("{source_name:<12} [yellow]en pause (quota) jusqu'à "
                               "{until}[/yellow]").format(source_name=source_name, until=until))
            else:
                lines.append(_("{source_name:<12} [green]configurée[/green]").format(source_name=source_name))
        self.query_one("#sources-text", Static).update("\n".join(lines))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()
            return
        if event.button.id == "open-history":
            self.app.push_screen(HistoryScreen(container=self._container))
