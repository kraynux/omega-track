# Copyright (c) 2026 kraynux - Licence MIT
"""Use case ConfigureSourceKey (plan de dev §12 `source configure
<name> <key>`) - meme discipline que configure_provider.py::
configure_maxmind_credentials (Phase 5) : valide non-vide, ecrit dans
SecretStore, jamais dans settings.json (regle transverse
docs/DATA_SOURCES.md). Ne fait AUCUNE verification "l'avertissement a-
t-il ete affiche" - c'est la responsabilite de l'appelant (CLI/TUI)
d'afficher get_source_disclosure.py avant chaque appel, voir son
docstring."""
from __future__ import annotations

from omega_track.application.exceptions import ApiKeyMissingError, UnknownReputationSourceError
from omega_track.application.queries.get_source_disclosure import (
    list_known_reputation_sources,
    secret_name_for,
)
from omega_track.ports.services.secret_store import SecretStore


def configure_source_key(*, secret_store: SecretStore, source_name: str, api_key: str) -> None:
    if source_name not in list_known_reputation_sources():
        raise UnknownReputationSourceError(source_name)
    cleaned = api_key.strip()
    if not cleaned:
        raise ApiKeyMissingError(source_name)
    secret_store.set_secret(secret_name_for(source_name), cleaned)
