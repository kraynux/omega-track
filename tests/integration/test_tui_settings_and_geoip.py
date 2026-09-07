# Copyright (c) 2026 kraynux - Licence MIT
"""Ecrans Reglages/GeoIP/Dashboard (Phase 11) - conteneur reel
(`bootstrap()`), aucun collecteur reseau exerce par ces ecrans (GeoIP
n'appelle le telechargement reel que sur clic explicite, jamais teste
ici - meme discipline que Phase 5 : le vrai telechargement est teste par
tests/integration/test_geoip_database_updater.py, pas ici)."""
from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path

import pytest
from textual.pilot import Pilot
from textual.widgets import Button, Input, Select, Static

from omega_track.app.bootstrap import bootstrap
from omega_track.app.container import DependencyContainer
from omega_track.application.exceptions import MaxMindCredentialsMissingError
from omega_track.domain.entities.geoip_database_status import GeoIpDatabaseStatus
from omega_track.interfaces.tui.app import OmegaTrackApp
from omega_track.interfaces.tui.screens.dashboard import DashboardScreen
from omega_track.interfaces.tui.screens.geoip_configuration import GeoIpConfigurationScreen
from omega_track.interfaces.tui.screens.settings_screen import SettingsScreen
from omega_track.interfaces.tui.screens.terminal_warning import TerminalWarningScreen

_NOW = datetime(2026, 9, 7, tzinfo=timezone.utc)


class _FakeDatabaseUpdater:
    """Reussit toujours instantanement - pas de vrai reseau. Le vrai
    telechargement (Phase 5) est teste par test_geoip_database_updater.py,
    pas ici : cet ecran teste seulement que la mise a jour passe par un
    worker (Phase 12, bug signale : l'appel synchrone gelait l'interface)."""

    def download_latest(self, provider: str, destination: Path) -> GeoIpDatabaseStatus:
        return GeoIpDatabaseStatus(
            provider=provider, edition="City Lite", local_path=str(destination),
            checksum="abc123", downloaded_at=_NOW, published_at=None, status="ok",
        )


class _FakeDatabaseUpdaterMissingMaxMindKey:
    """Regression Phase 12 : `MaxMindCredentialsMissingError` n'etait
    rattrapee nulle part dans l'ecran - remontait comme "Erreur
    inattendue" generique au lieu d'un message actionnable."""

    def download_latest(self, provider: str, destination: Path) -> GeoIpDatabaseStatus:
        raise MaxMindCredentialsMissingError()


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


async def test_dashboard_shows_summary_with_no_data(container: DependencyContainer) -> None:
    app = OmegaTrackApp(container)
    async with app.run_test(size=(120, 40)) as pilot:
        await _reach_home(pilot)
        pilot.app.screen.query_one("#dashboard", Button).press()
        await pilot.pause()
        assert isinstance(pilot.app.screen, DashboardScreen)
        assert "0 cible" in str(pilot.app.screen.query_one("#targets-text", Static).content)
        assert "0 observation" in str(pilot.app.screen.query_one("#status-breakdown-text", Static).content)
        assert "hibp" in str(pilot.app.screen.query_one("#sources-text", Static).content)


