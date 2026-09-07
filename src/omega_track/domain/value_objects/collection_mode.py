# Copyright (c) 2026 kraynux - Licence MIT
"""Niveau de collecte (plan de dev §1.3/§4.2) - rend la nature de chaque
action explicite, condition de confidentialite du produit (docs/PRIVACY.md)."""
from __future__ import annotations

from enum import Enum


class CollectionMode(str, Enum):
    OFFLINE = "offline"
    """Validation de cible, lecture GeoIP locale, correlations sur donnees
    deja stockees, exports - aucun reseau."""
    PASSIVE_PUBLIC = "passive_public"
    """RDAP, DNS public, CT logs, archives publiques, BGP/RDAP publics."""
    ACTIVE_LIGHT = "active_light"
    """Resolution DNS, reverse DNS, traceroute (D-008 : seule action
    reseau active du MVP), MTR optionnel."""
    API_KEY = "api_key"
    """Fournisseurs qui exigent une cle ou appliquent des quotas, actives
    uniquement apres configuration explicite (Phase 12)."""
