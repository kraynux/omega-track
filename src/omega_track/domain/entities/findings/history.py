# Copyright (c) 2026 kraynux - Licence MIT
"""Famille de findings 'history' (plan de dev §4.3, Phase 10) : snapshots
publics, changements DNS/RDAP/certificats, timeline."""
from __future__ import annotations

from enum import Enum


class HistoryFindingType(str, Enum):
    ARCHIVE_SNAPSHOT = "history.archive_snapshot"
    """Wayback Machine (Phase 10) - horodate, jamais suppose refleter
    l'etat actuel de la cible."""
    FIELD_CHANGE = "history.field_change"
    """Changement detecte entre deux TrackRun de la meme cible (D-013,
    `track replay`) - construit par domain/services/timeline_builder.py."""
