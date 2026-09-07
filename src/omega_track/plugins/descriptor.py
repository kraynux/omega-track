# Copyright (c) 2026 kraynux - Licence MIT
"""Metadonnees d'un plugin (plan de dev §10 "Interface conceptuelle") -
absent de ARBORESCENCE.md, ajoute par necessite : `plugins/registry.py`
et chaque `*_plugin.py` en ont besoin des cette phase. `plugins/` est une
couche tier-2 (pair d'infrastructure/interfaces dans le contrat
import-linter "Dependency Rule") : elle peut importer domain/ports/core,
mais jamais application/ (l'inverse est vrai - voir
application/orchestrators/phases/extended_modules_phase.py, Phase 10,
qui recoit un objet satisfaisant structurellement un port existant sans
jamais importer `plugins.*` par son nom)."""
from __future__ import annotations

from dataclasses import dataclass

from omega_track.domain.value_objects.collection_mode import CollectionMode


@dataclass(frozen=True, slots=True)
class PluginDescriptor:
    name: str
    category: str
    version: str
    required_capabilities: frozenset[str]
    """Ex. 'requires_network', 'requires_api_key' (plan de dev §10)."""
    default_enabled: bool
    collection_mode: CollectionMode
    dependencies: frozenset[str]
    """Noms d'autres modules dont ce plugin depend (ex. resolution DNS
    prealable) - vide pour les plugins de la Phase 10, aucune dependance
    inter-modules reelle identifiee pour CT/archives/BGP."""
    output_finding_types: frozenset[str]
