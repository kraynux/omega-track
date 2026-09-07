# Copyright (c) 2026 kraynux - Licence MIT
"""Point d'entree Textual de l'application, cable par le composition root
(app/bootstrap.py). Phase 11 : remplace le squelette de la Phase 1 -
theme/terminal (D-008), enchainement splash -> (avertissement terminal)
-> accueil, raccourcis q/ctrl+q/t/r/a."""
from __future__ import annotations

import logging
from collections.abc import Iterable
from pathlib import Path, PurePath
from typing import TYPE_CHECKING, ClassVar, cast

from omega_lib.terminal.models import RenderProfile
from omega_lib.theme.policies import TUI_THEMES
from textual.app import App, SystemCommand
from textual.binding import Binding, BindingType

from omega_track.application.commands.select_theme import select_theme
from omega_track.application.exceptions import UnknownThemeError
from omega_track.application.queries.detect_terminal import detect_terminal
from omega_track.core.constants import LOGGER_NAME
from omega_track.interfaces.tui.controllers.startup_controller import (
    StartupState,
    resolve_startup_state,
)
from omega_track.interfaces.tui.rendering.stylesheet_loader import load_paths_for
from omega_track.interfaces.tui.rendering.textual_theme_builder import build_all_textual_themes
from omega_track.interfaces.tui.screens.help_screen import HelpScreen
from omega_track.interfaces.tui.screens.history import HistoryScreen
from omega_track.interfaces.tui.screens.home import HomeScreen
from omega_track.interfaces.tui.screens.quit_confirm import QuitConfirmScreen
from omega_track.interfaces.tui.screens.splash import SplashScreen
from omega_track.interfaces.tui.screens.targets import TargetsScreen
from omega_track.interfaces.tui.screens.terminal_warning import TerminalWarningScreen
from omega_track.interfaces.tui.screens.tracker import TrackerScreen

if TYPE_CHECKING:
    from textual.screen import Screen

    from omega_track.app.container import DependencyContainer

TITLE = "\U0001f6f0 OMEGA-TRACK"


class OmegaTrackApp(App[None]):
    """Application TUI d'omega-track : resout theme/profil de rendu au
    demarrage, puis enchaine splash -> (avertissement terminal) -> accueil."""

    TITLE = TITLE
    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("q", "quit", "Quitter", show=True),
        Binding("ctrl+q", "quit", "Quitter", show=False),
        Binding("t", "cycle_theme", "Theme suivant", show=True),
        Binding("r", "refresh_terminal", "Rafraichir", show=True),
        Binding("a", "help", "Aide", show=True),
    ]

    def __init__(self, container: DependencyContainer) -> None:
        self._container = container
        self._startup_state = resolve_startup_state(
            terminal_detector=container.terminal_detector,
            settings_repository=container.settings_repository,
        )
        css_path = cast("list[str | PurePath]", load_paths_for(self._startup_state.theme.render_profile))
        super().__init__(css_path=css_path)
        for theme in build_all_textual_themes():
            self.register_theme(theme)
        self.theme = self._startup_state.theme.theme_name

    def on_mount(self) -> None:
        self.push_screen(SplashScreen(), self._after_splash)

    def _after_splash(self, _result: None) -> None:
        terminal = self._startup_state.terminal
        too_small = terminal.signals.columns < 80 or terminal.signals.rows < 24
        if terminal.render_profile == RenderProfile.MONO or too_small:
            message = (
                f"Terminal detecte : {terminal.signals.family} "
                f"({terminal.signals.columns}x{terminal.signals.rows}). "
                f"Rendu applique : {terminal.render_profile.value}."
            )
            self.push_screen(TerminalWarningScreen(message=message), self._show_home)
        else:
            self._show_home(None)

    def _show_home(self, _result: None) -> None:
        self.push_screen(HomeScreen(container=self._container))

    def watch_theme(self, _theme_name: str) -> None:
        terminal = self._startup_state.terminal
        self.sub_title = f"{self.theme} | {terminal.signals.columns}x{terminal.signals.rows}"

    async def action_quit(self) -> None:
        """Surcharge : demande confirmation avant de fermer."""
        self.push_screen(QuitConfirmScreen(), self._quit_if_confirmed)

    def _quit_if_confirmed(self, confirmed: bool | None) -> None:
        if confirmed:
            self.exit()

    def action_cycle_theme(self) -> None:
        """Touche `t` : bascule vers le theme SUIVANT du catalogue, sans
        confirmation."""
        names = list(TUI_THEMES.keys())
        current_index = names.index(self.theme) if self.theme in names else 0
        next_name = names[(current_index + 1) % len(names)]
        try:
            select_theme(settings_repository=self._container.settings_repository, theme_name=next_name)
        except UnknownThemeError as exc:
            self.notify(str(exc), severity="error")
            return
        self.theme = next_name

    def action_refresh_terminal(self) -> None:
        """Touche `r` : redetecte taille/famille du terminal et met a jour
        le sous-titre du Header."""
        terminal = detect_terminal(terminal_detector=self._container.terminal_detector)
        self._startup_state = StartupState(terminal=terminal, theme=self._startup_state.theme)
        self.sub_title = f"{self.theme} | {terminal.signals.columns}x{terminal.signals.rows}"
        self.notify(
            f"{terminal.signals.family} ({terminal.signals.columns}x{terminal.signals.rows})",
            title="Terminal rafraichi",
        )

    def action_help(self) -> None:
        self.push_screen(HelpScreen())

    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        """Remplace la liste par defaut de Textual plutot que d'appeler
        `super()` (meme raisonnement que omega-check) - expose les
        actions "non visibles" du plan de dev §11 (accessibles sans
        naviguer le menu) en plus des commandes systeme habituelles."""
        yield SystemCommand("Theme", "Changer le theme actif", self.action_change_theme)
        yield SystemCommand("Ajouter une cible", "Ouvrir l'ecran Cibles", self._open_targets)
        yield SystemCommand("Lancer une observation", "Ouvrir l'ecran Tracker", self._open_tracker)
        yield SystemCommand("Ouvrir l'historique", "Ouvrir l'ecran Historique", self._open_history)
        yield SystemCommand(
            "Capture d'ecran",
            "Enregistrer une capture SVG de l'ecran courant",
            self._deliver_screenshot_to_configured_dir,
        )
        yield SystemCommand(
            "Quitter", "Quitter l'application (avec confirmation)", self.action_quit
        )

    def _open_targets(self) -> None:
        self.push_screen(TargetsScreen(container=self._container))

    def _open_tracker(self) -> None:
        self.push_screen(TrackerScreen(container=self._container))

    def _open_history(self) -> None:
        self.push_screen(HistoryScreen(container=self._container))

    def _deliver_screenshot_to_configured_dir(self) -> None:
        """Reintroduit le menu palette "Capture d'ecran" fourni de base par
        Textual (retour utilisateur Phase 12 : absent depuis la Phase 11,
        omis faute de dossier dedie a l'epoque) - meme mecanisme que
        CHECK/omega-scan/omega-stress (D-007/D-008)."""
        directory = Path(self._container.default_screenshots_dir)
        directory.mkdir(parents=True, exist_ok=True)
        self.deliver_screenshot(path=str(directory))

    def _handle_exception(self, error: Exception) -> None:
        """Filet de securite unique cote TUI : toute exception technique
        non prevue est journalisee puis affichee comme notification,
        sans jamais fermer l'application."""
        logging.getLogger(LOGGER_NAME).error("Exception non prevue", exc_info=error)
        self.notify(
            str(error) or type(error).__name__,
            title="Erreur inattendue",
            severity="error",
            timeout=10,
        )
