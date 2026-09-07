# Copyright (c) 2026 kraynux - Licence MIT
"""Implementation SQLite du port TargetRepository (ports/repositories/
target_repository.py) - meme patron que CHECK (D-007) : SQL brut,
`row_factory = sqlite3.Row`, erreurs sqlite3 traduites en StorageError."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime

from omega_track.domain.entities.target import Target
from omega_track.domain.value_objects.identifiers import TargetId
from omega_track.domain.value_objects.target_value import (
    TargetValue,
    parse_target_value,
    target_kind_of,
)
from omega_track.infrastructure.exceptions import StorageError


class SqliteTargetRepository:
    """Implemente ports/repositories/target_repository.py::TargetRepository."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def save(self, target: Target) -> None:
        try:
            self._connection.execute(
                """
                INSERT INTO targets
                    (id, normalized_value, target_kind, alias, tags_json, pinned,
                     created_at, updated_at, last_track_at, last_status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    normalized_value = excluded.normalized_value,
                    target_kind = excluded.target_kind,
                    alias = excluded.alias,
                    tags_json = excluded.tags_json,
                    pinned = excluded.pinned,
                    updated_at = excluded.updated_at,
                    last_track_at = excluded.last_track_at,
                    last_status = excluded.last_status
                """,
                (
                    target.id,
                    str(target.value),
                    target_kind_of(target.value).value,
                    target.alias,
                    json.dumps(sorted(target.tags)),
                    int(target.pinned),
                    target.created_at.isoformat(),
                    target.updated_at.isoformat(),
                    target.last_track_at.isoformat() if target.last_track_at else None,
                    target.last_status,
                ),
            )
            self._connection.commit()
        except sqlite3.Error as exc:
            raise StorageError(f"echec de sauvegarde de la cible {target.id!r}") from exc

    def get(self, target_id: TargetId) -> Target | None:
        row = self._connection.execute("SELECT * FROM targets WHERE id = ?", (target_id,)).fetchone()
        return self._row_to_target(row) if row is not None else None

    def find_by_value(self, value: TargetValue) -> Target | None:
        row = self._connection.execute(
            "SELECT * FROM targets WHERE normalized_value = ? AND target_kind = ?",
            (str(value), target_kind_of(value).value),
        ).fetchone()
        return self._row_to_target(row) if row is not None else None

    def list_all(self) -> list[Target]:
        rows = self._connection.execute("SELECT * FROM targets ORDER BY created_at DESC").fetchall()
        return [self._row_to_target(row) for row in rows]

    def delete(self, target_id: TargetId) -> None:
        self._connection.execute("DELETE FROM targets WHERE id = ?", (target_id,))
        self._connection.commit()

    @staticmethod
    def _row_to_target(row: sqlite3.Row) -> Target:
        return Target(
            id=TargetId(row["id"]),
            value=parse_target_value(row["normalized_value"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            alias=row["alias"],
            tags=set(json.loads(row["tags_json"])),
            pinned=bool(row["pinned"]),
            last_track_at=datetime.fromisoformat(row["last_track_at"]) if row["last_track_at"] else None,
            last_status=row["last_status"],
        )
