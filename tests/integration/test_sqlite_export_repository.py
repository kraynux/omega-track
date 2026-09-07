# Copyright (c) 2026 kraynux - Licence MIT
import sqlite3
from datetime import datetime, timezone

from omega_track.domain.entities.export_artifact import ExportArtifact
from omega_track.domain.value_objects.identifiers import ExportId, TrackRunId
from omega_track.domain.value_objects.statuses import RedactionPolicy
from omega_track.infrastructure.repositories.sqlite.export_repository import (
    SqliteExportRepository,
)

_NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def _artifact(**overrides) -> ExportArtifact:
    defaults = {
        "id": ExportId("e1"),
        "track_run_id": TrackRunId("run-1"),
        "format": "json",
        "output_path": "var/exports/run-1.json",
        "checksum": "deadbeef",
        "redaction_policy": RedactionPolicy.NONE,
        "created_at": _NOW,
    }
    defaults.update(overrides)
    return ExportArtifact(**defaults)


def test_save_and_list_for_run(connection: sqlite3.Connection) -> None:
    repo = SqliteExportRepository(connection)
    repo.save(_artifact())
    results = repo.list_for_run(TrackRunId("run-1"))
    assert len(results) == 1
    assert results[0].format == "json"
    assert results[0].redaction_policy == RedactionPolicy.NONE


def test_list_for_run_scoped_to_run(connection: sqlite3.Connection) -> None:
    repo = SqliteExportRepository(connection)
    repo.save(_artifact(id=ExportId("e1"), track_run_id=TrackRunId("run-1")))
    repo.save(_artifact(id=ExportId("e2"), track_run_id=TrackRunId("run-2")))
    assert len(repo.list_for_run(TrackRunId("run-1"))) == 1


def test_delete_removes_export(connection: sqlite3.Connection) -> None:
    repo = SqliteExportRepository(connection)
    repo.save(_artifact())
    repo.delete(ExportId("e1"))
    assert repo.list_for_run(TrackRunId("run-1")) == []
