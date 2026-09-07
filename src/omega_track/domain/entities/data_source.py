# Copyright (c) 2026 kraynux - Licence MIT
"""Description d'une source externe (plan de dev §4.1) - absente de
l'arborescence initiale (ARBORESCENCE.md ne listait pas ce fichier alors
que §4.1 l'exige comme entite centrale), ajoutee ici en cohérence. Le
contenu reel (docs/DATA_SOURCES.md) reste la reference humaine ; cette
entite est la representation machine consommee par l'ecran/commande de
configuration de sources (Phase 12)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from omega_track.domain.value_objects.collection_mode import CollectionMode


@dataclass
class DataSource:
    name: str
    """Ex. 'crt.sh', 'rdap', 'dbip', 'virustotal' - voir docs/DATA_SOURCES.md."""
    collection_mode: CollectionMode
    requires_api_key: bool
    available: bool = True
    """False si desactivee/indisponible (ex. clef manquante) - distinct
    d'un echec ponctuel de collecte."""
    last_used_at: datetime | None = None
