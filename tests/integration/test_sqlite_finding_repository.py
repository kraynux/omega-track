# Copyright (c) 2026 kraynux - Licence MIT
"""Persistance et relecture de findings polymorphes (critere de sortie
Phase 4) - plusieurs finding_type/payload de formes differentes dans le
meme run, avec preuves multiples conservees."""
import sqlite3
from datetime import datetime, timezone

from omega_track.core.enums import ConfidenceLevel
from omega_track.domain.entities.findings.base import Finding
from omega_track.domain.entities.relation import Relation, RelationType
from omega_track.domain.value_objects.collection_mode import CollectionMode
from omega_track.domain.value_objects.evidence import Evidence
from omega_track.domain.value_objects.identifiers import (
    FindingId,
    ModuleRunId,
    RelationId,
    TrackRunId,
)
from omega_track.infrastructure.repositories.sqlite.finding_repository import (
    SqliteFindingRepository,
)

_NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)
_RUN = TrackRunId("run-1")


def _finding(finding_type: str, payload: dict, finding_id: str = "f1") -> Finding:
    return Finding(
        id=FindingId(finding_id), track_run_id=_RUN, module_run_id=ModuleRunId("mr-1"),
        finding_type=finding_type, payload=payload, confidence=ConfidenceLevel.VERIFIED,
        collection_mode=CollectionMode.ACTIVE_LIGHT, source_name="dns",
        observed_at=_NOW, collected_at=_NOW,
    )


def test_polymorphic_findings_round_trip_distinct_payload_shapes(connection: sqlite3.Connection) -> None:
    repo = SqliteFindingRepository(connection)
    dns_finding = _finding("dns.a_record", {"value": "203.0.113.10"}, "f1")
    path_finding = _finding("path.hop", {"sequence": 1, "rtt_ms": 12.5, "hops": ["a", "b"]}, "f2")
    identity_finding = _finding("identity.registrar", {"name": "Example Registrar", "iana_id": 123}, "f3")

    repo.save_findings([dns_finding, path_finding, identity_finding])

    findings = repo.list_findings_for_run(_RUN)
    by_type = {f.finding_type: f.payload for f in findings}
    assert by_type["dns.a_record"] == {"value": "203.0.113.10"}
    assert by_type["path.hop"] == {"sequence": 1, "rtt_ms": 12.5, "hops": ["a", "b"]}
    assert by_type["identity.registrar"] == {"name": "Example Registrar", "iana_id": 123}


def test_multiple_evidences_preserved_across_save_and_reload(connection: sqlite3.Connection) -> None:
    repo = SqliteFindingRepository(connection)
    finding = _finding("certificate.observed", {"san": "example.com"})
    finding.add_evidence(Evidence(source="crt.sh", collected_at=_NOW, reference="log-a"))
    finding.add_evidence(Evidence(source="crt.sh", collected_at=_NOW, reference="log-b"))
    repo.save_findings([finding])

    reloaded = repo.list_findings_for_run(_RUN)[0]
    assert len(reloaded.evidences) == 2
    assert {e.reference for e in reloaded.evidences} == {"log-a", "log-b"}


def test_resave_updates_confidence_in_place(connection: sqlite3.Connection) -> None:
    repo = SqliteFindingRepository(connection)
    finding = _finding("certificate.observed", {"san": "example.com"})
    repo.save_findings([finding])

    finding.confidence = ConfidenceLevel.CORROBORATED
    repo.save_findings([finding])

    reloaded = repo.list_findings_for_run(_RUN)
    assert len(reloaded) == 1
    assert reloaded[0].confidence == ConfidenceLevel.CORROBORATED


def test_relations_round_trip_with_evidences(connection: sqlite3.Connection) -> None:
    repo = SqliteFindingRepository(connection)
    relation = Relation(
        id=RelationId("rel-1"), track_run_id=_RUN, source_entity_ref="example.com",
        target_entity_ref="203.0.113.10", relation_type=RelationType.RESOLVES_TO,
        confidence=ConfidenceLevel.VERIFIED,
    )
    relation.evidences.append(Evidence(source="dns", collected_at=_NOW))
    repo.save_relations([relation])

    reloaded = repo.list_relations_for_run(_RUN)
    assert len(reloaded) == 1
    assert reloaded[0].relation_type == RelationType.RESOLVES_TO
    assert len(reloaded[0].evidences) == 1


def test_findings_and_relations_scoped_to_their_own_run(connection: sqlite3.Connection) -> None:
    repo = SqliteFindingRepository(connection)
    other_run = TrackRunId("run-2")
    repo.save_findings([
        _finding("dns.a_record", {"value": "1.1.1.1"}, "f1"),
        Finding(
            id=FindingId("f-other"), track_run_id=other_run, module_run_id=ModuleRunId("mr-2"),
            finding_type="dns.a_record", payload={"value": "2.2.2.2"},
            confidence=ConfidenceLevel.VERIFIED, collection_mode=CollectionMode.ACTIVE_LIGHT,
            source_name="dns", observed_at=_NOW, collected_at=_NOW,
        ),
    ])
    assert len(repo.list_findings_for_run(_RUN)) == 1
    assert len(repo.list_findings_for_run(other_run)) == 1


def test_delete_for_run_removes_only_findings_and_relations_of_that_run(connection: sqlite3.Connection) -> None:
    repo = SqliteFindingRepository(connection)
    other_run = TrackRunId("run-2")
    repo.save_findings([
        _finding("dns.a_record", {"value": "1.1.1.1"}, "f1"),
        Finding(
            id=FindingId("f-other"), track_run_id=other_run, module_run_id=ModuleRunId("mr-2"),
            finding_type="dns.a_record", payload={"value": "2.2.2.2"},
            confidence=ConfidenceLevel.VERIFIED, collection_mode=CollectionMode.ACTIVE_LIGHT,
            source_name="dns", observed_at=_NOW, collected_at=_NOW,
        ),
    ])
    repo.save_relations([
        Relation(
            id=RelationId("rel-1"), track_run_id=_RUN, source_entity_ref="a", target_entity_ref="b",
            relation_type=RelationType.RESOLVES_TO, confidence=ConfidenceLevel.VERIFIED,
        ),
        Relation(
            id=RelationId("rel-2"), track_run_id=other_run, source_entity_ref="c", target_entity_ref="d",
            relation_type=RelationType.RESOLVES_TO, confidence=ConfidenceLevel.VERIFIED,
        ),
    ])

    repo.delete_for_run(_RUN)

    assert repo.list_findings_for_run(_RUN) == []
    assert repo.list_relations_for_run(_RUN) == []
    assert len(repo.list_findings_for_run(other_run)) == 1
    assert len(repo.list_relations_for_run(other_run)) == 1
