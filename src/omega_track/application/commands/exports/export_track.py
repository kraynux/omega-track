# Copyright (c) 2026 kraynux - Licence MIT
"""Use case ExportTrack (plan de dev, Phase 8) - volontairement fin :
toute la mecanique reelle (construction du rapport, redaction, ecriture,
checksum, persistance) vit dans export_orchestrator.py. `output_dir` est
fourni par l'appelant (jamais resolu ici via
infrastructure/config/paths.py::default_exports_dir - application/ ne
peut pas importer infrastructure/, Dependency Rule) : c'est a la racine
de composition (Phase 9 CLI) de le resoudre avant d'appeler ce use case.

Prend un `ExportOrchestratorPort` structurel plutot que la classe
concrete `ExportOrchestrator` - permet de faker ce use case en test sans
construire un vrai ExportOrchestrator (qui ecrit reellement sur disque),
meme discipline "dependre d'un contrat, pas d'une implementation" que le
reste de application/."""
from __future__ import annotations

from pathlib import Path
from typing import Protocol

from omega_track.domain.entities.export_artifact import ExportArtifact
from omega_track.domain.value_objects.export_options import ExportOptions
from omega_track.domain.value_objects.identifiers import TrackRunId


class ExportOrchestratorPort(Protocol):
    def export(
        self,
        *,
        track_run_id: TrackRunId,
        export_format: str,
        output_dir: Path,
        options: ExportOptions | None,
    ) -> ExportArtifact: ...


def export_track(
    *,
    export_orchestrator: ExportOrchestratorPort,
    track_run_id: TrackRunId,
    export_format: str,
    output_dir: Path,
    options: ExportOptions | None = None,
) -> ExportArtifact:
    return export_orchestrator.export(
        track_run_id=track_run_id,
        export_format=export_format,
        output_dir=output_dir,
        options=options,
    )
