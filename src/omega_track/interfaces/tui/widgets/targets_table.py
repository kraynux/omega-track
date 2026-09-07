# Copyright (c) 2026 kraynux - Licence MIT
"""Tableau des cibles enregistrees (adapte du patron
interfaces/tui/widgets/targets_table.py d'omega-check, D-007/D-008)."""
from __future__ import annotations

from textual.widgets import DataTable

from omega_track.domain.entities.target import Target


class TargetsTable(DataTable[str]):
    """Une ligne par cible enregistree. Cle de ligne = str(target.id)."""

    def on_mount(self) -> None:
        self.cursor_type = "row"
        self.add_columns("Valeur", "Alias", "Tags", "Epinglee", "Dernier statut")

    def set_targets(self, targets: list[Target]) -> None:
        self.clear()
        for target in targets:
            self.add_row(
                str(target.value),
                target.alias or "-",
                ", ".join(sorted(target.tags)) or "-",
                "oui" if target.pinned else "non",
                target.last_status or "-",
                key=str(target.id),
            )
