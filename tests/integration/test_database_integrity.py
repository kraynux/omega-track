# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

import hashlib
from pathlib import Path

import maxminddb
import pytest

from omega_track.infrastructure.geoip.database_integrity import compute_checksum, validate_mmdb


def test_compute_checksum_matches_real_sha256(tmp_path: Path) -> None:
    path = tmp_path / "sample.mmdb"
    path.write_bytes(b"contenu de test")
    assert compute_checksum(path) == hashlib.sha256(b"contenu de test").hexdigest()


def test_validate_mmdb_rejects_corrupt_file(tmp_path: Path) -> None:
    path = tmp_path / "corrupt.mmdb"
    path.write_bytes(b"pas un vrai mmdb")
    assert validate_mmdb(path) is False


def test_validate_mmdb_rejects_missing_file(tmp_path: Path) -> None:
    assert validate_mmdb(tmp_path / "absent.mmdb") is False


def test_validate_mmdb_accepts_a_file_maxminddb_can_open(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = tmp_path / "valid.mmdb"
    path.write_bytes(b"peu importe le contenu ici, l'ouverture est simulee")

    class _FakeReader:
        def close(self) -> None:
            pass

    monkeypatch.setattr(maxminddb, "open_database", lambda _path: _FakeReader())
    assert validate_mmdb(path) is True
