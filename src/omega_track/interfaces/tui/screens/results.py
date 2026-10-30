# Copyright (c) 2026 kraynux - Licence MIT
"""Ecran Resultats : rapport d'identite complet d'un TrackRun termine
(plan de dev §9 `track show`, Phase 8 IdentityReport). Onglets reels
uniquement (pas de reputation/organisation - modules a cle jamais
implementes, hors perimetre v1.0, voir domain/entities/track_profile.py::
KNOWN_MODULES) : Identite (WHOIS/RDAP), DNS, Reseau/ASN, NeoTrace,
Certificats, Archives, Relations (graphe Mermaid partage avec l'export,
voir application/orchestrators/mermaid_graph_builder.py), Diagnostics
(findings collection.* : sources indisponibles/quotas - visibilite du
D-015 "absence de champ isole n'est jamais une erreur")."""
from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import (
    Button,
    DataTable,
    Footer,
    Header,
    Static,
    TabbedContent,
    TabPane,
    TextArea,
)

from omega_track.application.orchestrators.mermaid_graph_builder import build_mermaid_graph
from omega_track.application.queries.get_identity_report import get_identity_report
from omega_track.domain.value_objects.identifiers import TrackRunId
from omega_track.domain.value_objects.statuses import ModuleStatus
from omega_track.interfaces.tui.screens._base import OmegaScreen
from omega_track.shared.i18n import _

if TYPE_CHECKING:
    from omega_track.app.container import DependencyContainer
    from omega_track.domain.entities.identity_report import IdentityReport
    from omega_track.domain.entities.track_run import ModuleRun, TrackRun


def _finding_table(report: IdentityReport, prefix: str) -> DataTable[str]:
    table: DataTable[str] = DataTable()
    table.add_columns(_("Type"), _("Valeur"), _("Confiance"), _("Source"))
    for finding in report.findings_by_type_prefix(prefix):
        payload = ", ".join(f"{k}={v}" for k, v in finding.payload.items())
        table.add_row(finding.finding_type, payload, finding.confidence.value, finding.source_name)
    return table


def _module_status_note(track_run: TrackRun | None, module_name: str) -> str | None:
    """Rappel affiche au-dessus d'un onglet lie a un module optionnel -
    None si le module a reellement produit un resultat exploitable
    (COMPLETED/PARTIAL), auquel cas le tableau parle de lui-meme -
    retour utilisateur Phase 12 ("les onglets... toujours vide, normal?")."""
    if track_run is None:
        return None
    module_run: ModuleRun | None = track_run.module_runs.get(module_name)
    if module_run is None:
        return _("Module '{module_name}' non activé dans le profil de cette observation.").format(module_name=module_name)
    if module_run.status == ModuleStatus.SKIPPED:
        return _("Module '{module_name}' non exécuté : {value}.").format(module_name=module_name, value=_(module_run.error_detail) if module_run.error_detail else _("raison non précisée"))
    if module_run.status == ModuleStatus.FAILED:
        detail = _(module_run.error_detail) if module_run.error_detail else module_run.error_code or _("raison non précisée")
        # "en echec" = la source n'a donne AUCUNE reponse exploitable
        # (timeout, erreur HTTP, reseau injoignable...) - jamais un
        # blocage/chargement indefini de l'application elle-meme :
        # l'observation entiere s'est deja terminee normalement au
        # moment ou ce message s'affiche (retour utilisateur Phase 12 :
        # demande d'explication sur ce que signifie ce statut).
        return (
            _("Module '{module_name}' en échec ({detail}) - la source n'a donné aucune réponse "
              "exploitable ; ceci ne bloque jamais le reste de l'observation, déjà terminée.").format(module_name=module_name, detail=detail)
        )
    if module_run.status == ModuleStatus.CANCELLED:
        return _("Module '{module_name}' annulé avant d'avoir terminé.").format(module_name=module_name)
    return None


