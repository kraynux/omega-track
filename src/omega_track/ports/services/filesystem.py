# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat d'acces au systeme de fichiers (plan de dev, Phase 3) - la
seule I/O disque autorisee hors SQLite, utilisee par le telechargement de
bases GeoIP (Phase 5) et les exporteurs fichiers (Phase 8)."""
from __future__ import annotations

from pathlib import Path
from typing import Protocol


class Filesystem(Protocol):
    def read_bytes(self, path: Path) -> bytes: ...

    def write_bytes(self, path: Path, content: bytes) -> None: ...

    def exists(self, path: Path) -> bool: ...

    def compute_checksum(self, path: Path) -> str:
        """SHA-256 hexdigest - verification d'integrite des bases GeoIP
        telechargees (Phase 5, "Regles d'update")."""
        ...
