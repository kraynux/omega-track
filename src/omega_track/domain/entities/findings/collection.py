# Copyright (c) 2026 kraynux - Licence MIT
"""Famille de findings 'collection' (plan de dev §4.3) : erreurs,
limites, indisponibilites et diagnostics par collecteur - jamais un
echec silencieux, toujours un fait journalise dans le rapport final."""
from __future__ import annotations

from enum import Enum


class CollectionFindingType(str, Enum):
    SOURCE_UNAVAILABLE = "collection.source_unavailable"
    QUOTA_EXCEEDED = "collection.quota_exceeded"
    NOT_EXECUTED_NO_KEY = "collection.not_executed_no_key"
    """Source a cle non configuree (Phase 12) - distinct d'un echec."""
    BUDGET_EXCEEDED = "collection.budget_exceeded"
    """IP au-dela du budget d'enrichissement (D-012) - reference le
    finding brut network.ip_observed correspondant."""
    TRACEROUTE_UNAVAILABLE = "collection.traceroute_unavailable"
    """Etat degrade nomme (D-016, angle mort 7) - binaire absent ou
    capacite insuffisante, distinct d'un hop non repondant."""
