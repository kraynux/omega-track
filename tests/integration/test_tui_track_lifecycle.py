# Copyright (c) 2026 kraynux - Licence MIT
"""Cycle de vie complet via la TUI reelle (Phase 11) : accueil -> Cibles
(ajouter + epingler) -> Tracker (lancer) -> Progression -> Resultats,
puis Historique (voir le rapport + rejouer). Meme technique que
tests/integration/test_cli_track_lifecycle.py (Phase 9) : conteneur reel
(`bootstrap()`, vraie base SQLite) a l'exception des collecteurs reseau,
remplaces par des fakes et le TrackOrchestrator reconstruit avec eux
(capture ses dependances a la construction, Phase 7) - seule facon de
tester le cycle complet sans reseau reel (D-014).

Interactions par methode directe (`Button.press()`, `Checkbox.toggle()`,
assignation `.value`, `.focus()` + touche "entree") plutot que par clic
aux coordonnees (`pilot.click`) : plusieurs boutons de ces ecrans
(rangees d'actions a 4-5 boutons) tombent hors de la region visible
selon la taille du terminal virtuel de test, ce qui rend le clic par
coordonnees fragile - la methode directe teste le meme comportement
(le message `Button.Pressed` reellement envoye) sans dependre du rendu
a l'ecran."""
from __future__ import annotations

from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path

import pytest
from textual.pilot import Pilot
from textual.widgets import Button, Checkbox, DataTable, Input, Select

from omega_track.app.bootstrap import bootstrap
from omega_track.app.container import DependencyContainer
from omega_track.application.orchestrators.track_orchestrator import TrackOrchestrator
from omega_track.core.enums import ConfidenceLevel
from omega_track.domain.entities.findings.dns import DnsFindingType
from omega_track.domain.entities.findings.path import NetworkPath
from omega_track.domain.entities.track_profile import NeoTraceOptions
from omega_track.domain.value_objects.collected_record import CollectedRecord
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.domain.value_objects.ip_address import IPAddress
from omega_track.interfaces.tui.app import OmegaTrackApp
from omega_track.interfaces.tui.screens.history import HistoryScreen
from omega_track.interfaces.tui.screens.results import ResultsScreen
from omega_track.interfaces.tui.screens.targets import TargetsScreen
from omega_track.interfaces.tui.screens.terminal_warning import TerminalWarningScreen
from omega_track.interfaces.tui.screens.tracker import TrackerScreen
from omega_track.interfaces.tui.widgets.targets_table import TargetsTable

_NOW = datetime(2026, 9, 6, tzinfo=timezone.utc)


class _FakeDnsCollector:
    def resolve(self, domain: DomainName) -> list[CollectedRecord]:
        return [
            CollectedRecord(
                finding_type=DnsFindingType.A_RECORD.value,
                payload={"address": "93.184.216.34"},
                confidence=ConfidenceLevel.VERIFIED,
                source_name="dns",
                observed_at=_NOW,
            )
        ]

    def reverse_lookup(self, ip: IPAddress) -> CollectedRecord | None:
        return None


class _FakeRdapCollector:
    def collect_domain_registration(self, domain: DomainName) -> list[CollectedRecord]:
        return []

    def collect_ip_registration(self, ip: IPAddress) -> list[CollectedRecord]:
        return []


class _FakeTracerouteCollector:
    def is_available(self) -> bool:
        return False

    def trace(self, target_ip: IPAddress, options: NeoTraceOptions) -> NetworkPath:
        raise AssertionError("non exerce (is_available=False)")


@pytest.fixture
def container(tmp_path: Path) -> Iterator[DependencyContainer]:
    c = bootstrap(var_dir=tmp_path, console_logging=False)
    c.dns_collector = _FakeDnsCollector()
    c.rdap_collector = _FakeRdapCollector()
    c.traceroute_collector = _FakeTracerouteCollector()
    c.track_orchestrator = TrackOrchestrator(
        dns_collector=c.dns_collector,
        rdap_collector=c.rdap_collector,
        traceroute_collector=c.traceroute_collector,
        finding_repository=c.finding_repository,
        track_run_repository=c.track_run_repository,
        event_publisher=c.event_publisher,
        id_factory=c.id_factory,
        now=c.clock,
        log_correlation=c.log_correlation,
    )
    yield c
    c.close()


