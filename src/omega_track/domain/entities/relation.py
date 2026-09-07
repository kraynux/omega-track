# Copyright (c) 2026 kraynux - Licence MIT
"""Relations et preuves entre entites, clusters, noeuds/aretes de graphe
(plan de dev §4.1). Entite de premier niveau, pas une famille de finding
(corrige : §4.3 la listait a tort dans findings/, alors que ARBORESCENCE.md
et §7 la placent tous deux comme fichier frere de findings/ - une Relation
porte sur une PAIRE d'entites, jamais une seule, forme suffisamment
differente d'un Finding pour justifier une table SQL separee (Phase 4) et
donc un fichier separe ici).

Les types de relation et leurs regles de confiance sont figes par D-011
(angle mort 2, voir OMEGA_TRACK_PLAN_DEVELOPPEMENT.md) - appliquees par
domain/services/correlation_engine.py, jamais construites au hasard ici."""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

from omega_track.core.enums import ConfidenceLevel
from omega_track.domain.value_objects.evidence import Evidence
from omega_track.domain.value_objects.identifiers import RelationId, TrackRunId


class RelationType(str, Enum):
    RESOLVES_TO = "resolves_to"
    """Domaine -> IP (resolution DNS directe) - VERIFIED (D-011)."""
    CERTIFICATE_SAN = "certificate_san"
    """Certificat (SAN observe via CT log) -> domaine - DECLARED, puis
    CORROBORATED si observe par 2+ CT logs distincts (D-011)."""
    SHARED_NAMESERVER = "shared_nameserver"
    """Nameserver commun entre deux domaines - INFERRED (D-011, signal
    faible seul)."""
    SHARED_ASN = "shared_asn"
    """ASN commun entre deux IPs - **jamais construite automatiquement**
    (D-011) : ce type n'existe que pour une Relation deja escaladee a
    CORROBORATED par un second signal independant, jamais pour le signal
    ASN seul (qui reste un Finding brut, voir findings/network.py)."""


@dataclass
class Relation:
    id: RelationId
    track_run_id: TrackRunId
    source_entity_ref: str
    """Reference opaque vers l'entite source (IP/domaine observe) - pas
    necessairement un Target enregistre, voir schema `relations` (Phase 4)."""
    target_entity_ref: str
    relation_type: RelationType
    confidence: ConfidenceLevel
    evidences: list[Evidence] = field(default_factory=list)


@dataclass
class Cluster:
    """Regroupement d'entites liees (plan de dev §4.1) - construit par
    domain/services/cluster_identifier.py a partir des Relation d'un
    TrackRun, jamais persiste independamment (recalcule a la lecture,
    meme discipline que D-011 de FOLD : ne pas stocker un cache derive
    d'une donnee deja reconstructible)."""

    id: str
    member_refs: set[str]
    label: str | None = None