async def test_dashboard_shows_enriched_activity_reliability_and_sources(
    container: DependencyContainer,
) -> None:
    """Regression : "dashboard vraiment pauvre... mets en un maximum" -
    verifie que les sections ajoutees exploitent des donnees deja
    existantes (Target.last_track_at, ModuleRun agreges, backoff d'une
    source) plutot que du texte fige."""
    from omega_track.domain.entities.target import Target
    from omega_track.domain.entities.track_profile import TrackProfile
    from omega_track.domain.entities.track_run import ModuleRun, TrackRun
    from omega_track.domain.value_objects.collection_mode import CollectionMode
    from omega_track.domain.value_objects.identifiers import (
        ModuleRunId,
        TargetId,
        TrackProfileId,
        TrackRunId,
    )
    from omega_track.domain.value_objects.statuses import ModuleStatus, TrackStatus
    from omega_track.domain.value_objects.target_value import parse_target_value

    now = container.clock()
    target = Target(
        id=TargetId("t1"), value=parse_target_value("example.org"),
        created_at=now, updated_at=now, last_track_at=now, last_status="partial",
    )
    container.target_repository.save(target)

    profile = TrackProfile(id=TrackProfileId("p1"), name="default", modules={"dns", "rdap"}, created_at=now, updated_at=now)
    run = TrackRun(id=TrackRunId("r1"), target_id=target.id, profile_snapshot=profile, status=TrackStatus.QUEUED, created_at=now)
    run.start(now=now)
    run.module_runs["rdap"] = ModuleRun(
        id=ModuleRunId("m1"), module_name="rdap", status=ModuleStatus.FAILED,
        collection_mode=CollectionMode.PASSIVE_PUBLIC,
    )
    run.module_runs["dns"] = ModuleRun(
        id=ModuleRunId("m2"), module_name="dns", status=ModuleStatus.COMPLETED,
        collection_mode=CollectionMode.PASSIVE_PUBLIC,
    )
    run.finish(status=TrackStatus.PARTIAL, now=now)
    container.track_run_repository.save(run)

    from omega_track.application.policies.quota_backoff import record_quota_exceeded

    container.secret_store.set_secret("virustotal_api_key", "dummy")
    record_quota_exceeded(settings_repository=container.settings_repository, source_name="virustotal", now=container.clock)

    app = OmegaTrackApp(container)
    async with app.run_test(size=(120, 45)) as pilot:
        await _reach_home(pilot)
        pilot.app.screen.query_one("#dashboard", Button).press()
        await pilot.pause()

        assert "0 cible(s) jamais observee(s)" in str(pilot.app.screen.query_one("#targets-text", Static).content)

        last_activity = str(pilot.app.screen.query_one("#last-activity-text", Static).content)
        assert "example.org" in last_activity
        assert "partial" in last_activity

        reliability = str(pilot.app.screen.query_one("#module-reliability-text", Static).content)
        assert "dns" in reliability and "100%" in reliability
        assert "rdap" in reliability and "0%" in reliability

        sources = str(pilot.app.screen.query_one("#sources-text", Static).content)
        assert "virustotal" in sources
        assert "en pause" in sources


async def test_dashboard_open_history_button_navigates_to_history(container: DependencyContainer) -> None:
    """Regression Phase 12 : "j'ai du mal a faire la difference entre le
    dashboard et l'historique" - le dashboard ne duplique plus le tableau
    detaille, un bouton direct y mene desormais."""
    from omega_track.interfaces.tui.screens.history import HistoryScreen

    app = OmegaTrackApp(container)
    async with app.run_test(size=(120, 40)) as pilot:
        await _reach_home(pilot)
        pilot.app.screen.query_one("#dashboard", Button).press()
        await pilot.pause()
        pilot.app.screen.query_one("#open-history", Button).press()
        await pilot.pause()
        assert isinstance(pilot.app.screen, HistoryScreen)


async def test_geoip_screen_shows_missing_database_by_default(container: DependencyContainer) -> None:
    app = OmegaTrackApp(container)
    async with app.run_test(size=(120, 40)) as pilot:
        await _reach_home(pilot)
        pilot.app.screen.query_one("#geoip", Button).press()
        await pilot.pause()
        assert isinstance(pilot.app.screen, GeoIpConfigurationScreen)
        assert "absente" in str(pilot.app.screen.query_one("#status-text", Static).content)

        pilot.app.screen.query_one("#provider-select", Select).value = "maxmind"
        await pilot.pause()
        assert container.settings_repository.get("geoip_provider") == "maxmind"


async def test_geoip_update_runs_in_a_worker_and_refreshes_status(container: DependencyContainer) -> None:
    """Regression Phase 12 : `_update()` appelait `update_geoip_database`
    directement dans le handler du bouton (bloquant) - l'interface entiere
    gelait le temps du telechargement. Verifie que l'appel passe desormais
    par un worker (bouton reactive et statut rafraichi apres l'operation,
    sans jamais avoir a attendre un vrai reseau)."""
    container.database_updater = _FakeDatabaseUpdater()

    app = OmegaTrackApp(container)
    async with app.run_test(size=(120, 40)) as pilot:
        await _reach_home(pilot)
        pilot.app.screen.query_one("#geoip", Button).press()
        await pilot.pause()

        update_button = pilot.app.screen.query_one("#update", Button)
        update_button.press()
        await pilot.pause()

        for _ in range(20):
            await pilot.pause(0.05)
            if not update_button.disabled:
                break
        assert not update_button.disabled
        assert "ok" in str(pilot.app.screen.query_one("#status-text", Static).content)


async def test_geoip_update_without_maxmind_key_notifies_instead_of_crashing(
    container: DependencyContainer,
) -> None:
    container.database_updater = _FakeDatabaseUpdaterMissingMaxMindKey()

    app = OmegaTrackApp(container)
    async with app.run_test(size=(120, 40)) as pilot:
        await _reach_home(pilot)
        pilot.app.screen.query_one("#geoip", Button).press()
        await pilot.pause()

        pilot.app.screen.query_one("#provider-select", Select).value = "maxmind"
        await pilot.pause()
        update_button = pilot.app.screen.query_one("#update", Button)
        update_button.press()

        for _ in range(20):
            await pilot.pause(0.05)
            if not update_button.disabled:
                break
        assert not update_button.disabled
        # ne plante jamais l'app : l'ecran GeoIP est toujours affiche
        assert isinstance(pilot.app.screen, GeoIpConfigurationScreen)


