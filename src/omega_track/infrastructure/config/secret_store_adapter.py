# Copyright (c) 2026 kraynux - Licence MIT
"""Implementation fichier du port SecretStore (Phase 5) - pas de
trousseau systeme (aucun precedent dans la suite) : fichier JSON dedie,
permissions 0600, distinct de settings.json pour ne jamais melanger
secrets et reglages non sensibles. Coherent avec docs/PRIVACY.md §1:
pas de chiffrement applicatif, la protection releve des permissions
filesystem, comme le reste de la base locale de l'outil."""
from __future__ import annotations

import json
import os
from pathlib import Path


class FileSecretStore:
    """Implemente ports/services/secret_store.py::SecretStore."""

    def __init__(self, path: Path) -> None:
        self._path = path

    def get_secret(self, key: str) -> str | None:
        return self._read().get(key)

    def set_secret(self, key: str, value: str) -> None:
        data = self._read()
        data[key] = value
        self._write(data)

    def delete_secret(self, key: str) -> None:
        data = self._read()
        if key in data:
            del data[key]
            self._write(data)

    def _read(self) -> dict[str, str]:
        if not self._path.exists():
            return {}
        return dict(json.loads(self._path.read_text(encoding="utf-8")))

    def _write(self, data: dict[str, str]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        os.chmod(self._path, 0o600)
