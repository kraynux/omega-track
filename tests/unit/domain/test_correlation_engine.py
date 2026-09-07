# Copyright (c) 2026 kraynux - Licence MIT
"""Classification de relations (D-011, angle mort 2) : domaine resout
vers IP (VERIFIED), certificat contient SAN (DECLARED/CORROBORATED), NS
commun (INFERRED), ASN commun (jamais automatique)."""
from omega_track.core.enums import ConfidenceLevel
from omega_track.domain.entities.relation import RelationType
from omega_track.domain.services.correlation_engine import (
    escalate_if_corroborated,
    infer_certificate_san_relation,
    infer_resolution_relation,
    infer_shared_nameserver_relation,
)
from omega_track.domain.value_objects.identifiers import TrackRunId

_RUN = TrackRunId("run-1")


def _id_factory_counter():
    counter = iter(range(1, 1000))

    def factory() -> str:
        return f"id-{next(counter)}"

    return factory


def test_domain_resolves_to_ip_is_verified() -> None:
    relation = infer_resolution_relation(_RUN, "example.com", "203.0.113.10", id_factory=_id_factory_counter())
    assert relation.relation_type == RelationType.RESOLVES_TO
    assert relation.confidence == ConfidenceLevel.VERIFIED


def test_certificate_san_single_ct_log_is_declared() -> None:
    relation = infer_certificate_san_relation(
        _RUN, "cert-abc", "example.com", distinct_ct_log_count=1, id_factory=_id_factory_counter()
    )
    assert relation.relation_type == RelationType.CERTIFICATE_SAN
    assert relation.confidence == ConfidenceLevel.DECLARED


def test_certificate_san_two_distinct_ct_logs_is_corroborated() -> None:
    relation = infer_certificate_san_relation(
        _RUN, "cert-abc", "example.com", distinct_ct_log_count=2, id_factory=_id_factory_counter()
    )
    assert relation.confidence == ConfidenceLevel.CORROBORATED


def test_shared_nameserver_is_inferred() -> None:
    relation = infer_shared_nameserver_relation(
        _RUN, "example.com", "example.net", id_factory=_id_factory_counter()
    )
    assert relation.relation_type == RelationType.SHARED_NAMESERVER
    assert relation.confidence == ConfidenceLevel.INFERRED


def test_shared_asn_never_built_automatically() -> None:
    """Pas de fonction infer_shared_asn_relation() : un ASN commun seul
    reste un Finding brut (domain/entities/findings/network.py), jamais
    une Relation automatique (D-011)."""
    import omega_track.domain.services.correlation_engine as module

    assert not hasattr(module, "infer_shared_asn_relation")


def test_two_independent_inferred_signals_escalate_to_corroborated() -> None:
    id_factory = _id_factory_counter()
    nameserver_relation = infer_shared_nameserver_relation(
        _RUN, "example.com", "example.net", id_factory=id_factory
    )
    # Un second signal INFERRED independant sur la meme paire mais d'un
    # type different (simule ici par une relation deja existante) doit
    # faire passer le candidat a CORROBORATED.
    from omega_track.domain.entities.relation import Relation
    from omega_track.domain.entities.relation import RelationType as RT

    other_signal = Relation(
        id="other", track_run_id=_RUN, source_entity_ref="example.com",
        target_entity_ref="example.net", relation_type=RT.RESOLVES_TO,
        confidence=ConfidenceLevel.INFERRED,
    )
    escalated = escalate_if_corroborated([other_signal], nameserver_relation)
    assert escalated.confidence == ConfidenceLevel.CORROBORATED


def test_single_inferred_signal_not_escalated() -> None:
    id_factory = _id_factory_counter()
    relation = infer_shared_nameserver_relation(_RUN, "example.com", "example.net", id_factory=id_factory)
    escalated = escalate_if_corroborated([], relation)
    assert escalated.confidence == ConfidenceLevel.INFERRED


def test_verified_relation_never_escalated_or_downgraded() -> None:
    id_factory = _id_factory_counter()
    relation = infer_resolution_relation(_RUN, "example.com", "203.0.113.10", id_factory=id_factory)
    escalated = escalate_if_corroborated([], relation)
    assert escalated.confidence == ConfidenceLevel.VERIFIED