async def test_settings_screen_config_set_and_cleanup_preview(container: DependencyContainer) -> None:
    app = OmegaTrackApp(container)
    async with app.run_test(size=(120, 40)) as pilot:
        await _reach_home(pilot)
        pilot.app.screen.query_one("#settings", Button).press()
        await pilot.pause()
        assert isinstance(pilot.app.screen, SettingsScreen)

        pilot.app.screen.query_one("#config-key-input", Input).value = "some_key"
        pilot.app.screen.query_one("#config-value-input", Input).value = "some_value"
        pilot.app.screen.query_one("#config-set", Button).press()
        await pilot.pause()
        assert container.settings_repository.get("some_key") == "some_value"
        assert "some_key = some_value" in str(pilot.app.screen.query_one("#settings-text", Static).content)

        pilot.app.screen.query_one("#cleanup-days-input", Input).value = "9999"
        pilot.app.screen.query_one("#cleanup-preview", Button).press()
        await pilot.pause()
        assert "0 execution" in str(pilot.app.screen.query_one("#cleanup-text", Static).content)


async def test_settings_screen_has_header_footer_and_consistent_button_styling(
    container: DependencyContainer,
) -> None:
    """Regression Phase 12 : Header()/Footer() manquants sur cet ecran
    (seul de toute la TUI dans ce cas) - contribuait au symptome "on ne
    voit pas le bas du menu". Et 3 rangees de boutons (config-set,
    cleanup, fichiers locaux) etaient dans un Horizontal() sans la
    classe "omega-actions", retombant sur le style Textual par defaut
    au lieu du style de l'application (meme bug que le bouton Annuler
    du round precedent, jamais verifie ici a l'epoque)."""
    from textual.widgets import Footer as FooterWidget
    from textual.widgets import Header as HeaderWidget

    app = OmegaTrackApp(container)
    async with app.run_test(size=(120, 40)) as pilot:
        await _reach_home(pilot)
        pilot.app.screen.query_one("#settings", Button).press()
        await pilot.pause()
        assert isinstance(pilot.app.screen, SettingsScreen)

        assert pilot.app.screen.query(HeaderWidget)
        assert pilot.app.screen.query(FooterWidget)

        for button_id in ("config-set", "cleanup-preview", "cleanup-run", "clear-screenshots", "clear-exports"):
            button = pilot.app.screen.query_one(f"#{button_id}", Button)
            ancestor_classes: set[str] = set()
            node = button.parent
            while node is not None:
                ancestor_classes |= set(node.classes)
                node = node.parent
            assert "omega-actions" in ancestor_classes, f"#{button_id} n'est pas dans un .omega-actions"


async def test_clear_screenshots_and_exports_buttons_delete_files(
    container: DependencyContainer, tmp_path: Path
) -> None:
    screenshots_dir = container.default_screenshots_dir
    screenshots_dir.mkdir(parents=True, exist_ok=True)
    (screenshots_dir / "shot1.svg").write_text("x")
    exports_dir = container.default_exports_dir
    exports_dir.mkdir(parents=True, exist_ok=True)
    (exports_dir / "old_export.json").write_text("x")

    app = OmegaTrackApp(container)
    async with app.run_test(size=(120, 40)) as pilot:
        await _reach_home(pilot)
        pilot.app.screen.query_one("#settings", Button).press()
        await pilot.pause()

        pilot.app.screen.query_one("#clear-screenshots", Button).press()
        await pilot.pause()
        pilot.app.screen.query_one("#confirm", Button).press()
        await pilot.pause()
        assert list(screenshots_dir.iterdir()) == []

        pilot.app.screen.query_one("#clear-exports", Button).press()
        await pilot.pause()
        pilot.app.screen.query_one("#confirm", Button).press()
        await pilot.pause()
        assert list(exports_dir.iterdir()) == []


async def test_theme_select_applies_theme(container: DependencyContainer) -> None:
    app = OmegaTrackApp(container)
    async with app.run_test(size=(120, 40)) as pilot:
        await _reach_home(pilot)
        pilot.app.screen.query_one("#settings", Button).press()
        await pilot.pause()

        pilot.app.screen.query_one("#theme-select", Select).value = "omega-neon"
        await pilot.pause()
        assert app.theme == "omega-neon"
        assert container.settings_repository.get("theme") == "omega-neon"
