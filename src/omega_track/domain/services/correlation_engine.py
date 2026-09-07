# Copyright (c) 2026 kraynux - Licence MIT
"""Moteur de correlation - regles figees par D-011 (angle mort 2, voir
OMEGA_TRACK_PLAN_DEVELOPPEMENT.md), pures, sans I/O.

Volontairement absent : un constructeur direct de Relation(SHARED_ASN).
Un ASN commun entre deux IPs ne devient JAMAIS une relation automatique
(trop bruyant sur tout grand hebergeur/cloud) - il reste un Finding brut
(voir domain/entities/findings/network.py::NetworkFindingType.ASN) et ne
peut devenir une Relation SHARED_ASN qu'en passant par
`escalate_if_corroborated`, jamais par un raccourci a un seul appel qui
rendrait trop facile de la construire par erreur."""
from __future__ import annotations

from dataclasses import replace

from omega_track.core.enums import ConfidenceLevel
from omega_track.domain.entities.relation import Relation, RelationType
from omega_track.domain.value_objects.identifiers import RelationId, TrackRunId
from omega_track.shared.typing import IdFactory


def infer_resolution_relation(
    track_run_id: TrackRunId, domain_ref: str, ip_ref: str, *, id_factory: IdFactory
) -> Relation:
    """Domaine -> IP (resolution DNS directe) : VERIFIED (D-011)."""
    return Relation(
        id=RelationId(id_factory()),
        track_run_id=track_run_id,
        source_entity_ref=domain_ref,
        target_entity_ref=ip_ref,
        relation_type=RelationType.RESOLVES_TO,
        confidence=ConfidenceLevel.VERIFIED,
    )


def infer_certificate_san_relation(
    track_run_id: TrackRunId,
    certificate_ref: str,
    domain_ref: str,
    *,
    distinct_ct_log_count: int,
    id_factory: IdFactory,
) -> Relation:
    """Certificat (SAN observe via CT log) -> domaine : DECLARED (source
    publique tierce, pas une connexion TLS verifiee par TRACK), passe a
    CORROBORATED si observe par 2+ CT logs distincts (D-011)."""
    confidence = (
        ConfidenceLevel.CORROBORATED if distinct_ct_log_count >= 2 else ConfidenceLevel.DECLARED
    )
    return Relation(
        id=RelationId(id_factory()),
        track_run_id=track_run_id,
        source_entity_ref=certificate_ref,
        target_entity_ref=domain_ref,
        relation_type=RelationType.CERTIFICATE_SAN,
        confidence=confidence,
    )


def infer_shared_nameserver_relation(
    track_run_id: TrackRunId, domain_a_ref: str, domain_b_ref: str, *, id_factory: IdFactory
) -> Relation:
    """Nameserver commun entre deux domaines : INFERRED (D-011, signal
    faible seul - courant sur hebergement mutualise/registrar par defaut)."""
    return Relation(
        id=RelationId(id_factory()),
        track_run_id=track_run_id,
        source_entity_ref=domain_a_ref,
        target_entity_ref=domain_b_ref,
        relation_type=RelationType.SHARED_NAMESERVER,
        confidence=ConfidenceLevel.INFERRED,
    )


def escalate_if_corroborated(existing_relations: list[Relation], candidate: Relation) -> Relation:
    """Deux signaux INFERRED independants sur la meme paire d'entites ->
    CORROBORATED, jamais au-dela sans preuve directe (D-011). Ne fait
    rien si `candidate` n'est pas INFERRED - VERIFIED/DECLARED restent
    hors de portee du moteur de correlation, qui ne fait qu'inferer."""
    if candidate.confidence != ConfidenceLevel.INFERRED:
        return candidate

    candidate_pair = {candidate.source_entity_ref, candidate.target_entity_ref}
    has_independent_inferred_signal = any(
        existing.confidence == ConfidenceLevel.INFERRED
        and existing.relation_type != candidate.relation_type
        and {existing.source_entity_ref, existing.target_entity_ref} == candidate_pair
        for existing in existing_relations
    )
    if has_independent_inferred_signal:
        return replace(candidate, confidence=ConfidenceLevel.CORROBORATED)
    return candidate
