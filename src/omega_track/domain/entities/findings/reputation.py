# Copyright (c) 2026 kraynux - Licence MIT
"""Famille de findings 'reputation' (plan de dev §4.3) : listes,
detections, reputations, verdicts et limites de source."""
from __future__ import annotations

from enum import Enum


class ReputationFindingType(str, Enum):
    BLOCKLIST_MATCH = "reputation.blocklist_match"
    VERDICT = "reputation.verdict"
    """Verdict d'un moteur tiers (ex. VirusTotal, Phase 12) - toujours
    DECLARED (jamais verifie independamment par TRACK, docs/DATA_SOURCES.md)."""
