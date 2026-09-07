# Copyright (c) 2026 kraynux - Licence MIT
"""Une base vide se cree directement au schema courant (critere de
sortie Phase 4, D-018 : pas de vrai moteur de migration en MVP)."""
from pathlib import Path

from omega_track.infrastructure.repositories.sqlite.connection import open_connection

_EXPECTED_TABLES = {
    "targets", "track_profiles", "track_runs", "module_runs",
    "findings", "relations", "exports", "geoip_databases",
}


def test_fresh_database_creates_all_tables(tmp_path: Path) -> None:
    connection = open_connection(tmp_path / "omega-track.db")
    try:
        rows = connection.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        table_names = {row["name"] for row in rows}
        assert _EXPECTED_TABLES <= table_names
    finally:
        connection.close()


def test_no_settings_table_created() -> None:
    """Decision Phase 4 : settings.json est la seule source de verite
    pour les reglages - aucune table `settings` ne doit jamais exister."""
    from omega_track.infrastructure.repositories.sqlite.schema import SCHEMA_STATEMENTS

    assert not any("settings" in statement.lower() and "create table" in statement.lower() for statement in SCHEMA_STATEMENTS)


def test_reopening_existing_database_is_idempotent(tmp_path: Path) -> None:
    path = tmp_path / "omega-track.db"
    first = open_connection(path)
    first.close()
    second = open_connection(path)
    try:
        rows = second.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name NOT LIKE 'sqlite_%'"
        ).fetchall()
        assert _EXPECTED_TABLES <= {row["name"] for row in rows}
    finally:
        second.close()
