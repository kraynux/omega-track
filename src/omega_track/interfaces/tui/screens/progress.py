# Copyright (c) 2026 kraynux - Licence MIT
"""Ecran de progression : lance un TrackRun (start_track/replay_track,
fournis en closure par l'ecran appelant) dans un worker, sans bloquer
l'UI. Adapte du patron screens/scan_progress.py d'omega-check
(D-007/D-008), etendu d'un bouton Annuler : TrackOrchestrator (Phase 7)
accepte un CancellationToken cooperatif verifie entre phases (jamais
preemptif), CHECK n'a pas cet equivalent (ses scans sont trop courts
pour le justifier).

`run` est fourni par l'ecran appelant (tracker.py pour un lancement,
history.py pour un rejeu) plutot que d'etre code en dur ici : cet ecran
ne sait pas s'il execute `start_track` ou `replay_track`, seulement
qu'il doit executer un `Callable[[CancellationToken], TrackRun]` dans un
thread et relayer les lignes de journal - meme separation que
l'orchestrateur lui-meme (Phase 7), qui ignore aussi quel use case l'a
invoque."""
from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Center, Container, Horizontal, Middle
from textual.screen import Screen
from textual.widgets import Button

from omega_track.application.orchestrators.cancellation import CancellationToken
from omega_track.core.constants import LOGGER_NAME
from omega_track.domain.value_objects.statuses import TrackStatus
from omega_track.interfaces.tui.screens.results import ResultsScreen
from omega_track.interfaces.tui.widgets.progress_panel import ProgressPanel
from omega_track.shared.i18n import _, log_message

if TYPE_CHECKING:
    from omega_track.app.container import DependencyContainer
    from omega_track.domain.entities.track_run import TrackRun


class _RelayHandler(logging.Handler):
    """Relaie chaque record du logger applicatif vers un callback - pas de
    formattage, juste le message."""

    def __init__(self, callback: Callable[[str], None]) -> None:
        super().__init__()
        self._callback = callback

    def emit(self, record: logging.LogRecord) -> None:
        # Plan i18n R2 : le fichier journal reste en francais, l'ecran retraduit la ligne.
        self._callback(log_message(record.msg, record.args))


class ProgressScreen(Screen[None]):
    """Ecran transitoire : disparait des que l'observation se termine
    (succes/partiel/echec -> ResultsScreen remplace cet ecran ; annule ->
    retour a l'ecran d'origine)."""

    def __init__(
        self, *, container: DependencyContainer, heading: str, run: Callable[[CancellationToken], TrackRun]
    ) -> None:
        super().__init__()
        self._container = container
        self._heading = heading
        self._run = run
        self._token = CancellationToken()
        self._cancel_requested = False

    def compose(self) -> ComposeResult:
        # Panneau et bouton dans un seul Middle() : le bouton reste juste
        # sous le journal de progression, centre, au lieu d'etre pousse
        # tout en bas de l'ecran (bug signale par l'utilisateur - voir
        # aussi ".omega-progress-panel" dans base.tcss, height: auto).
        # Le Horizontal garde la classe "omega-actions" (memes regles CSS
        # que tous les autres boutons de l'appli, ex. geoip_configuration.
        # py/settings_screen.py) - le simple Container precedent en etait
        # depourvu et retombait sur le style Textual generique par
        # defaut (retour utilisateur : "tu m'as remis le design par
        # defaut"), le Center() ici ne fait QUE centrer le groupe.
        with Middle():
            yield ProgressPanel(message=self._heading)
            with Center(), Horizontal(classes="omega-actions"), Container(classes="omega-btn-frame"):
                yield Button(_("Annuler"), id="cancel", variant="error")

    def on_mount(self) -> None:
        self.run_worker(self._run_track(), exclusive=True)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel" and not self._cancel_requested:
            self._cancel_requested = True
            self._token.cancel()
            self.query_one("#cancel", Button).disabled = True
            self.app.notify(_("Annulation demandée - en attente de la fin de la phase en cours."))

    async def _run_track(self) -> None:
        logger = logging.getLogger(LOGGER_NAME)
        handler = _RelayHandler(self._on_log_record)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)

        try:
            track_run = await asyncio.to_thread(self._run, self._token)
        except Exception as exc:  # noqa: BLE001
            # Filet de securite : une exception non prevue ici (ex. un
            # module optionnel qui plante pour une raison imprevue) ne
            # doit JAMAIS laisser cet ecran fige indefiniment (bug reel
            # signale par l'utilisateur : spinner tournant sans fin,
            # obligeant a quitter l'application) - toujours notifier et
            # revenir a l'ecran precedent, jamais rester bloque ici.
            self.app.notify(str(exc) or type(exc).__name__, title=_("Observation échouée"), severity="error", timeout=10)
            self.dismiss()
            return
        finally:
            logger.removeHandler(handler)

        if track_run.status == TrackStatus.CANCELLED:
            self.app.notify(_("Observation annulée."), title=_("Annulé"))
            self.dismiss()
            return

        self.app.switch_screen(ResultsScreen(container=self._container, track_run_id=track_run.id))

    def _on_log_record(self, message: str) -> None:
        self.app.call_from_thread(self._write_log_line, message)

    def _write_log_line(self, message: str) -> None:
        if self.is_mounted:
            self.query_one(ProgressPanel).write_line(message)
