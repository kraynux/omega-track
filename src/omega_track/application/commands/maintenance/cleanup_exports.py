# Copyright (c) 2026 kraynux - Licence MIT
"""Suppression des exports d'un ensemble de TrackRun (plan de dev §9,
"politique de retention" - "les exports peuvent etre supprimes sans
supprimer l'execution source", docs/PRIVACY.md §5) - supprime le fichier
sur disque ET la ligne `exports` (Phase 4), jamais l'un sans l'autre.
Reutilise par cleanup_history.py (purge combinee run+exports), mais
appelable independamment (nettoyer seulement les exports d'anciens runs
sans purger l'historique lui-meme)."""
from __future__ import annotations

from pathlib import Path

from omega_track.domain.value_objects.identifiers import TrackRunId
from omega_track.ports.repositories.export_repository import ExportRepository


def delete_exports_for_runs(
    *, export_repository: ExportRepository, track_run_ids: list[TrackRunId]
) -> int:
    deleted = 0
    for track_run_id in track_run_ids:
        for artifact in export_repository.list_for_run(track_run_id):
            Path(artifact.output_path).unlink(missing_ok=True)
            export_repository.delete(artifact.id)
            deleted += 1
    return deleted
