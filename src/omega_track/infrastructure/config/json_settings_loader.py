# Copyright (c) 2026 kraynux - Licence MIT
"""Implementation JSON du port SettingsRepository (reexport de
omega_lib.ports.settings_store.SettingsStore, voir ports/repositories/
settings_repository.py) - copiee verbatim depuis CHECK (D-007) :
`settings.json`, JSON, pas TOML (tranche, plan de dev Phase 4)."""
from __future__ import annotations

import json
from pathlib import Path


class JsonSettingsRepository:
    """Implemente ports/repositories/settings_repository.py::SettingsRepository."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def get(self, key: str, default: str | None = None) -> str | None:
        return self.all().get(key, default)

    def set(self, key: str, value: str) -> None:
        data = self.all()
        data[key] = value
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    def all(self) -> dict[str, str]:
        if not self._path.exists():
            return {}
        return dict(json.loads(self._path.read_text(encoding="utf-8")))
