# Copyright (c) 2026 kraynux - Licence MIT
"""Ecran Cibles : carnet des cibles enregistrees (CRUD complet, plan de
dev §9 `target add|edit|pin|delete|list`). Adapte du patron
interfaces/tui/screens/targets.py d'omega-check (D-007/D-008), etendu :
TRACK a une vraie notion d'autorisation persistante (epinglage, D-010),
absente de CHECK - d'ou le bouton "Epingler" en plus de CHECK."""
from __future__ import annotations

from typing import TYPE_CHECKING

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Button, DataTable, Footer, Header, Input, Static

from omega_track.application.commands.targets.create_target import create_target
from omega_track.application.commands.targets.delete_targets import delete_targets
from omega_track.application.commands.targets.pin_target import pin_target
from omega_track.application.commands.targets.update_target import update_target
from omega_track.application.queries.list_targets import list_targets
from omega_track.domain.exceptions.target import DuplicateTargetError, InvalidTargetValueError
from omega_track.domain.value_objects.identifiers import TargetId
from omega_track.interfaces.tui.screens._base import OmegaScreen
from omega_track.interfaces.tui.screens.confirm import ConfirmScreen
from omega_track.interfaces.tui.widgets.targets_table import TargetsTable
from omega_track.shared.i18n import _

if TYPE_CHECKING:
    from omega_track.app.container import DependencyContainer


def _parse_tags(raw: str) -> set[str]:
    return {tag.strip() for tag in raw.split(",") if tag.strip()}


class TargetsScreen(OmegaScreen):
    """Ajouter/modifier/epingler/supprimer des cibles."""

    def __init__(self, *, container: DependencyContainer) -> None:
        super().__init__()
        self._container = container
        self._selected_id: str | None = None

    def compose(self) -> ComposeResult:
        yield Header()
        with Vertical(classes="omega-panel"):
            yield Static(_("CIBLES"), classes="omega-title")
            yield TargetsTable(id="targets-table")
            yield Input(placeholder=_("ex. 192.168.1.10, example.org"), id="value-input")
            yield Input(placeholder=_("Alias (optionnel)"), id="alias-input")
            yield Input(placeholder=_("Tags séparés par des virgules (optionnel)"), id="tags-input")
            with Horizontal(classes="omega-actions"):
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Ajouter"), id="add", variant="primary")
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Modifier"), id="edit")
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Épingler"), id="pin")
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Supprimer"), id="delete", variant="error")
                with Container(classes="omega-btn-frame"):
                    yield Button(_("Retour"), id="back")
        yield Footer()

    def on_mount(self) -> None:
        self._refresh()

    def _refresh(self) -> None:
        targets = list_targets(target_repository=self._container.target_repository)
        self.query_one(TargetsTable).set_targets(targets)

    def on_data_table_row_selected(self, event: DataTable.RowSelected) -> None:
        self._selected_id = str(event.row_key.value)
        targets = {str(t.id): t for t in list_targets(target_repository=self._container.target_repository)}
        target = targets.get(self._selected_id)
        if target is not None:
            self.query_one("#alias-input", Input).value = target.alias or ""
            self.query_one("#tags-input", Input).value = ", ".join(sorted(target.tags))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "back":
            self.dismiss()
            return
        if event.button.id == "add":
            self._add()
            return
        if event.button.id == "edit":
            self._edit()
            return
        if event.button.id == "pin":
            self._pin()
            return
        if event.button.id == "delete":
            self._confirm_delete()

    def _add(self) -> None:
        raw_value = self.query_one("#value-input", Input).value.strip()
        if not raw_value:
            self.app.notify(_("Saisissez une valeur de cible."), severity="warning")
            return
        alias = self.query_one("#alias-input", Input).value.strip() or None
        tags = _parse_tags(self.query_one("#tags-input", Input).value)
        try:
            create_target(
                target_repository=self._container.target_repository,
                raw_value=raw_value,
                alias=alias,
                tags=tags,
                id_factory=self._container.id_factory,
                now=self._container.clock,
            )
        except (InvalidTargetValueError, DuplicateTargetError) as exc:
            self.app.notify(str(exc), severity="error")
            return
        self.query_one("#value-input", Input).value = ""
        self.query_one("#alias-input", Input).value = ""
        self.query_one("#tags-input", Input).value = ""
        self._refresh()

    def _edit(self) -> None:
        if self._selected_id is None:
            self.app.notify(_("Sélectionnez d'abord une ligne."), severity="warning")
            return
        alias = self.query_one("#alias-input", Input).value.strip() or None
        tags = _parse_tags(self.query_one("#tags-input", Input).value)
        targets = {str(t.id): t for t in list_targets(target_repository=self._container.target_repository)}
        current = targets.get(self._selected_id)
        update_target(
            target_repository=self._container.target_repository,
            target_id=TargetId(self._selected_id),
            alias=alias,
            add_tags=tags - (current.tags if current else set()),
            remove_tags=(current.tags if current else set()) - tags,
            now=self._container.clock,
        )
        self._refresh()

    def _pin(self) -> None:
        if self._selected_id is None:
            self.app.notify(_("Sélectionnez d'abord une ligne."), severity="warning")
            return
        pin_target(
            target_repository=self._container.target_repository,
            target_id=TargetId(self._selected_id),
            now=self._container.clock,
        )
        self._refresh()

    def _confirm_delete(self) -> None:
        if self._selected_id is None:
            self.app.notify(_("Sélectionnez d'abord une ligne."), severity="warning")
            return
        self.app.push_screen(
            ConfirmScreen(title=_("SUPPRIMER CETTE CIBLE ?"), message=_("Cette action est irréversible.")),
            self._delete_if_confirmed,
        )

    def _delete_if_confirmed(self, confirmed: bool | None) -> None:
        if not confirmed or self._selected_id is None:
            return
        delete_targets(target_repository=self._container.target_repository, target_ids=[TargetId(self._selected_id)])
        self._selected_id = None
        self._refresh()
