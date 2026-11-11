# Copyright (c) 2026 kraynux - Licence MIT
"""Ecran d'accueil : menu principal vers les autres ecrans. Adapte du
patron screens/home.py d'omega-check (D-007/D-008) - menu propre a
TRACK (Cibles/Tracker/Historique/GeoIP en plus, pas de Profils)."""
from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar

from textual.app import ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Center, Container, Vertical
from textual.screen import Screen
from textual.widgets import Button, Footer, Header

from omega_track.interfaces.tui.screens.dashboard import DashboardScreen
from omega_track.interfaces.tui.screens.geoip_configuration import GeoIpConfigurationScreen
from omega_track.interfaces.tui.screens.help_screen import HelpScreen
from omega_track.interfaces.tui.screens.history import HistoryScreen
from omega_track.interfaces.tui.screens.quit_confirm import QuitConfirmScreen
from omega_track.interfaces.tui.screens.settings_screen import SettingsScreen
from omega_track.interfaces.tui.screens.source_configuration import SourceConfigurationScreen
from omega_track.interfaces.tui.screens.targets import TargetsScreen
from omega_track.interfaces.tui.screens.tracker import TrackerScreen
from omega_track.interfaces.tui.widgets.home_wordmark import HomeWordmark
from omega_track.shared.i18n import _

if TYPE_CHECKING:
    from omega_track.app.container import DependencyContainer

_MENU_ITEMS: tuple[tuple[str, str], ...] = (
    ("dashboard", _("Dashboard")),
    ("targets", _("Cibles")),
    ("tracker", _("Tracker")),
    ("history", _("Historique")),
    ("geoip", "GeoIP"),
    ("sources", _("Sources à clé")),
    ("settings", _("Réglages")),
    ("help", _("Aide")),
    ("quit", _("Quitter")),
)
"""Quitter avait ete retire du menu (hauteur excessive, retour
utilisateur initial) au profit du seul raccourci clavier `q` - retabli
ici (retour utilisateur ulterieur, dans le contexte d'omega-suite : sans
bouton visible, "q" pouvait etre confondu avec le raccourci global de
la suite qui ferme TOUTE la suite, pas seulement cet onglet - un bouton
explicite lisible dans le menu evite l'ambiguite, meme convention que
les 6 autres outils). `on_button_pressed`/`action_back` geraient deja
"quit" via `_quit_if_confirmed` - seule l'entree de menu manquait."""


class HomeScreen(Screen[None]):
    """Menu principal, racine de la pile de navigation. N'herite pas de
    OmegaScreen : `echap` ici demande confirmation de sortie, pas un
    dismiss() (rien "en dessous" de cet ecran)."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("escape", "back", _("Retour"), show=True),
        Binding("up", "focus_previous_item", _("Monter"), show=False),
        Binding("down", "focus_next_item", _("Descendre"), show=False),
    ]

    def __init__(self, *, container: DependencyContainer) -> None:
        super().__init__()
        self._container = container

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="omega-home-root"):
            with Center():
                yield HomeWordmark()
            with Center():
                with Vertical(classes="omega-home-menu") as menu:
                    for item_id, label in _MENU_ITEMS:
                        with Container(classes="omega-btn-frame"):
                            yield Button(label.upper(), id=item_id)
                menu.border_title = _("MENU PRINCIPAL")
        yield Footer()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "help":
            self.app.push_screen(HelpScreen(container=self._container))
            return
        if event.button.id == "quit":
            self.app.push_screen(QuitConfirmScreen(), self._quit_if_confirmed)
            return
        screen = self._screen_for(event.button.id)
        if screen is not None:
            self.app.push_screen(screen)

    def action_back(self) -> None:
        self.app.push_screen(QuitConfirmScreen(), self._quit_if_confirmed)

    def action_focus_previous_item(self) -> None:
        self.focus_previous()

    def action_focus_next_item(self) -> None:
        self.focus_next()

    def _quit_if_confirmed(self, confirmed: bool | None) -> None:
        if confirmed:
            self.app.exit()

    def _screen_for(self, item_id: str | None) -> Screen[None] | None:
        if item_id == "dashboard":
            return DashboardScreen(container=self._container)
        if item_id == "targets":
            return TargetsScreen(container=self._container)
        if item_id == "tracker":
            return TrackerScreen(container=self._container)
        if item_id == "history":
            return HistoryScreen(container=self._container)
        if item_id == "geoip":
            return GeoIpConfigurationScreen(container=self._container)
        if item_id == "sources":
            return SourceConfigurationScreen(container=self._container)
        if item_id == "settings":
            return SettingsScreen(container=self._container)
        return None
