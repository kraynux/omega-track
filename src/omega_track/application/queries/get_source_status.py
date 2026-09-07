# Copyright (c) 2026 kraynux - Licence MIT
"""Use case GetSourceStatus (plan de dev §12 `source list`) - etat
courant d'une source a cle : cle configuree ou non, backoff actif ou non
(application/policies/quota_backoff.py) - jamais le contenu de la cle
elle-meme (regle transverse docs/DATA_SOURCES.md : "aucune cle API ne
doit jamais apparaitre... dans les... diagnostics")."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from omega_track.application.policies.quota_backoff import backoff_setting_key, is_in_backoff
from omega_track.ports.repositories.settings_repository import SettingsRepository
from omega_track.ports.services.secret_store import SecretStore


@dataclass(frozen=True, slots=True)
class SourceStatusView:
    source_name: str
    key_configured: bool
    in_backoff: bool
    backoff_until: datetime | None


def get_source_status(
    *,
    secret_store: SecretStore,
    settings_repository: SettingsRepository,
    source_name: str,
    now: Callable[[], datetime],
) -> SourceStatusView:
    key_configured = bool(secret_store.get_secret(f"{source_name}_api_key"))
    backoff_raw = settings_repository.get(backoff_setting_key(source_name), "")
    backoff_until = datetime.fromisoformat(backoff_raw) if backoff_raw else None
    return SourceStatusView(
        source_name=source_name,
        key_configured=key_configured,
        in_backoff=is_in_backoff(settings_repository=settings_repository, source_name=source_name, now=now),
        backoff_until=backoff_until,
    )
