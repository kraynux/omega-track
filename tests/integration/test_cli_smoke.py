# Copyright (c) 2026 kraynux - Licence MIT
"""Smoke test Phase 1 : la CLI se lance et repond, aucune sous-commande
reelle n'existe encore (arrivent en Phase 9)."""
from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest

from omega_track.app.bootstrap import bootstrap
from omega_track.app.container import DependencyContainer
from omega_track.interfaces.cli.main import run


@pytest.fixture
def container(tmp_path: Path) -> Iterator[DependencyContainer]:
    c = bootstrap(var_dir=tmp_path)
    yield c
    c.close()


def test_help_exits_cleanly(container: DependencyContainer) -> None:
    with pytest.raises(SystemExit) as exc_info:
        run(container, ["--help"])
    assert exc_info.value.code == 0


def test_version_exits_cleanly(container: DependencyContainer) -> None:
    with pytest.raises(SystemExit) as exc_info:
        run(container, ["--version"])
    assert exc_info.value.code == 0


def test_no_arguments_returns_zero(container: DependencyContainer) -> None:
    assert run(container, []) == 0
