# Copyright (c) 2026 kraynux - Licence MIT
"""Ecran Reglages : theme, profil de rendu, reglages generiques cle/valeur,
diagnostics, purge de l'historique (plan de dev §9 `config show|set`,
`diagnostics`, `cleanup preview|run`)."""
from __future__ import annotations

from datetime import timedelta
from pathlib import Path
from typing import TYPE_CHECKING

from omega_lib.terminal.models import RenderProfile
from omega_lib.theme.policies import TUI_THEMES
from textual.app import ComposeResult
from textual.containers import Container, Horizontal, VerticalScroll
from textual.widgets import Button, Footer, Header, Input, Select, Static

from omega_track.application.commands.maintenance.cleanup_history import (
    cleanup_history,
    preview_history_cleanup,
)
from omega_track.application.commands.maintenance.clear_directory import clear_directory
from omega_track.application.commands.select_render_profile import select_render_profile
from omega_track.application.commands.select_theme import select_theme
from omega_track.application.exceptions import UnknownThemeError
from omega_track.application.queries.diagnostics import run_diagnostics
from omega_track.application.queries.get_settings import get_settings
from omega_track.interfaces.tui.screens._base import OmegaScreen
from omega_track.interfaces.tui.screens.confirm import ConfirmScreen

if TYPE_CHECKING:
    from omega_track.app.container import DependencyContainer

_RENDER_PROFILE_CHOICES: tuple[tuple[str, str], ...] = (
    ("(automatique)", ""),
    *((p.value, p.value) for p in RenderProfile),
)


