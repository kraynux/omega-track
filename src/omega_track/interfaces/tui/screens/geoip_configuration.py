# Copyright (c) 2026 kraynux - Licence MIT
"""Ecran GeoIP : etat de la base locale, choix du fournisseur, mise a
jour, cle de licence MaxMind (plan de dev §9 `geoip status|update
[--provider]`, §5).

Mise a jour lancee via un worker (`run_worker` + `asyncio.to_thread`),
jamais appelee directement dans le handler du bouton : `update_geoip_
database` fait un vrai telechargement HTTP bloquant (Phase 5), qui
gelait toute l'interface Textual (aucun rendu, aucune reponse au
clavier) le temps du telechargement - bug signale par l'utilisateur.
Meme patron que screens/progress.py (Phase 11), sans le relais de log
(un seul appel, pas une sequence de phases a journaliser)."""
from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Input, Select, Static

from omega_track.application.commands.geoip.configure_provider import (
    configure_maxmind_credentials,
    select_geoip_provider,
)
from omega_track.application.commands.geoip.update_database import update_geoip_database
from omega_track.application.exceptions import (
    GeoIpDownloadError,
    MaxMindCredentialsMissingError,
    UnknownGeoIpProviderError,
)
from omega_track.application.policies.provider_selection import (
    VALID_GEOIP_PROVIDERS,
    resolve_active_geoip_provider,
)
from omega_track.application.queries.get_geoip_status import get_geoip_database_status
from omega_track.interfaces.tui.screens._base import OmegaScreen

if TYPE_CHECKING:
    from omega_track.app.container import DependencyContainer

_PROVIDER_SETTING_KEY = "geoip_provider"


class GeoIpConfigurationScreen(OmegaScreen):
    """Etat + configuration de la base de geolocalisation locale."""

    def __init__(self, *, container: DependencyContainer) -> None:
        super().__init__()
        self._container = container

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="omega-form-panel"):
            yield Static("GEOIP", classes="omega-title")
            yield Static("", id="status-text", classes="omega-subtitle")

            yield Static("Fournisseur", classes="omega-subtitle")
            yield Select(
                [(p, p) for p in sorted(VALID_GEOIP_PROVIDERS)], id="provider-select"
            )

            yield Static("Cle de licence MaxMind (optionnel, requise pour le fournisseur maxmind)", classes="omega-subtitle")
            yield Input(placeholder="cle de licence", password=True, id="license-key-input")

            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button("Enregistrer la cle", id="save-key")
                with Container(classes="omega-btn-frame"):
                    yield Button("Mettre a jour la base", id="update", variant="primary")
                with Container(classes="omega-btn-frame"):
                    yield Button("Retour", id="back")
        yield Footer()

    def on_mount(self) -> None:
        provider = resolve_active_geoip_provider(self._container.settings_repository.get(_PROVIDER_SETTING_KEY))
        self.query_one("#provider-select", Select).value = provider
        self._refresh_status(provider)

    def _refresh_status(self, provider: str) -> None:
        view = get_geoip_database_status(
            geoip_database_repository=self._container.geoip_database_repository,
            provider=provider,
            now=self._container.clock,
        )
        if view.status is None:
            text = f"base GeoIP ({provider}) : absente"
        else:
            stale = " (perimee)" if view.is_stale else ""
            text = f"base GeoIP ({provider}) : {view.status.status}{stale} - {view.status.local_path}"
        self.query_one("#status-text", Static).update(text)

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "provider-select":
            provider = str(event.value)
            try:
                select_geoip_provider(settings_repository=self._container.settings_repository, provider=provider)
            except UnknownGeoIpProviderError as exc:
                self.app.notify(str(exc), severity="error")
                return
            self._refresh_status(provider)

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()
            return
        if event.button.id == "save-key":
            self._save_key()
            return
        if event.button.id == "update":
            self._update()

    def _save_key(self) -> None:
        license_key = self.query_one("#license-key-input", Input).value
        try:
            configure_maxmind_credentials(secret_store=self._container.secret_store, license_key=license_key)
        except MaxMindCredentialsMissingError as exc:
            self.app.notify(str(exc), severity="warning")
            return
        self.query_one("#license-key-input", Input).value = ""
        self.app.notify("Cle de licence enregistree.")

    def _update(self) -> None:
        provider = str(self.query_one("#provider-select", Select).value)
        self.query_one("#update", Button).disabled = True
        self.app.notify("Telechargement en cours...", title="GeoIP")
        self.run_worker(self._do_update(provider), exclusive=True)

    async def _do_update(self, provider: str) -> None:
        try:
            await asyncio.to_thread(
                update_geoip_database,
                geoip_database_repository=self._container.geoip_database_repository,
                database_updater=self._container.database_updater,
                provider=provider,
                destination=self._container.geoip_db_paths[provider],
                now=self._container.clock,
            )
        except MaxMindCredentialsMissingError:
            # Bug reel signale par l'utilisateur : cette exception n'etait
            # rattrapee nulle part ici, elle remontait comme "Erreur
            # inattendue" generique (filet de securite de app.py) au lieu
            # d'un message actionnable - `update_geoip_database` (Phase 5)
            # ne l'attrape jamais lui-meme par design (precondition de
            # configuration, pas un echec de telechargement).
            self.app.notify(
                "Cle de licence MaxMind absente - renseignez-la ci-dessus avant de mettre a jour.",
                title="GeoIP", severity="warning",
            )
        except GeoIpDownloadError as exc:
            self.app.notify(str(exc), severity="error")
        else:
            self._refresh_status(provider)
            self.app.notify("Base GeoIP mise a jour.")
        finally:
            if self.is_mounted:
                self.query_one("#update", Button).disabled = False
