# Copyright (c) 2026 kraynux - Licence MIT
"""Base commune de toute donnee collectee (plan de dev §4.1/§4.3).

Une seule classe `Finding` generique plutot qu'une classe par micro-donnee
(consigne explicite du plan §4.3) : `finding_type` discrimine la nature
exacte (voir les constantes des modules freres `identity.py`/`dns.py`/...),
`payload` porte les champs specifiques. Les familles ne definissent que
des identifiants de type et, quand la donnee le justifie reellement
(chemin reseau, relations), de vraies entites dediees."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from omega_track.core.enums import ConfidenceLevel
from omega_track.domain.value_objects.collection_mode import CollectionMode
from omega_track.domain.value_objects.evidence import Evidence
from omega_track.domain.value_objects.identifiers import FindingId, ModuleRunId, TrackRunId


@dataclass
class Finding:
    id: FindingId
    track_run_id: TrackRunId
    module_run_id: ModuleRunId
    finding_type: str
    """Ex. 'dns.a_record', 'identity.registrar' - voir les constantes
    *FindingType des modules de findings/ pour les valeurs valides."""
    payload: dict[str, Any]
    confidence: ConfidenceLevel
    collection_mode: CollectionMode
    source_name: str
    observed_at: datetime
    """Quand le fait etait vrai a la source (ex. date d'un enregistrement
    DNS observe) - distinct de `collected_at`."""
    collected_at: datetime
    """Quand TRACK a lui-meme effectue la collecte."""
    evidences: list[Evidence] = field(default_factory=list)

    def add_evidence(self, evidence: Evidence) -> None:
        """Deduplique sur (source, reference) - une meme source qui
        renvoie deux fois la meme preuve ne doit pas gonfler artificiellement
        le nombre d'evidences (voir Phase 2, test "deduplication d'un
        finding et conservation des preuves multiples")."""
        for existing in self.evidences:
            if existing.source == evidence.source and existing.reference == evidence.reference:
                return
        self.evidences.append(evidence)

    @property
    def distinct_sources(self) -> set[str]:
        return {e.source for e in self.evidences}
