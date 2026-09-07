# Copyright (c) 2026 kraynux - Licence MIT
"""CLI de bout en bout pour `target`/`config`/`history`/`cleanup`/
`diagnostics` (Phase 9) - conteneur reel (`bootstrap()`, vraie base
SQLite via tmp_path), aucun reseau requis pour ces commandes."""
from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path

import pytest

from omega_track.app.bootstrap import bootstrap
from omega_track.app.container import DependencyContainer
from omega_track.interfaces.cli.main import run


@pytest.fixture
def container(tmp_path: Path) -> Iterator[DependencyContainer]:
    c = bootstrap(var_dir=tmp_path, console_logging=False)
    yield c
    c.close()


def test_target_add_list_pin_delete_lifecycle(container: DependencyContainer, capsys: pytest.CaptureFixture[str]) -> None:
    assert run(container, ["target", "add", "example.com", "--alias", "site", "--json"]) == 0
    added = json.loads(capsys.readouterr().out)
    target_id = added["id"]
    assert added["value"] == "example.com"
    assert added["pinned"] is False

    assert run(container, ["target", "list", "--json"]) == 0
    listed = json.loads(capsys.readouterr().out)
    assert len(listed) == 1
    assert listed[0]["id"] == target_id

    assert run(container, ["target", "pin", target_id, "--json"]) == 0
    pinned = json.loads(capsys.readouterr().out)
    assert pinned["pinned"] is True

    assert run(container, ["target", "edit", target_id, "--add-tag", "prod", "--json"]) == 0
    edited = json.loads(capsys.readouterr().out)
    assert edited["tags"] == ["prod"]

    assert run(container, ["target", "delete", target_id]) == 0
    assert run(container, ["target", "list", "--json"]) == 0
    assert json.loads(capsys.readouterr().out) == []


def test_target_add_duplicate_returns_validation_exit_code(
    container: DependencyContainer, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run(container, ["target", "add", "example.com"]) == 0
    capsys.readouterr()
    assert run(container, ["target", "add", "example.com"]) == 1


def test_target_add_invalid_value_returns_validation_exit_code(container: DependencyContainer) -> None:
    assert run(container, ["target", "add", "not a valid target!!"]) == 1


def test_target_pin_missing_returns_unavailable_exit_code(container: DependencyContainer) -> None:
    assert run(container, ["target", "pin", "missing-id"]) == 3


def test_config_show_and_set(container: DependencyContainer, capsys: pytest.CaptureFixture[str]) -> None:
    assert run(container, ["config", "set", "geoip_provider", "maxmind"]) == 0
    assert run(container, ["config", "show", "--json"]) == 0
    settings = json.loads(capsys.readouterr().out)
    assert settings["geoip_provider"] == "maxmind"


def test_history_list_empty(container: DependencyContainer, capsys: pytest.CaptureFixture[str]) -> None:
    assert run(container, ["history", "list", "--json"]) == 0
    assert json.loads(capsys.readouterr().out) == []


def test_cleanup_run_without_yes_is_refused(container: DependencyContainer) -> None:
    assert run(container, ["cleanup", "run", "--older-than", "30"]) == 1


def test_cleanup_preview_empty(container: DependencyContainer, capsys: pytest.CaptureFixture[str]) -> None:
    assert run(container, ["cleanup", "preview", "--older-than", "30", "--json"]) == 0
    assert json.loads(capsys.readouterr().out) == {"count": 0, "track_run_ids": []}


def test_diagnostics_reports_no_geoip_database_yet(
    container: DependencyContainer, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run(container, ["diagnostics", "--json"]) == 0
    report = json.loads(capsys.readouterr().out)
    assert report["geoip_status"]["status"] is None
