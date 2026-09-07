# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat de persistance des exports generes (plan de dev, Phase 3/4/8)."""
from __future__ import annotations

from typing import Protocol

from omega_track.domain.entities.export_artifact import ExportArtifact
from omega_track.domain.value_objects.identifiers import ExportId, TrackRunId


class ExportRepository(Protocol):
    def save(self, artifact: ExportArtifact) -> None: ...

    def list_for_run(self, track_run_id: TrackRunId) -> list[ExportArtifact]: ...

    def delete(self, export_id: ExportId) -> None: ...
