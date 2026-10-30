# Copyright (c) 2026 kraynux - Licence MIT
"""Ecran Tracker : formulaire de lancement d'une observation (plan de dev
§9 `track run`). Adapte du patron screens/scan_setup.py d'omega-check
(D-007/D-008) : validation imperative au bouton "Lancer", pas de
framework de validation.

Pas d'ecran "options NeoTrace" separe (protocole/timeout/hops/MTR) : la
liste des "Commandes minimales" du plan de dev §9 (`track run
<target-id> [--profile] [--module] [--tag] [--authorize]`) n'expose
aucun de ces reglages a la CLI (Phase 9) - le profil ad-hoc construit par
start_track.py utilise toujours NeoTraceOptions/ExecutionLimits par
defaut (domain/entities/track_profile.py). Ajouter un formulaire TUI pour
des options qu'aucun use case ne consomme serait une fonctionnalite
inventee dans la couche presentation, jamais fait ailleurs cette session -
la TUI reprend exactement la meme surface que la CLI, voir docstring de
ResultsScreen pour la meme discipline sur les onglets."""
from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Checkbox, Footer, Header, Input, Select, Static

from omega_track.application.commands.tracking.start_track import (
    DEFAULT_MVP_MODULES,
    start_track,
)
from omega_track.application.guards.authorization_guard import ensure_target_authorized
from omega_track.application.orchestrators.cancellation import CancellationToken
from omega_track.application.queries.list_targets import list_targets
from omega_track.domain.entities.track_profile import KNOWN_MODULES
from omega_track.domain.exceptions.track import TargetNotAuthorizedError
from omega_track.interfaces.tui.screens._base import OmegaScreen
from omega_track.interfaces.tui.screens.progress import ProgressScreen
from omega_track.shared.i18n import _

if TYPE_CHECKING:
    from omega_track.app.container import DependencyContainer
    from omega_track.domain.entities.target import Target
    from omega_track.domain.entities.track_run import TrackRun

_EXTENDED_MODULES = sorted(KNOWN_MODULES - DEFAULT_MVP_MODULES)


class TrackerScreen(OmegaScreen):
    """Choisir une cible enregistree, les modules a activer, puis lancer."""

    def __init__(self, *, container: DependencyContainer) -> None:
        super().__init__()
        self._container = container
        self._targets: list[Target] = []

    def compose(self) -> ComposeResult:
        self._targets = list_targets(target_repository=self._container.target_repository)

        yield Header()
        with Vertical(classes="omega-form-panel"):
            yield Static(_("LANCER UNE OBSERVATION"), classes="omega-title")

            if not self._targets:
                yield Static(
                    _("Aucune cible enregistrée - ajoutez-en une dans l'écran Cibles."),
                    classes="omega-hint",
                )
            else:
                yield Static(_("Cible"), classes="omega-subtitle")
                yield Select(
                    [(_target_label(t), str(t.id)) for t in self._targets],
                    value=str(self._targets[0].id),
                    id="target-select",
                )

                yield Static(_("Modules"), classes="omega-subtitle")
                for module in sorted(DEFAULT_MVP_MODULES):
                    yield Checkbox(module, value=True, id=f"module-{module}")
                for module in _EXTENDED_MODULES:
                    yield Checkbox(module, value=False, id=f"module-{module}")

                yield Static(_("Tags (séparés par des virgules, optionnel)"), classes="omega-subtitle")
                yield Input(placeholder=_("ex. campagne-2026"), id="tags-input")

                yield Checkbox(
                    _("Autorisation explicite pour cette observation (cible non épinglée)"),
                    value=False,
                    id="authorize-checkbox",
                    classes="omega-hidden",
                )

            # Retour utilisateur : "Retour" ne vivait QUE dans la branche
            # "des cibles existent" ci-dessus - sans aucune cible
            # enregistree, cet ecran n'offrait alors aucun moyen de
            # revenir a la souris (seul Echap fonctionnait), seul
            # endroit de toute l'interface dans ce cas. Sorti du if/else,
            # toujours affiche ; "Lancer" reste conditionne aux cibles
            # (lancer sans cible n'a jamais de sens).
            with Horizontal(classes="omega-actions"):
                if self._targets:
                    with Container(classes="omega-btn-frame"):
                        yield Button(_("Lancer"), id="launch", variant="primary")
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Retour"), id="back")
        yield Footer()

    def on_mount(self) -> None:
        if self._targets:
            self._update_authorize_visibility(str(self._targets[0].id))

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "target-select":
            self._update_authorize_visibility(str(event.value))

    def _update_authorize_visibility(self, target_id: str) -> None:
        target = next((t for t in self._targets if str(t.id) == target_id), None)
        needs_authorization = target is not None and not target.pinned
        self.query_one("#authorize-checkbox", Checkbox).set_class(not needs_authorization, "omega-hidden")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()
            return
        if event.button.id == "launch":
            self._launch()

    def _launch(self) -> None:
        if not self._targets:
            self.app.notify(_("Aucune cible enregistrée."), severity="warning")
            return

        target_id_raw = self.query_one("#target-select", Select).value
        if target_id_raw is None:
            self.app.notify(_("Choisissez une cible."), severity="warning")
            return
        target = next((t for t in self._targets if str(t.id) == str(target_id_raw)), None)
        if target is None:
            self.app.notify(_("Cible introuvable."), severity="error")
            return

        modules = {
            module for module in KNOWN_MODULES if self.query_one(f"#module-{module}", Checkbox).value
        }
        if not modules:
            self.app.notify(_("Activez au moins un module."), severity="warning")
            return

        tags_raw = self.query_one("#tags-input", Input).value
        tags = {tag.strip() for tag in tags_raw.split(",") if tag.strip()}
        explicit_authorization = self.query_one("#authorize-checkbox", Checkbox).value

        try:
            ensure_target_authorized(target, explicit_authorization=explicit_authorization)
        except TargetNotAuthorizedError as exc:
            self.app.notify(str(exc), severity="error")
            return

        target_id = target.id

        def _run(token: CancellationToken) -> TrackRun:
            return start_track(
                target_repository=self._container.target_repository,
                track_run_repository=self._container.track_run_repository,
                track_orchestrator=self._container.track_orchestrator,
                target_id=target_id,
                modules=modules,
                tags=tags,
                explicit_authorization=explicit_authorization,
                cancellation_token=token,
                id_factory=self._container.id_factory,
                now=self._container.clock,
            )

        self.app.push_screen(ProgressScreen(container=self._container, heading=_("Observation en cours..."), run=_run))


def _target_label(target: Target) -> str:
    marker = "* " if target.pinned else ""
    alias = f" ({target.alias})" if target.alias else ""
    return f"{marker}{target.value}{alias}"
