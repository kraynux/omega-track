# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

import stat
from pathlib import Path

from omega_track.infrastructure.config.secret_store_adapter import FileSecretStore


def test_round_trips_a_secret(tmp_path: Path) -> None:
    store = FileSecretStore(tmp_path / "secrets.json")
    store.set_secret("maxmind_license_key", "abc123")
    assert store.get_secret("maxmind_license_key") == "abc123"


def test_get_secret_returns_none_when_absent(tmp_path: Path) -> None:
    store = FileSecretStore(tmp_path / "secrets.json")
    assert store.get_secret("nope") is None


def test_delete_secret_removes_key(tmp_path: Path) -> None:
    store = FileSecretStore(tmp_path / "secrets.json")
    store.set_secret("maxmind_license_key", "abc123")
    store.delete_secret("maxmind_license_key")
    assert store.get_secret("maxmind_license_key") is None


def test_delete_secret_is_a_no_op_when_absent(tmp_path: Path) -> None:
    store = FileSecretStore(tmp_path / "secrets.json")
    store.delete_secret("nope")  # ne doit pas lever


def test_file_is_written_with_owner_only_permissions(tmp_path: Path) -> None:
    path = tmp_path / "secrets.json"
    store = FileSecretStore(path)
    store.set_secret("maxmind_license_key", "abc123")
    mode = stat.S_IMODE(path.stat().st_mode)
    assert mode == 0o600
