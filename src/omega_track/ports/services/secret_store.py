# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat de stockage des secrets (cles API, Phase 12) - hors de la base
de resultats, trousseau systeme si disponible sinon fichier de
configuration protege (plan de dev §2.2/docs/PRIVACY.md §1)."""
from __future__ import annotations

from typing import Protocol


class SecretStore(Protocol):
    def get_secret(self, key: str) -> str | None: ...

    def set_secret(self, key: str, value: str) -> None: ...

    def delete_secret(self, key: str) -> None: ...
