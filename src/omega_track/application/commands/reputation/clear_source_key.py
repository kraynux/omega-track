# Copyright (c) 2026 kraynux - Licence MIT
"""Use case ClearSourceKey (plan de dev §12) - retire une cle deja
configuree, idempotent (retirer une cle deja absente ne leve jamais,
meme discipline que delete_targets.py, Phase 9)."""
from __future__ import annotations

from omega_track.application.exceptions import UnknownReputationSourceError
from omega_track.application.queries.get_source_disclosure import (
    list_known_reputation_sources,
    secret_name_for,
)
from omega_track.ports.services.secret_store import SecretStore


def clear_source_key(*, secret_store: SecretStore, source_name: str) -> None:
    if source_name not in list_known_reputation_sources():
        raise UnknownReputationSourceError(source_name)
    secret_store.delete_secret(secret_name_for(source_name))
