# Copyright (c) 2026 kraynux - Licence MIT
"""Implementation SQLite du port TrackRunRepository. Persiste TrackRun +
ModuleRun ensemble (aggregat "execution") - `module_runs` reecrit en
delete-then-insert a chaque save() (pas de `ON DELETE CASCADE` fiable
par defaut, meme raisonnement deja documente pour DEEP/FOLD dans la
suite)."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime

from omega_track.domain.entities.track_run import ModuleRun, TrackRun
from omega_track.domain.value_objects.collection_mode import CollectionMode
from omega_track.domain.value_objects.identifiers import ModuleRunId, TargetId, TrackRunId
from omega_track.domain.value_objects.statuses import ModuleStatus, TrackStatus
from omega_track.infrastructure.exceptions import StorageError
from omega_track.infrastructure.repositories.sqlite._profile_serde import (
    profile_from_snapshot_json,
    profile_snapshot_json,
)


class SqliteTrackRunRepository:
    """Implemente ports/repositories/track_run_repository.py::TrackRunRepository."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def save(self, run: TrackRun) -> None:
        try:
            self._connection.execute(
                """
                INSERT INTO track_runs
                    (id, target_id, profile_snapshot_json, status, progress,
                     created_at, started_at, completed_at, error_summary, tags_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    status = excluded.status,
                    progress = excluded.progress,
                    started_at = excluded.started_at,
                    completed_at = excluded.completed_at,
                    error_summary = excluded.error_summary,
                    tags_json = excluded.tags_json
                """,
                (
                    run.id,
                    run.target_id,
                    profile_snapshot_json(run.profile_snapshot),
                    run.status.value,
                    run.progress,
                    run.created_at.isoformat(),
                    run.started_at.isoformat() if run.started_at else None,
                    run.completed_at.isoformat() if run.completed_at else None,
                    run.error_summary,
                    json.dumps(sorted(run.tags)),
                ),
            )
            self._connection.execute("DELETE FROM module_runs WHERE track_run_id = ?", (run.id,))
            for module_run in run.module_runs.values():
                self._connection.execute(
                    """
                    INSERT INTO module_runs
                        (id, track_run_id, module_name, status, collection_mode,
                         started_at, completed_at, source_name, error_code, error_detail)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        module_run.id,
                        run.id,
                        module_run.module_name,
                        module_run.status.value,
                        module_run.collection_mode.value,
                        module_run.started_at.isoformat() if module_run.started_at else None,
                        module_run.completed_at.isoformat() if module_run.completed_at else None,
                        module_run.source_name,
                        module_run.error_code,
                        module_run.error_detail,
                    ),
                )
            self._connection.commit()
        except sqlite3.Error as exc:
            raise StorageError(f"echec de sauvegarde du TrackRun {run.id!r}") from exc

    def get(self, track_run_id: TrackRunId) -> TrackRun | None:
        row = self._connection.execute(
            "SELECT * FROM track_runs WHERE id = ?", (track_run_id,)
        ).fetchone()
        return self._hydrate(row) if row is not None else None

    def list_for_target(self, target_id: TargetId) -> list[TrackRun]:
        rows = self._connection.execute(
            "SELECT * FROM track_runs WHERE target_id = ? ORDER BY created_at DESC", (target_id,)
        ).fetchall()
        return [self._hydrate(row) for row in rows]

    def list_recent(
        self,
        *,
        status: str | None = None,
        tag: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> list[TrackRun]:
        clauses: list[str] = []
        params: list[object] = []
        if status is not None:
            clauses.append("status = ?")
            params.append(status)
        if since is not None:
            clauses.append("created_at >= ?")
            params.append(since.isoformat())
        if until is not None:
            clauses.append("created_at <= ?")
            params.append(until.isoformat())
        where = f"WHERE {' AND '.join(clauses)}" if clauses else ""
        rows = self._connection.execute(
            f"SELECT * FROM track_runs {where} ORDER BY created_at DESC", params
        ).fetchall()
        runs = [self._hydrate(row) for row in rows]
        if tag is not None:
            runs = [r for r in runs if tag in r.tags]
        return runs

    def delete(self, track_run_id: TrackRunId) -> None:
        self._connection.execute("DELETE FROM module_runs WHERE track_run_id = ?", (track_run_id,))
        self._connection.execute("DELETE FROM track_runs WHERE id = ?", (track_run_id,))
        self._connection.commit()

    def _hydrate(self, row: sqlite3.Row) -> TrackRun:
        module_rows = self._connection.execute(
            "SELECT * FROM module_runs WHERE track_run_id = ?", (row["id"],)
        ).fetchall()
        module_runs = {mr["module_name"]: self._row_to_module_run(mr) for mr in module_rows}
        return TrackRun(
            id=TrackRunId(row["id"]),
            target_id=TargetId(row["target_id"]),
            profile_snapshot=profile_from_snapshot_json(row["profile_snapshot_json"]),
            status=TrackStatus(row["status"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            started_at=datetime.fromisoformat(row["started_at"]) if row["started_at"] else None,
            completed_at=datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None,
            progress=row["progress"],
            error_summary=row["error_summary"],
            tags=set(json.loads(row["tags_json"])),
            module_runs=module_runs,
        )

    @staticmethod
    def _row_to_module_run(row: sqlite3.Row) -> ModuleRun:
        return ModuleRun(
            id=ModuleRunId(row["id"]),
            module_name=row["module_name"],
            status=ModuleStatus(row["status"]),
            collection_mode=CollectionMode(row["collection_mode"]),
            started_at=datetime.fromisoformat(row["started_at"]) if row["started_at"] else None,
            completed_at=datetime.fromisoformat(row["completed_at"]) if row["completed_at"] else None,
            source_name=row["source_name"],
            error_code=row["error_code"],
            error_detail=row["error_detail"],
        )
