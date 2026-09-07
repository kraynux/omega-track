# Copyright (c) 2026 kraynux - Licence MIT
"""`settings.json` (tranche, pas TOML/table SQLite - plan de dev Phase 4)."""
from pathlib import Path

from omega_track.infrastructure.config.json_settings_loader import JsonSettingsRepository


def test_get_missing_key_returns_default(tmp_path: Path) -> None:
    repo = JsonSettingsRepository(tmp_path / "settings.json")
    assert repo.get("theme", "dark") == "dark"


def test_set_then_get_round_trips(tmp_path: Path) -> None:
    repo = JsonSettingsRepository(tmp_path / "settings.json")
    repo.set("theme", "light")
    assert repo.get("theme") == "light"


def test_settings_persisted_across_repository_instances(tmp_path: Path) -> None:
    path = tmp_path / "settings.json"
    JsonSettingsRepository(path).set("geoip_provider", "dbip")
    reloaded = JsonSettingsRepository(path)
    assert reloaded.get("geoip_provider") == "dbip"


def test_all_returns_every_setting(tmp_path: Path) -> None:
    repo = JsonSettingsRepository(tmp_path / "settings.json")
    repo.set("a", "1")
    repo.set("b", "2")
    assert repo.all() == {"a": "1", "b": "2"}


def test_creates_parent_directory_on_write(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "settings.json"
    JsonSettingsRepository(path).set("k", "v")
    assert path.exists()