class ResultsScreen(OmegaScreen):
    """Rapport complet d'une observation, deja terminee (statut terminal)."""

    def __init__(self, *, container: DependencyContainer, track_run_id: TrackRunId) -> None:
        super().__init__()
        self._container = container
        self._track_run_id = track_run_id
        self._track_run = container.track_run_repository.get(track_run_id)
        self._report = get_identity_report(
            track_run_id=track_run_id,
            track_run_repository=container.track_run_repository,
            target_repository=container.target_repository,
            finding_repository=container.finding_repository,
            now=container.clock,
        )

    def _module_note_widget(self, module_name: str) -> Static | None:
        note = _module_status_note(self._track_run, module_name)
        return Static(note, classes="omega-hint") if note else None

    def compose(self) -> ComposeResult:
        report = self._report
        yield Header()
        yield Static(
            _("Cible : {target_value}  |  Run : {track_run_id}  |  {count} finding(s), "
              "{count2} relation(s), {count3} chemin(s)").format(target_value=report.target_value, track_run_id=report.track_run_id, count=len(report.findings), count2=len(report.relations), count3=len(report.paths)),
            classes="omega-subtitle",
        )
        with TabbedContent():
            with TabPane(_("Identité"), id="tab-identity"):
                note = self._module_note_widget("rdap")
                if note is not None:
                    yield note
                yield _finding_table(report, "identity.")
            with TabPane(_("DNS"), id="tab-dns"):
                note = self._module_note_widget("dns")
                if note is not None:
                    yield note
                yield _finding_table(report, "dns.")
            with TabPane(_("Réseau / ASN"), id="tab-network"):
                note = self._module_note_widget("bgp")
                if note is not None:
                    yield note
                yield _finding_table(report, "network.")
            with TabPane("NeoTrace", id="tab-neotrace"):
                note = self._module_note_widget("neotrace")
                if note is not None:
                    yield note
                yield self._neotrace_table()
            with TabPane(_("Certificats"), id="tab-certificates"):
                note = self._module_note_widget("certificate_transparency")
                if note is not None:
                    yield note
                yield _finding_table(report, "certificate.")
            with TabPane(_("Archives"), id="tab-archives"):
                note = self._module_note_widget("archives")
                if note is not None:
                    yield note
                yield _finding_table(report, "history.")
            with TabPane(_("Relations"), id="tab-relations"):
                yield self._relations_table()
                yield Static(_("Graphe Mermaid (même source que l'export .mmd)"), classes="omega-hint")
                yield TextArea(build_mermaid_graph(report), read_only=True, id="mermaid-source")
            with TabPane(_("Diagnostics"), id="tab-diagnostics"):
                yield _finding_table(report, "collection.")
        with Horizontal(classes="omega-actions"), Container(classes="omega-btn-frame"):
            yield Button(_("Retour"), id="back")
        yield Footer()

    def _neotrace_table(self) -> VerticalScroll:
        if not self._report.paths:
            return VerticalScroll(Static(_("Aucun chemin réseau collecté.")))

        children: list[Static | DataTable[str]] = []
        for path in self._report.paths:
            table: DataTable[str] = DataTable()
            table.add_columns(_("Séquence"), _("IP"), _("Hôte"), _("RTT (ms)"), _("ASN"), _("Pays"))
            for hop in path.hops:
                table.add_row(
                    str(hop.sequence),
                    str(hop.ip) if hop.ip else "*",
                    hop.hostname or "-",
                    f"{hop.rtt_ms:.1f}" if hop.rtt_ms is not None else "-",
                    str(hop.asn.number) if hop.asn else "-",
                    (hop.geo.country if hop.geo else None) or "-",
                )
            children.append(Static(_("{target_ip} ({protocol})").format(target_ip=path.target_ip, protocol=path.protocol), classes="omega-subtitle"))
            children.append(table)
        return VerticalScroll(*children)

    def _relations_table(self) -> DataTable[str]:
        table: DataTable[str] = DataTable()
        table.add_columns(_("Source"), _("Cible"), _("Type"), _("Confiance"))
        for relation in self._report.relations:
            table.add_row(
                relation.source_entity_ref,
                relation.target_entity_ref,
                relation.relation_type.value,
                relation.confidence.value,
            )
        return table

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()