async def _reach_home(pilot: Pilot[None]) -> None:
    await pilot.press("x")
    await pilot.pause()
    if isinstance(pilot.app.screen, TerminalWarningScreen):
        pilot.app.screen.query_one("#continue", Button).press()
        await pilot.pause()


async def _select_first_row(pilot: Pilot[None], table_id: str) -> None:
    table = pilot.app.screen.query_one(table_id, DataTable)
    table.focus()
    table.move_cursor(row=0)
    await pilot.press("enter")
    await pilot.pause()


async def test_full_lifecycle_add_pin_track_show_replay(container: DependencyContainer) -> None:
    app = OmegaTrackApp(container)
    async with app.run_test(size=(120, 40)) as pilot:
        await _reach_home(pilot)

        pilot.app.screen.query_one("#targets", Button).press()
        await pilot.pause()
        assert isinstance(pilot.app.screen, TargetsScreen)

        pilot.app.screen.query_one("#value-input", Input).value = "example.com"
        pilot.app.screen.query_one("#add", Button).press()
        await pilot.pause()

        table = pilot.app.screen.query_one(TargetsTable)
        assert table.row_count == 1
        await _select_first_row(pilot, "#targets-table")
        pilot.app.screen.query_one("#pin", Button).press()
        await pilot.pause()
        assert table.row_count == 1

        pilot.app.screen.query_one("#back", Button).press()
        await pilot.pause()

        pilot.app.screen.query_one("#tracker", Button).press()
        await pilot.pause()
        assert isinstance(pilot.app.screen, TrackerScreen)
        for module in ("reverse_dns", "rdap", "neotrace"):
            pilot.app.screen.query_one(f"#module-{module}", Checkbox).toggle()
        pilot.app.screen.query_one("#launch", Button).press()
        await pilot.pause()

        for _ in range(20):
            await pilot.pause(0.05)
            if isinstance(pilot.app.screen, ResultsScreen):
                break
        assert isinstance(pilot.app.screen, ResultsScreen)
        assert len(pilot.app.screen._report.findings) >= 1

        # regression Phase 12 : les onglets Certificats/Archives (modules
        # etendus jamais coches par ce lancement, la toggle ci-dessus a
        # meme desactive rdap qui l'etait par defaut) doivent expliquer
        # pourquoi ils sont vides, pas rester silencieux.
        from omega_track.interfaces.tui.screens.results import _module_status_note

        cert_note = _module_status_note(pilot.app.screen._track_run, "certificate_transparency")
        assert cert_note is not None and "non activé" in cert_note
        rdap_note = _module_status_note(pilot.app.screen._track_run, "rdap")
        assert rdap_note is not None and "non activé" in rdap_note

        pilot.app.screen.query_one("#back", Button).press()
        await pilot.pause()
        assert isinstance(pilot.app.screen, TrackerScreen)
        pilot.app.screen.query_one("#back", Button).press()
        await pilot.pause()

        pilot.app.screen.query_one("#history", Button).press()
        await pilot.pause()
        assert isinstance(pilot.app.screen, HistoryScreen)

        runs_table = pilot.app.screen.query_one("#runs-table", DataTable)
        assert runs_table.row_count == 1

        await _select_first_row(pilot, "#runs-table")
        pilot.app.screen.query_one("#show", Button).press()
        await pilot.pause()
        assert isinstance(pilot.app.screen, ResultsScreen)


async def test_tracker_refuses_unauthorized_target(container: DependencyContainer) -> None:
    """Une cible non epinglee, sans case "autorisation explicite" cochee,
    doit refuser le lancement (D-010) - notification, pas de crash, pas
    de changement d'ecran."""
    from omega_track.application.commands.targets.create_target import create_target

    create_target(
        target_repository=container.target_repository,
        raw_value="example.org",
        id_factory=container.id_factory,
        now=container.clock,
    )

    app = OmegaTrackApp(container)
    async with app.run_test(size=(120, 40)) as pilot:
        await _reach_home(pilot)
        pilot.app.screen.query_one("#tracker", Button).press()
        await pilot.pause()
        assert isinstance(pilot.app.screen, TrackerScreen)

        assert pilot.app.screen.query_one("#authorize-checkbox", Checkbox).has_class("omega-hidden") is False
        pilot.app.screen.query_one("#launch", Button).press()
        await pilot.pause()
        assert isinstance(pilot.app.screen, TrackerScreen)


