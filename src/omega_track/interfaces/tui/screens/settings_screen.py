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
from omega_track.interfaces.tui.language_setting import LanguageSetting
from omega_track.interfaces.tui.screens._base import OmegaScreen
from omega_track.interfaces.tui.screens.confirm import ConfirmScreen
from omega_track.shared.i18n import _

if TYPE_CHECKING:
    from omega_track.app.container import DependencyContainer

_RENDER_PROFILE_CHOICES: tuple[tuple[str, str], ...] = (
    (_("(automatique)"), ""),
    *((p.value, p.value) for p in RenderProfile),
)

_RENDER_PROFILE_OVERRIDE_KEY = "render_profile_override"
"""Meme cle/meme duplication locale que select_render_profile.py et
startup_controller.py (D-008) - lue ici pour donner au Select sa valeur
INITIALE directement au constructeur (voir compose() ci-dessous)."""


class SettingsScreen(OmegaScreen):
    """Theme, rendu, reglages generiques, diagnostics, purge."""

    def __init__(self, *, container: DependencyContainer) -> None:
        super().__init__()
        self._container = container

    def compose(self) -> ComposeResult:
        yield Header()
        # Retour utilisateur (bug reel : la notification "Profil de
        # rendu applique au prochain demarrage" s'affichait a CHAQUE
        # visite de cet ecran, meme sans toucher au Select) - meme
        # diagnostic et meme correctif qu'omega-stress
        # (interfaces/tui/screens/settings_screen.py) : un Select SANS
        # `value=` passe au constructeur choisit lui-meme sa PREMIERE
        # option et poste son evenement Changed pendant son PROPRE
        # montage, AVANT que le on_mount() de cet ecran ne s'execute -
        # un garde-fou pose dans on_mount() (`self.prevent(...)` ou un
        # flag "pret") arrive donc toujours trop tard pour l'intercepter.
        # En passant `value=` directement ICI, au constructeur, le
        # Select n'a jamais besoin de choisir une option par defaut :
        # aucun evenement Changed parasite ne peut se produire.
        current_theme = self.app.theme
        stored_profile = self._container.settings_repository.get(_RENDER_PROFILE_OVERRIDE_KEY, "")
        with VerticalScroll(classes="omega-panel"):
            yield Static(_("RÉGLAGES"), classes="omega-title")

            yield Static(_("Thème"), classes="omega-subtitle")
            yield Select([(name, name) for name in TUI_THEMES], id="theme-select", allow_blank=False, value=current_theme)

            yield Static(_("Profil de rendu (surcharge la détection automatique)"), classes="omega-subtitle")
            yield Select(_RENDER_PROFILE_CHOICES, id="render-profile-select", allow_blank=False, value=stored_profile)

            yield LanguageSetting(self._container.settings_repository)

            yield Static(_("Diagnostics"), classes="omega-subtitle")
            yield Static("", id="diagnostics-text")

            yield Static(_("Réglages actuels"), classes="omega-subtitle")
            yield Static("", id="settings-text")
            with Horizontal(classes="omega-actions"):
                yield Input(placeholder="cle", id="config-key-input")
                yield Input(placeholder="valeur", id="config-value-input")
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Définir"), id="config-set")

            yield Static(_("Purge de l'historique"), classes="omega-subtitle")
            yield Static(_("0 = toutes les observations existantes (utile pour tester sans "
                           "attendre)"), classes="omega-hint")
            with Horizontal(classes="omega-actions"):
                yield Input(placeholder=_("ancienneté en jours"), id="cleanup-days-input")
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Aperçu"), id="cleanup-preview")
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Purger"), id="cleanup-run", variant="error")
            yield Static("", id="cleanup-text", classes="omega-hint")

            yield Static(_("Fichiers locaux"), classes="omega-subtitle")
            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Vider les captures d'écran"), id="clear-screenshots", variant="error")
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Vider les exports"), id="clear-exports", variant="error")
            yield Static("", id="clear-files-text", classes="omega-hint")

            with Horizontal(classes="omega-actions"), Container(classes="omega-btn-frame"):
                yield Button(_("Retour"), id="back")
        yield Footer()

    def on_mount(self) -> None:
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
            _("version : {app_version} | schéma export : {schema_version}\nrépertoire de "
              "données : {var_dir}\ntraceroute disponible : {value}\nbase GeoIP ({provider}) : "
              "{value2}").format(app_version=report.app_version, schema_version=report.schema_version, var_dir=report.var_dir, value=_("oui") if report.traceroute_available else _("non"), provider=report.geoip_status.provider, value2=_("absente") if report.geoip_status.status is None else report.geoip_status.status.status)
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
            # Valeur initiale signalee a l'ouverture : ne rien enregistrer ni notifier (retour 2026-11-10).
            if raw == str(self._container.settings_repository.get(_RENDER_PROFILE_OVERRIDE_KEY, "") or ""):
                return
            select_render_profile(
                settings_repository=self._container.settings_repository,
                render_profile=RenderProfile(raw) if raw else None,
            )
            self.app.notify(_("Profil de rendu appliqué au prochain démarrage."))

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
            self.app.notify(_("Saisissez une clé."), severity="warning")
            return
        self._container.settings_repository.set(key, value)
        self.query_one("#config-key-input", Input).value = ""
        self.query_one("#config-value-input", Input).value = ""
        self._refresh_settings()
        self.app.notify(_("{key} = {value}").format(key=key, value=value))

    def _parsed_days(self) -> int | None:
        raw = self.query_one("#cleanup-days-input", Input).value.strip()
        if not raw.isdigit():
            self.app.notify(_("Saisissez une ancienneté en jours (entier)."), severity="warning")
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
        self.query_one("#cleanup-text", Static).update(_("{count} exécution(s) seraient "
                                                         "supprimée(s).").format(count=preview.count))

    def _confirm_cleanup(self) -> None:
        days = self._parsed_days()
        if days is None:
            return
        self.app.push_screen(
            ConfirmScreen(
                title=_("PURGER L'HISTORIQUE ?"),
                message=_("Supprime définitivement toutes les exécutions de plus de {days} "
                          "jour(s).").format(days=days),
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
        self.query_one("#cleanup-text", Static).update(_("{count} exécution(s) supprimée(s).").format(count=result.count))

    def _confirm_clear(self, label: str, directory: Path) -> None:
        self.app.push_screen(
            ConfirmScreen(
                title=_("VIDER LES {upper} ?").format(upper=label.upper()),
                message=_("Supprime définitivement tous les fichiers de {directory}.").format(directory=directory),
            ),
            lambda confirmed: self._clear_if_confirmed(confirmed, label, directory),
        )

    def _clear_if_confirmed(self, confirmed: bool | None, label: str, directory: Path) -> None:
        if not confirmed:
            return
        deleted = clear_directory(directory)
        self.query_one("#clear-files-text", Static).update(_("{deleted} fichier(s) {label} "
                                                             "supprimé(s).").format(deleted=deleted, label=label))
