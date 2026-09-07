# Copyright (c) 2026 kraynux - Licence MIT
"""Resultat brut d'un collecteur (Phase 3) - absent de ARBORESCENCE.md/du
plan de dev, ajoute par necessite : un port de collecte ne connait ni le
TrackRunId ni le ModuleRunId (il collecte pour UNE cible, sans savoir
dans quel contexte d'execution il est appele) - il ne peut donc pas
construire un `Finding` complet lui-meme (voir domain/entities/findings/
base.py). L'orchestrateur (Phase 7) transforme chaque CollectedRecord en
Finding en y ajoutant le contexte d'execution."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from omega_track.core.enums import ConfidenceLevel


@dataclass(frozen=True, slots=True)
class CollectedRecord:
    finding_type: str
    """Voir domain/entities/findings/*.py pour les valeurs valides."""
    payload: dict[str, Any]
    confidence: ConfidenceLevel
    source_name: str
    observed_at: datetime
    evidence_reference: str | None = field(default=None)
