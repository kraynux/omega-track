# Copyright (c) 2026 kraynux - Licence MIT
"""Ecran Sources a cle (Phase 12) - conteneur reel (`bootstrap()`),
aucun collecteur reseau exerce par cet ecran (configurer/retirer une cle
ne declenche jamais d'appel reseau, meme discipline que
test_tui_settings_and_geoip.py::test_geoip_screen... pour GeoIP)."""
from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from textual.pilot import Pilot
from textual.widgets import Button, Input, Select, Static

from omega_track.app.bootstrap import bootstrap
from omega_track.app.container import DependencyContainer
from omega_track.interfaces.tui.app import OmegaTrackApp
from omega_track.interfaces.tui.screens.source_configuration import SourceConfigurationScreen
from omega_track.interfaces.tui.screens.terminal_warning import TerminalWarningScreen


@pytest.fixture
def container(tmp_path: Path) -> Iterator[DependencyContainer]:
    c = bootstrap(var_dir=tmp_path, console_logging=False)
    yield c
    c.close()


async def _reach_home(pilot: Pilot[None]) -> None:
    await pilot.press("x")
    await pilot.pause()
    if isinstance(pilot.app.screen, TerminalWarningScreen):
        pilot.app.screen.query_one("#continue", Button).press()
        await pilot.pause()


async def test_source_screen_shows_disclosure_before_any_key_is_entered(
    container: DependencyContainer,
) -> None:
    app = OmegaTrackApp(container)
    async with app.run_test(size=(120, 40)) as pilot:
        await _reach_home(pilot)
        pilot.app.screen.query_one("#sources", Button).press()
        await pilot.pause()
        assert isinstance(pilot.app.screen, SourceConfigurationScreen)

        disclosure = str(pilot.app.screen.query_one("#disclosure-text", Static).content)
        assert "Quota" in disclosure
        assert "Donnees envoyees" in disclosure
        status = str(pilot.app.screen.query_one("#status-text", Static).content)
        assert "absente" in status


async def test_hibp_disclosure_flags_paid_source(container: DependencyContainer) -> None:
    app = OmegaTrackApp(container)
    async with app.run_test(size=(120, 40)) as pilot:
        await _reach_home(pilot)
        pilot.app.screen.query_one("#sources", Button).press()
        await pilot.pause()

        pilot.app.screen.query_one("#source-select", Select).value = "hibp"
        await pilot.pause()
        disclosure = str(pilot.app.screen.query_one("#disclosure-text", Static).content)
        assert "PAYANTE" in disclosure


async def test_save_and_clear_key_round_trip(container: DependencyContainer) -> None:
    app = OmegaTrackApp(container)
    async with app.run_test(size=(120, 40)) as pilot:
        await _reach_home(pilot)
        pilot.app.screen.query_one("#sources", Button).press()
        await pilot.pause()

        pilot.app.screen.query_one("#source-select", Select).value = "virustotal"
        await pilot.pause()
        pilot.app.screen.query_one("#key-input", Input).value = "cle-de-test"
        pilot.app.screen.query_one("#save-key", Button).press()
        await pilot.pause()

        assert container.secret_store.get_secret("virustotal_api_key") == "cle-de-test"
        status = str(pilot.app.screen.query_one("#status-text", Static).content)
        assert "configuree" in status

        pilot.app.screen.query_one("#clear-key", Button).press()
        await pilot.pause()
        assert container.secret_store.get_secret("virustotal_api_key") is None
        status = str(pilot.app.screen.query_one("#status-text", Static).content)
        assert "absente" in status


async def test_save_key_rejects_empty_input(container: DependencyContainer) -> None:
    app = OmegaTrackApp(container)
    async with app.run_test(size=(120, 40)) as pilot:
        await _reach_home(pilot)
        pilot.app.screen.query_one("#sources", Button).press()
        await pilot.pause()

        pilot.app.screen.query_one("#save-key", Button).press()
        await pilot.pause()
        assert container.secret_store.get_secret("virustotal_api_key") is None
