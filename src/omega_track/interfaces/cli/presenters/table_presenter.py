# Copyright (c) 2026 kraynux - Licence MIT
"""Tableaux texte simples pour les commandes de listing (plan de dev §9
`target list`/`history list`) - alignement par largeur de colonne, pas de
dependance a une librairie de rendu de tableau tierce."""
from __future__ import annotations

from collections.abc import Iterable, Sequence

from omega_track.domain.entities.target import Target
from omega_track.domain.entities.track_run import TrackRun


def print_targets_table(targets: Sequence[Target]) -> None:
    rows = [
        (str(t.id), str(t.value), t.alias or "", ",".join(sorted(t.tags)), "oui" if t.pinned else "non")
        for t in targets
    ]
    _print_table(("ID", "Cible", "Alias", "Tags", "Epinglee"), rows)


def print_track_runs_table(runs: Sequence[TrackRun]) -> None:
    rows = [
        (str(r.id), str(r.target_id), r.status.value, f"{r.progress:.0%}", r.created_at.isoformat())
        for r in runs
    ]
    _print_table(("ID", "Cible", "Statut", "Progression", "Cree le"), rows)


def _print_table(headers: Sequence[str], rows: Iterable[Sequence[str]]) -> None:
    rows = list(rows)
    if not rows:
        print("(aucun resultat)")
        return
    widths = [
        max(len(headers[i]), max((len(row[i]) for row in rows), default=0)) for i in range(len(headers))
    ]
    print("  ".join(header.ljust(widths[i]) for i, header in enumerate(headers)))
    print("  ".join("-" * width for width in widths))
    for row in rows:
        print("  ".join(cell.ljust(widths[i]) for i, cell in enumerate(row)))
