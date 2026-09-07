# Copyright (c) 2026 kraynux - Licence MIT
"""Ouverture d'une connexion SQLite configuree pour le projet - copie
verbatim du patron de CHECK (D-007) : `check_same_thread=False` (TUI
Phase 11, worker Textual separe du thread principal, connexion ouverte
une seule fois par app/bootstrap.py)."""
from __future__ import annotations

import sqlite3
from pathlib import Path

from omega_track.infrastructure.repositories.sqlite.schema import SCHEMA_STATEMENTS


def open_connection(path: Path) -> sqlite3.Connection:
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    for statement in SCHEMA_STATEMENTS:
        connection.execute(statement)
    connection.commit()
    return connection
