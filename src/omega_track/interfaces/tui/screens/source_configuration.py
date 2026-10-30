# Copyright (c) 2026 kraynux - Licence MIT
"""Ecran Sources a cle : divulgation obligatoire (cle requise/quota/
donnees envoyees/confidentialite) avant toute activation (plan de dev
§12), configuration/retrait de cle, statut (cle configuree/backoff
actif). La divulgation s'affiche des la selection d'une source dans le
`Select` (`on_mount`/`on_select_changed`) - jamais seulement au clic sur
"Enregistrer" : impossible de faire defiler l'ecran sans la voir."""
from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, Footer, Header, Input, Select, Static

from omega_track.application.commands.reputation.clear_source_key import clear_source_key
from omega_track.application.commands.reputation.configure_source_key import configure_source_key
from omega_track.application.exceptions import ApiKeyMissingError
from omega_track.application.queries.get_source_disclosure import (
    get_source_disclosure,
    list_known_reputation_sources,
)
from omega_track.application.queries.get_source_status import get_source_status
from omega_track.interfaces.tui.screens._base import OmegaScreen
from omega_track.shared.i18n import _

if TYPE_CHECKING:
    from omega_track.app.container import DependencyContainer


class SourceConfigurationScreen(OmegaScreen):
    """Configuration des sources de reputation a cle (VirusTotal/HIBP)."""

    def __init__(self, *, container: DependencyContainer) -> None:
        super().__init__()
        self._container = container

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="omega-form-panel"):
            yield Static(_("SOURCES À CLÉ"), classes="omega-title")
            yield Select(
                [(name, name) for name in list_known_reputation_sources()], id="source-select"
            )
            yield Static("", id="disclosure-text", classes="omega-subtitle")
            yield Static("", id="status-text", classes="omega-hint")

            yield Static(_("Clé API"), classes="omega-subtitle")
            yield Input(placeholder=_("clé API"), password=True, id="key-input")

            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Enregistrer la clé"), id="save-key", variant="primary")
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Retirer la clé"), id="clear-key", variant="error")
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Retour"), id="back")
        yield Footer()

    def on_mount(self) -> None:
        self.query_one("#source-select", Select).value = list_known_reputation_sources()[0]
        self._refresh(list_known_reputation_sources()[0])

    def on_select_changed(self, event: Select.Changed) -> None:
        if event.select.id == "source-select":
            self._refresh(str(event.value))

    def _refresh(self, source_name: str) -> None:
        disclosure = get_source_disclosure(source_name)
        payant = _(" -- SOURCE PAYANTE") if disclosure.is_paid else ""
        self.query_one("#disclosure-text", Static).update(
            _("[b]{source_name}{payant}[/b]\nQuota : {quota_notice}\nDonnées envoyées : "
              "{data_sent_notice}\nConfidentialité : {privacy_notice}").format(source_name=source_name, payant=payant, quota_notice=disclosure.quota_notice, data_sent_notice=disclosure.data_sent_notice, privacy_notice=disclosure.privacy_notice)
        )
        status = get_source_status(
            secret_store=self._container.secret_store,
            settings_repository=self._container.settings_repository,
            source_name=source_name,
            now=self._container.clock,
        )
        backoff = ""
        if status.in_backoff and status.backoff_until is not None:
            backoff = _(" (en attente jusqu'à {isoformat})").format(isoformat=status.backoff_until.isoformat())
        self.query_one("#status-text", Static).update(
            _("clé {value}{backoff}").format(value=_("configurée") if status.key_configured else _("absente"), backoff=backoff)
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()
            return
        source_name = str(self.query_one("#source-select", Select).value)
        if event.button.id == "save-key":
            self._save_key(source_name)
            return
        if event.button.id == "clear-key":
            self._clear_key(source_name)

    def _save_key(self, source_name: str) -> None:
        api_key = self.query_one("#key-input", Input).value
        try:
            configure_source_key(secret_store=self._container.secret_store, source_name=source_name, api_key=api_key)
        except ApiKeyMissingError as exc:
            self.app.notify(str(exc), severity="warning")
            return
        self.query_one("#key-input", Input).value = ""
        self._refresh(source_name)
        self.app.notify(_("Clé enregistrée pour {source_name}.").format(source_name=source_name))

    def _clear_key(self, source_name: str) -> None:
        clear_source_key(secret_store=self._container.secret_store, source_name=source_name)
        self._refresh(source_name)
        self.app.notify(_("Clé retirée pour {source_name}.").format(source_name=source_name))
