# Copyright (c) 2026 kraynux - Licence MIT
"""Ecran Historique : liste des TrackRun passes (plan de dev §9 `history
list [--target] [--status] [--tag]`), avec rejeu (D-013) et export.

Pas de suppression individuelle ici : aucun use case ne supprime un seul
TrackRun par id (application/commands/maintenance/cleanup_history.py ne
purge que "plus vieux que N jours", en lot) - un bouton "Supprimer" par
ligne serait une fonctionnalite inventee dans la couche presentation,
jamais fait ailleurs cette session. La purge en lot reste accessible
depuis l'ecran Reglages (settings.py)."""
from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, DataTable, Footer, Header, Input, Select, Static

from omega_track.application.commands.exports.export_track import export_track
from omega_track.application.commands.tracking.replay_track import replay_track
from omega_track.application.guards.authorization_guard import ensure_target_authorized
from omega_track.application.orchestrators.cancellation import CancellationToken
from omega_track.application.queries.get_target import get_target
from omega_track.application.queries.list_track_runs import list_track_runs
from omega_track.core.export_theme import DEFAULT_EXPORT_THEME, EXPORT_PALETTES
from omega_track.domain.exceptions.track import TargetNotAuthorizedError
from omega_track.domain.value_objects.export_options import ExportOptions
from omega_track.domain.value_objects.identifiers import TrackRunId
from omega_track.domain.value_objects.statuses import TrackStatus
from omega_track.interfaces.tui.screens._base import OmegaScreen
from omega_track.interfaces.tui.screens.progress import ProgressScreen
from omega_track.interfaces.tui.screens.results import ResultsScreen
from omega_track.shared.i18n import LANGUAGE, _, translating_as

if TYPE_CHECKING:
    from omega_track.app.container import DependencyContainer
    from omega_track.domain.entities.track_run import TrackRun

_STATUS_CHOICES: tuple[tuple[str, str], ...] = ((_("(tous)"), ""), *((s.value, s.value) for s in TrackStatus))
_EXPORT_FORMATS: tuple[str, ...] = ("html", "json", "markdown", "csv", "dot", "mermaid")
"""HTML en tete de liste (Phase 12, retour utilisateur) - format le plus
directement consultable (theme applique, graphes Mermaid rendus), tant
comme premier choix affiche que comme valeur par defaut du Select."""


class HistoryScreen(OmegaScreen):
    """Filtrer, consulter, rejouer ou exporter une observation passee."""

    def __init__(self, *, container: DependencyContainer) -> None:
        super().__init__()
        self._container = container
        self._selected_id: str | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="omega-panel"):
            yield Static(_("HISTORIQUE"), classes="omega-title")
            with Horizontal():
                yield Select(_STATUS_CHOICES, value="", id="status-filter", classes="omega-select-compact")
                yield Input(placeholder=_("Filtrer par tag (optionnel)"), id="tag-filter")
            table: DataTable[str] = DataTable(id="runs-table")
            yield table
            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Voir le rapport"), id="show", variant="primary")
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Rejouer"), id="replay")
                with Container(classes="omega-btn-frame"):
                    yield Select(
                        [(f, f) for f in _EXPORT_FORMATS],
                        value="html", id="export-format", classes="omega-select-compact",
                    )
                with Container(classes="omega-btn-frame"):
                    yield Select(
                        [(theme, theme) for theme in sorted(EXPORT_PALETTES)],
                        value=DEFAULT_EXPORT_THEME, id="export-theme", classes="omega-select-compact",
                    )
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Exporter"), id="export")
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Retour"), id="back")
        yield Footer()

    def on_mount(self) -> None:
        table = self.query_one("#runs-table", DataTable)
        table.cursor_type = "row"
        table.add_columns(_("Run"), _("Cible"), _("Statut"), _("Lancé le"), _("Tags"))
        self._refresh()

    def _refresh(self) -> None:
        status_value = self.query_one("#status-filter", Select).value
        status = str(status_value) if status_value else None
        tag = self.query_one("#tag-filter", Input).value.strip() or None
        runs = list_track_runs(track_run_repository=self._container.track_run_repository, status=status, tag=tag)
        table = self.query_one("#runs-table", DataTable)
        table.clear()
        for run in runs:
            target = self._container.target_repository.get(run.target_id)
            target_label = str(target.value) if target is not None else str(run.target_id)
            table.add_row(
                str(run.id),
                target_label,
                run.status.value,
                run.created_at.isoformat(timespec="seconds"),
                ", ".join(sorted(run.tags)) or "-",
                key=str(run.id),
            )

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "status-filter":
            self._refresh()

    def on_input_submitted(self, event: Input.Submitted) -> None:
        if event.input.id == "tag-filter":
            self._refresh()

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self._selected_id = str(event.row_key.value)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()
            return
        if event.button.id == "show":
            self._show()
            return
        if event.button.id == "replay":
            self._replay()
            return
        if event.button.id == "export":
            self._export()

    def _show(self) -> None:
        if self._selected_id is None:
            self.app.notify(_("Sélectionnez d'abord une ligne."), severity="warning")
            return
        self.app.push_screen(ResultsScreen(container=self._container, track_run_id=TrackRunId(self._selected_id)))

    def _replay(self) -> None:
        if self._selected_id is None:
            self.app.notify(_("Sélectionnez d'abord une ligne."), severity="warning")
            return
        original_id = TrackRunId(self._selected_id)
        original = self._container.track_run_repository.get(original_id)
        if original is None:
            self.app.notify(_("Exécution introuvable."), severity="error")
            return
        target = get_target(target_repository=self._container.target_repository, target_id=original.target_id)
        try:
            ensure_target_authorized(target, explicit_authorization=False)
        except TargetNotAuthorizedError as exc:
            self.app.notify(str(exc), severity="error")
            return

        def _run(token: CancellationToken) -> TrackRun:
            return replay_track(
                target_repository=self._container.target_repository,
                track_run_repository=self._container.track_run_repository,
                track_orchestrator=self._container.track_orchestrator,
                original_track_run_id=original_id,
                explicit_authorization=False,
                cancellation_token=token,
                id_factory=self._container.id_factory,
                now=self._container.clock,
            )

        self.app.push_screen(ProgressScreen(container=self._container, heading=_("Rejeu en cours..."), run=_run))

    def _export(self) -> None:
        if self._selected_id is None:
            self.app.notify(_("Sélectionnez d'abord une ligne."), severity="warning")
            return
        export_format = str(self.query_one("#export-format", Select).value)
        export_theme = str(self.query_one("#export-theme", Select).value)
        # Lot N (Q5) : rapport ecrit dans la langue des exports (reglage ; dans la suite, le sien).
        with translating_as(LANGUAGE.export_state(self._container.settings_repository)):
            artifact = export_track(
                export_orchestrator=self._container.export_orchestrator,
                track_run_id=TrackRunId(self._selected_id),
                export_format=export_format,
                output_dir=self._container.default_exports_dir,
                options=ExportOptions(export_theme=export_theme),
            )
        self.app.notify(_("Exporté vers {name}").format(name=Path(artifact.output_path).name), title=_("Export terminé"))