async def test_tracker_screen_offers_a_back_button_with_no_target_registered(
    container: DependencyContainer,
) -> None:
    """Regression : "Retour" ne vivait que dans la branche "des cibles
    existent" de compose() - sans aucune cible enregistree, cet ecran
    n'offrait alors aucun moyen d'en sortir a la souris (seul Echap
    fonctionnait), seul endroit de toute l'interface dans ce cas."""
    app = OmegaTrackApp(container)
    async with app.run_test(size=(120, 40)) as pilot:
        await _reach_home(pilot)
        pilot.app.screen.query_one("#tracker", Button).press()
        await pilot.pause()
        assert isinstance(pilot.app.screen, TrackerScreen)

        assert len(pilot.app.screen.query("#launch")) == 0
        pilot.app.screen.query_one("#back", Button).press()
        await pilot.pause()
        assert not isinstance(pilot.app.screen, TrackerScreen)


async def test_export_from_history_writes_a_file(container: DependencyContainer, tmp_path: Path) -> None:
    from omega_track.application.commands.targets.create_target import create_target
    from omega_track.application.commands.targets.pin_target import pin_target
    from omega_track.application.commands.tracking.start_track import start_track

    target = create_target(
        target_repository=container.target_repository,
        raw_value="example.net",
        id_factory=container.id_factory,
        now=container.clock,
    )
    pin_target(target_repository=container.target_repository, target_id=target.id, now=container.clock)
    start_track(
        target_repository=container.target_repository,
        track_run_repository=container.track_run_repository,
        track_orchestrator=container.track_orchestrator,
        target_id=target.id,
        modules={"dns"},
        id_factory=container.id_factory,
        now=container.clock,
    )

    app = OmegaTrackApp(container)
    async with app.run_test(size=(120, 40)) as pilot:
        await _reach_home(pilot)
        pilot.app.screen.query_one("#history", Button).press()
        await pilot.pause()
        await _select_first_row(pilot, "#runs-table")
        export_select = pilot.app.screen.query_one("#export-format", Select)
        assert export_select.size.width <= 30, "regression Phase 12 : le select d'export ne doit pas s'etirer"
        export_select.value = "json"
        pilot.app.screen.query_one("#export", Button).press()
        await pilot.pause()

    exported = list(container.default_exports_dir.glob("*.json"))
    assert len(exported) == 1


async def test_export_html_theme_choice_is_applied(container: DependencyContainer) -> None:
    from omega_track.application.commands.targets.create_target import create_target
    from omega_track.application.commands.targets.pin_target import pin_target
    from omega_track.application.commands.tracking.start_track import start_track

    target = create_target(
        target_repository=container.target_repository, raw_value="example.org",
        id_factory=container.id_factory, now=container.clock,
    )
    pin_target(target_repository=container.target_repository, target_id=target.id, now=container.clock)
    start_track(
        target_repository=container.target_repository, track_run_repository=container.track_run_repository,
        track_orchestrator=container.track_orchestrator, target_id=target.id, modules={"dns"},
        id_factory=container.id_factory, now=container.clock,
    )

    app = OmegaTrackApp(container)
    async with app.run_test(size=(120, 40)) as pilot:
        await _reach_home(pilot)
        pilot.app.screen.query_one("#history", Button).press()
        await pilot.pause()
        await _select_first_row(pilot, "#runs-table")
        pilot.app.screen.query_one("#export-format", Select).value = "html"
        pilot.app.screen.query_one("#export-theme", Select).value = "omega-neon"
        pilot.app.screen.query_one("#export", Button).press()
        await pilot.pause()

    exported = list(container.default_exports_dir.glob("*.html"))
    assert len(exported) == 1
    from omega_lib.theme.policies import EXPORT_PALETTES

    assert EXPORT_PALETTES["omega-neon"].accent in exported[0].read_text(encoding="utf-8")
