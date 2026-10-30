# Copyright (c) 2026 kraynux - Licence MIT
"""Implementation SQLite du port TrackProfileRepository."""
from __future__ import annotations

import sqlite3

from omega_track.domain.entities.track_profile import TrackProfile
from omega_track.domain.value_objects.identifiers import TrackProfileId
from omega_track.infrastructure.exceptions import StorageError
from omega_track.infrastructure.repositories.sqlite._profile_serde import (
    modules_json_for,
    options_json_for,
    profile_from_columns,
)
from omega_track.shared.i18n import _


class SqliteTrackProfileRepository:
    """Implemente ports/repositories/track_profile_repository.py::TrackProfileRepository."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def save(self, profile: TrackProfile) -> None:
        try:
            self._connection.execute(
                """
                INSERT INTO track_profiles
                    (id, name, is_default, modules_json, options_json, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    is_default = excluded.is_default,
                    modules_json = excluded.modules_json,
                    options_json = excluded.options_json,
                    updated_at = excluded.updated_at
                """,
                (
                    profile.id,
                    profile.name,
                    int(profile.is_default),
                    modules_json_for(profile),
                    options_json_for(profile),
                    profile.created_at.isoformat(),
                    profile.updated_at.isoformat(),
                ),
            )
            self._connection.commit()
        except sqlite3.Error as exc:
            raise StorageError(_("échec de sauvegarde du profil {id!r}").format(id=profile.id)) from exc

    def get(self, profile_id: TrackProfileId) -> TrackProfile | None:
        row = self._connection.execute(
            "SELECT * FROM track_profiles WHERE id = ?", (profile_id,)
        ).fetchone()
        return self._row_to_profile(row) if row is not None else None

    def get_default(self) -> TrackProfile | None:
        row = self._connection.execute(
            "SELECT * FROM track_profiles WHERE is_default = 1 LIMIT 1"
        ).fetchone()
        return self._row_to_profile(row) if row is not None else None

    def list_all(self) -> list[TrackProfile]:
        rows = self._connection.execute("SELECT * FROM track_profiles ORDER BY name").fetchall()
        return [self._row_to_profile(row) for row in rows]

    def delete(self, profile_id: TrackProfileId) -> None:
        self._connection.execute("DELETE FROM track_profiles WHERE id = ?", (profile_id,))
        self._connection.commit()

    @staticmethod
    def _row_to_profile(row: sqlite3.Row) -> TrackProfile:
        return profile_from_columns(
            id_=row["id"], name=row["name"], is_default=row["is_default"],
            modules_json=row["modules_json"], options_json=row["options_json"],
            created_at=row["created_at"], updated_at=row["updated_at"],
        )
