# Copyright (c) 2026 kraynux - Licence MIT
"""Implementation SQLite du port GeoipDatabaseRepository - `provider`
est la cle primaire naturelle (pas d'id UUID separe, voir schema.py)."""
from __future__ import annotations

import sqlite3
from datetime import datetime

from omega_track.domain.entities.geoip_database_status import GeoIpDatabaseStatus
from omega_track.infrastructure.exceptions import StorageError


class SqliteGeoipDatabaseRepository:
    """Implemente ports/repositories/geoip_database_repository.py::GeoipDatabaseRepository."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def save_status(self, status: GeoIpDatabaseStatus) -> None:
        try:
            self._connection.execute(
                """
                INSERT INTO geoip_databases
                    (provider, edition, local_path, checksum, downloaded_at, published_at, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(provider) DO UPDATE SET
                    edition = excluded.edition,
                    local_path = excluded.local_path,
                    checksum = excluded.checksum,
                    downloaded_at = excluded.downloaded_at,
                    published_at = excluded.published_at,
                    status = excluded.status
                """,
                (
                    status.provider,
                    status.edition,
                    status.local_path,
                    status.checksum,
                    status.downloaded_at.isoformat(),
                    status.published_at.isoformat() if status.published_at else None,
                    status.status,
                ),
            )
            self._connection.commit()
        except sqlite3.Error as exc:
            raise StorageError(f"echec de sauvegarde du statut GeoIP {status.provider!r}") from exc

    def get_status(self, provider: str) -> GeoIpDatabaseStatus | None:
        row = self._connection.execute(
            "SELECT * FROM geoip_databases WHERE provider = ?", (provider,)
        ).fetchone()
        if row is None:
            return None
        return GeoIpDatabaseStatus(
            provider=row["provider"],
            edition=row["edition"],
            local_path=row["local_path"],
            checksum=row["checksum"],
            downloaded_at=datetime.fromisoformat(row["downloaded_at"]),
            published_at=datetime.fromisoformat(row["published_at"]) if row["published_at"] else None,
            status=row["status"],
        )
