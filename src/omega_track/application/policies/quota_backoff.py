# Copyright (c) 2026 kraynux - Licence MIT
"""Backoff generique par source a cle (plan de dev §12 "mecanisme
quota/cache/backoff generique, reutilisable par n'importe quelle
source") - persiste via SettingsRepository (deja un port cle/valeur JSON
generique, D-008) plutot qu'une nouvelle table SQLite : un TrackRun est
un nouveau processus CLI a chaque invocation (Phase 10 l'a deja etabli),
donc "backoff respecte sur un run suivant" (critere de sortie §12) exige
un etat qui survit au processus - settings.json suffit, pas besoin d'un
schema dedie pour une seule paire cle/horodatage par source.

Fichier separe d'execution_budget.py (pas fusionne malgre la mention du
plan "execution_budget.py centralise ce calcul") : le budget par IP
(quel IP enrichir) et le backoff temporel par source (quand retenter)
sont deux preoccupations distinctes, les melanger aurait rendu les deux
fichiers plus difficiles a lire independamment - meme discipline que
report_builder.py/export_orchestrator.py geardes separes."""
from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timedelta

from omega_track.ports.repositories.settings_repository import SettingsRepository

DEFAULT_BACKOFF = timedelta(hours=1)
"""Politique defensive interne a TRACK (pas un chiffre officiel du
fournisseur, docs/DATA_SOURCES.md ne documente aucun quota chiffre fiable
a coder en dur) : delai raisonnable avant de retenter une source ayant
signale un quota depasse, evite de marteler un service tiers en boucle
sur des `track run` rapproches."""


def backoff_setting_key(source_name: str) -> str:
    return f"quota_backoff::{source_name}"


def is_in_backoff(
    *, settings_repository: SettingsRepository, source_name: str, now: Callable[[], datetime]
) -> bool:
    raw = settings_repository.get(backoff_setting_key(source_name), "")
    if not raw:
        return False
    return datetime.fromisoformat(raw) > now()


def record_quota_exceeded(
    *,
    settings_repository: SettingsRepository,
    source_name: str,
    now: Callable[[], datetime],
    backoff: timedelta = DEFAULT_BACKOFF,
) -> None:
    settings_repository.set(backoff_setting_key(source_name), (now() + backoff).isoformat())