class SettingsScreen(OmegaScreen):
    """Theme, rendu, reglages generiques, diagnostics, purge."""

    def __init__(self, *, container: DependencyContainer) -> None:
        super().__init__()
        self._container = container

    def compose(self) -> ComposeResult:
        yield Header()
        with VerticalScroll(classes="omega-panel"):
            yield Static("REGLAGES", classes="omega-title")

            yield Static("Theme", classes="omega-subtitle")
            yield Select([(name, name) for name in TUI_THEMES], id="theme-select")

            yield Static("Profil de rendu (surcharge la detection automatique)", classes="omega-subtitle")
            yield Select(_RENDER_PROFILE_CHOICES, value="", id="render-profile-select")

            yield Static("Diagnostics", classes="omega-subtitle")
            yield Static("", id="diagnostics-text")

            yield Static("Reglages actuels", classes="omega-subtitle")
            yield Static("", id="settings-text")
            with Horizontal(classes="omega-actions"):
                yield Input(placeholder="cle", id="config-key-input")
                yield Input(placeholder="valeur", id="config-value-input")
                with Container(classes="omega-btn-frame"):
                    yield Button("Definir", id="config-set")

            yield Static("Purge de l'historique", classes="omega-subtitle")
            yield Static("0 = toutes les observations existantes (utile pour tester sans attendre)", classes="omega-hint")
            with Horizontal(classes="omega-actions"):
                yield Input(placeholder="anciennete en jours", id="cleanup-days-input")
                with Container(classes="omega-btn-frame"):
                    yield Button("Apercu", id="cleanup-preview")
                with Container(classes="omega-btn-frame"):
                    yield Button("Purger", id="cleanup-run", variant="error")
            yield Static("", id="cleanup-text", classes="omega-hint")

            yield Static("Fichiers locaux", classes="omega-subtitle")
            with Horizontal(classes="omega-actions"), Container(classes="omega-btn-frame"):
                yield Button("Vider les captures d'ecran", id="clear-screenshots", variant="error")
            with Horizontal(classes="omega-actions"), Container(classes="omega-btn-frame"):
                yield Button("Vider les exports", id="clear-exports", variant="error")
            yield Static("", id="clear-files-text", classes="omega-hint")

            with Horizontal(classes="omega-actions"), Container(classes="omega-btn-frame"):
                yield Button("Retour", id="back")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#theme-select", Select).value = self.app.theme
        self._refresh_diagnostics()
        self._refresh_settings()

    def _refresh_settings(self) -> None:
        settings = get_settings(settings_repository=self._container.settings_repository)
        text = "\n".join(f"{key} = {value}" for key, value in sorted(settings.items())) or "(aucun)"
        self.query_one("#settings-text", Static).update(text)

    def _refresh_diagnostics(self) -> None:
        provider = self._container.settings_repository.get("geoip_provider") or "dbip"
        report = run_diagnostics(
            traceroute_collector=self._container.traceroute_collector,
            geoip_database_repository=self._container.geoip_database_repository,
            geoip_provider=provider,
            var_dir=self._container.var_dir,
            now=self._container.clock,
        )
        text = (
            f"version : {report.app_version} | schema export : {report.schema_version}\n"
            f"repertoire de donnees : {report.var_dir}\n"
            f"traceroute disponible : {'oui' if report.traceroute_available else 'non'}\n"
            f"base GeoIP ({report.geoip_status.provider}) : "
            f"{'absente' if report.geoip_status.status is None else report.geoip_status.status.status}"
        )
        self.query_one("#diagnostics-text", Static).update(text)

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "theme-select":
            theme_name = str(event.value)
            try:
                select_theme(settings_repository=self._container.settings_repository, theme_name=theme_name)
            except UnknownThemeError as exc:
                self.app.notify(str(exc), severity="error")
                return
            self.app.theme = theme_name
            return
        if event.select.id == "render-profile-select":
            raw = str(event.value)
            select_render_profile(
                settings_repository=self._container.settings_repository,
                render_profile=RenderProfile(raw) if raw else None,
            )
            self.app.notify("Profil de rendu applique au prochain demarrage.")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()
            return
        if event.button.id == "config-set":
            self._config_set()
            return
        if event.button.id == "cleanup-preview":
            self._cleanup_preview()
            return
        if event.button.id == "cleanup-run":
            self._confirm_cleanup()
            return
        if event.button.id == "clear-screenshots":
            self._confirm_clear("screenshots", self._container.default_screenshots_dir)
            return
        if event.button.id == "clear-exports":
            self._confirm_clear("exports", self._container.default_exports_dir)

    def _config_set(self) -> None:
        key = self.query_one("#config-key-input", Input).value.strip()
        value = self.query_one("#config-value-input", Input).value
        if not key:
            self.app.notify("Saisissez une cle.", severity="warning")
            return
        self._container.settings_repository.set(key, value)
        self.query_one("#config-key-input", Input).value = ""
        self.query_one("#config-value-input", Input).value = ""
        self._refresh_settings()
        self.app.notify(f"{key} = {value}")

    def _parsed_days(self) -> int | None:
        raw = self.query_one("#cleanup-days-input", Input).value.strip()
        if not raw.isdigit():
            self.app.notify("Saisissez une anciennete en jours (entier).", severity="warning")
            return None
        return int(raw)

    def _cleanup_preview(self) -> None:
        days = self._parsed_days()
        if days is None:
            return
        preview = preview_history_cleanup(
            track_run_repository=self._container.track_run_repository,
            older_than=timedelta(days=days),
            now=self._container.clock,
        )
        self.query_one("#cleanup-text", Static).update(f"{preview.count} execution(s) seraient supprimee(s).")

    def _confirm_cleanup(self) -> None:
        days = self._parsed_days()
        if days is None:
            return
        self.app.push_screen(
            ConfirmScreen(
                title="PURGER L'HISTORIQUE ?",
                message=f"Supprime definitivement toutes les executions de plus de {days} jour(s).",
            ),
            lambda confirmed: self._cleanup_if_confirmed(confirmed, days),
        )

    def _cleanup_if_confirmed(self, confirmed: bool | None, days: int) -> None:
        if not confirmed:
            return
        result = cleanup_history(
            track_run_repository=self._container.track_run_repository,
            finding_repository=self._container.finding_repository,
            export_repository=self._container.export_repository,
            older_than=timedelta(days=days),
            now=self._container.clock,
        )
        self.query_one("#cleanup-text", Static).update(f"{result.count} execution(s) supprimee(s).")

    def _confirm_clear(self, label: str, directory: Path) -> None:
        self.app.push_screen(
            ConfirmScreen(
                title=f"VIDER LES {label.upper()} ?",
                message=f"Supprime definitivement tous les fichiers de {directory}.",
            ),
            lambda confirmed: self._clear_if_confirmed(confirmed, label, directory),
        )

    def _clear_if_confirmed(self, confirmed: bool | None, label: str, directory: Path) -> None:
        if not confirmed:
            return
        deleted = clear_directory(directory)
        self.query_one("#clear-files-text", Static).update(f"{deleted} fichier(s) {label} supprime(s).")
