# Copyright (c) 2026 kraynux - Licence MIT
from omega_track.core.enums import ConfidenceLevel
from omega_track.domain.entities.relation import Relation, RelationType
from omega_track.domain.services.cluster_identifier import identify_clusters
from omega_track.domain.value_objects.identifiers import RelationId, TrackRunId

_RUN = TrackRunId("run-1")


def _relation(source: str, target: str, relation_id: str) -> Relation:
    return Relation(
        id=RelationId(relation_id), track_run_id=_RUN, source_entity_ref=source,
        target_entity_ref=target, relation_type=RelationType.RESOLVES_TO,
        confidence=ConfidenceLevel.VERIFIED,
    )


def test_connected_entities_form_one_cluster() -> None:
    relations = [_relation("a.com", "1.1.1.1", "r1"), _relation("1.1.1.1", "b.com", "r2")]
    clusters = identify_clusters(relations)
    assert len(clusters) == 1
    assert clusters[0].member_refs == {"a.com", "1.1.1.1", "b.com"}


def test_disjoint_entities_form_separate_clusters() -> None:
    relations = [_relation("a.com", "1.1.1.1", "r1"), _relation("b.com", "2.2.2.2", "r2")]
    clusters = identify_clusters(relations)
    assert len(clusters) == 2


def test_no_relations_gives_no_clusters() -> None:
    assert identify_clusters([]) == []
