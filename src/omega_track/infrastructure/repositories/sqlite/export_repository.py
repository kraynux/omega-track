# Copyright (c) 2026 kraynux - Licence MIT
"""Implementation SQLite du port ExportRepository."""
from __future__ import annotations

import sqlite3
from datetime import datetime

from omega_track.domain.entities.export_artifact import ExportArtifact
from omega_track.domain.value_objects.identifiers import ExportId, TrackRunId
from omega_track.domain.value_objects.statuses import RedactionPolicy
from omega_track.infrastructure.exceptions import StorageError


class SqliteExportRepository:
    """Implemente ports/repositories/export_repository.py::ExportRepository."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def save(self, artifact: ExportArtifact) -> None:
        try:
            self._connection.execute(
                """
                INSERT INTO exports
                    (id, track_run_id, format, output_path, checksum, redaction_policy, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    artifact.id,
                    artifact.track_run_id,
                    artifact.format,
                    artifact.output_path,
                    artifact.checksum,
                    artifact.redaction_policy.value,
                    artifact.created_at.isoformat(),
                ),
            )
            self._connection.commit()
        except sqlite3.Error as exc:
            raise StorageError(f"echec de sauvegarde de l'export {artifact.id!r}") from exc

    def list_for_run(self, track_run_id: TrackRunId) -> list[ExportArtifact]:
        rows = self._connection.execute(
            "SELECT * FROM exports WHERE track_run_id = ? ORDER BY created_at DESC", (track_run_id,)
        ).fetchall()
        return [self._row_to_artifact(row) for row in rows]

    def delete(self, export_id: ExportId) -> None:
        self._connection.execute("DELETE FROM exports WHERE id = ?", (export_id,))
        self._connection.commit()

    @staticmethod
    def _row_to_artifact(row: sqlite3.Row) -> ExportArtifact:
        return ExportArtifact(
            id=ExportId(row["id"]),
            track_run_id=TrackRunId(row["track_run_id"]),
            format=row["format"],
            output_path=row["output_path"],
            checksum=row["checksum"],
            redaction_policy=RedactionPolicy(row["redaction_policy"]),
            created_at=datetime.fromisoformat(row["created_at"]),
        )
