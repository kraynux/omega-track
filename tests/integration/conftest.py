# Copyright (c) 2026 kraynux - Licence MIT
import sqlite3
from collections.abc import Iterator
from pathlib import Path

import pytest

from omega_track.infrastructure.repositories.sqlite.connection import open_connection


@pytest.fixture
def connection(tmp_path: Path) -> Iterator[sqlite3.Connection]:
    conn = open_connection(tmp_path / "omega-track.db")
    try:
        yield conn
    finally:
        conn.close()
