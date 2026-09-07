# Copyright (c) 2026 kraynux - Licence MIT
"""Localisation geographique approximative (plan de dev §4.2) - jamais
une position exacte, toujours qualifiee par sa source et sa precision."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class GeoLocation:
    country: str | None = None
    region: str | None = None
    city: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    timezone: str | None = None
    precision: str | None = None
    """Ex. 'city'/'region'/'country' selon ce que la base source garantit -
    jamais suppose 'city' par defaut."""
    source: str | None = None
    """Nom du fournisseur GeoIP ayant produit cette localisation (ex.
    'dbip', 'maxmind') - necessaire pour l'attribution (docs/DATA_SOURCES.md)."""
