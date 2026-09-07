# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat de correlation des logs avec un TrackRun (Phase 7) - absent de
ARBORESCENCE.md/du plan de dev, ajoute par necessite : `infrastructure/
logging/config.py` (Phase 1) anticipait deja "a appeler par
l'orchestrateur (Phase 7)" pour ses fonctions `set_current_track_run_id`/
`reset_current_track_run_id`, mais l'orchestrateur (application/) ne peut
pas importer infrastructure/ directement (Dependency Rule, import-linter
l'a reellement detecte en implementant cette phase) - ce port est le
sens autorise, `infrastructure/logging/log_correlation_adapter.py`
l'implemente. Optionnel pour TrackOrchestrator (purement observabilite,
jamais necessaire a la correction du resultat)."""
from __future__ import annotations

from typing import Protocol


class LogCorrelation(Protocol):
    def set_current_track_run_id(self, track_run_id: str) -> object: ...

    def reset_current_track_run_id(self, token: object) -> None: ...
