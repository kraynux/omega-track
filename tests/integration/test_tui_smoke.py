# Copyright (c) 2026 kraynux - Licence MIT
"""Smoke test Phase 11 : demarrage complet (splash -> avertissement
terminal eventuel -> accueil), cycle de theme, sortie avec confirmation.
Assertions structurelles (Pilot), jamais de capture d'ecran - deja
documente ailleurs dans la suite comme peu fiable pour ce type d'interface."""
from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from textual.pilot import Pilot
from textual.widgets import Button, Static

from omega_track.app.bootstrap import bootstrap
from omega_track.app.container import DependencyContainer
from omega_track.interfaces.tui.app import OmegaTrackApp
from omega_track.interfaces.tui.screens.help_screen import HelpScreen
from omega_track.interfaces.tui.screens.home import HomeScreen
from omega_track.interfaces.tui.screens.terminal_warning import TerminalWarningScreen
from omega_track.interfaces.tui.widgets.home_wordmark import HomeWordmark


@pytest.fixture
def container(tmp_path: Path) -> Iterator[DependencyContainer]:
    c = bootstrap(var_dir=tmp_path, console_logging=False)
    yield c
    c.close()


async def _reach_home(pilot: Pilot[None]) -> None:
    """Ferme le splash (n'importe quelle touche), puis franchit
    l'avertissement terminal s'il apparait (profil MONO ou terminal trop
    petit - depend de l'environnement reel d'execution des tests)."""
    await pilot.press("x")
    await pilot.pause()
    if isinstance(pilot.app.screen, TerminalWarningScreen):
        await pilot.click("#continue")
        await pilot.pause()
    assert isinstance(pilot.app.screen, HomeScreen)


async def test_app_reaches_home_after_splash(container: DependencyContainer) -> None:
    app = OmegaTrackApp(container)
    async with app.run_test() as pilot:
        await _reach_home(pilot)


async def test_quit_requires_confirmation(container: DependencyContainer) -> None:
    app = OmegaTrackApp(container)
    async with app.run_test() as pilot:
        await _reach_home(pilot)
        await pilot.press("q")
        await pilot.pause()
        assert app.is_running
        await pilot.click("#confirm")
    assert not app.is_running


async def test_theme_cycle_key_changes_theme(container: DependencyContainer) -> None:
    app = OmegaTrackApp(container)
    async with app.run_test() as pilot:
        await _reach_home(pilot)
        initial_theme = app.theme
        await pilot.press("t")
        await pilot.pause()
        assert app.theme != initial_theme


async def test_home_menu_has_no_help_or_quit_button(container: DependencyContainer) -> None:
    """Regression Phase 12 : Aide/Quitter retires du menu (hauteur
    excessive signalee) - restent accessibles via les raccourcis `a`/`q`
    du Footer (BINDINGS de app.py), jamais retires de l'app elle-meme."""
    app = OmegaTrackApp(container)
    async with app.run_test() as pilot:
        await _reach_home(pilot)
        button_ids = {b.id for b in pilot.app.screen.query(Button)}
        assert "help" not in button_ids
        assert "quit" not in button_ids

        pilot.app.screen.query_one(HomeWordmark)
        await pilot.press("a")
        await pilot.pause()
        assert not isinstance(pilot.app.screen, HomeScreen)


async def test_help_screen_explains_how_to_obtain_geoip_and_keyed_sources(
    container: DependencyContainer,
) -> None:
    """Regression Phase 12 : "rajouter un petit laius dans l'aide... pour
    un utilisateur novice" - MaxMind/VirusTotal/HIBP doivent chacun avoir
    des instructions concretes (ou et comment obtenir une cle), pas
    seulement leur nom."""
    app = OmegaTrackApp(container)
    async with app.run_test() as pilot:
        await _reach_home(pilot)
        await pilot.press("a")
        await pilot.pause()
        assert isinstance(pilot.app.screen, HelpScreen)

        text = " ".join(str(s.content) for s in pilot.app.screen.query(Static))
        assert "maxmind.com" in text
        assert "virustotal.com" in text
        assert "haveibeenpwned.com" in text
        assert "PAYANT" in text


async def test_help_screen_explains_module_failed_status(container: DependencyContainer) -> None:
    """Regression Phase 12 : "besoin d'explication sur le module rdap...
    en echec... aucune reponse en face, mais qu'il charge pas" - l'aide
    doit clarifier que "en echec" n'est jamais un blocage/chargement
    indefini de l'application."""
    app = OmegaTrackApp(container)
    async with app.run_test() as pilot:
        await _reach_home(pilot)
        await pilot.press("a")
        await pilot.pause()

        text = " ".join(str(s.content) for s in pilot.app.screen.query(Static))
        assert "en echec" in text.lower() or "En echec" in text
        assert "bloqu" in text.lower()
