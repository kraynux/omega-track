# Copyright (c) 2026 kraynux - Licence MIT
"""Implementation SQLite du port FindingRepository - findings et
relations d'un TrackRun, chacun avec ses preuves multiples serialisees
en JSON (`evidences_json` - voir schema.py, ecart assume par rapport a
l'esquisse initiale du plan qui ne prevoyait qu'une reference unique)."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime

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
from omega_track.infrastructure.exceptions import StorageError
from omega_track.shared.i18n import _


def _evidences_to_json(evidences: list[Evidence]) -> str:
    return json.dumps([
        {
            "source": e.source,
            "collected_at": e.collected_at.isoformat(),
            "reference": e.reference,
            "fingerprint": e.fingerprint,
            "method": e.method,
        }
        for e in evidences
    ])


def _evidences_from_json(raw: str) -> list[Evidence]:
    return [
        Evidence(
            source=item["source"],
            collected_at=datetime.fromisoformat(item["collected_at"]),
            reference=item["reference"],
            fingerprint=item["fingerprint"],
            method=item["method"],
        )
        for item in json.loads(raw)
    ]


class SqliteFindingRepository:
    """Implemente ports/repositories/finding_repository.py::FindingRepository."""

    def __init__(self, connection: sqlite3.Connection) -> None:
        self._connection = connection

    def save_findings(self, findings: list[Finding]) -> None:
        try:
            for finding in findings:
                self._connection.execute(
                    """
                    INSERT INTO findings
                        (id, track_run_id, module_run_id, finding_type, payload_json,
                         confidence, collection_mode, source_name, observed_at, collected_at,
                         evidences_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        payload_json = excluded.payload_json,
                        confidence = excluded.confidence,
                        evidences_json = excluded.evidences_json
                    """,
                    (
                        finding.id,
                        finding.track_run_id,
                        finding.module_run_id,
                        finding.finding_type,
                        json.dumps(finding.payload),
                        finding.confidence.value,
                        finding.collection_mode.value,
                        finding.source_name,
                        finding.observed_at.isoformat(),
                        finding.collected_at.isoformat(),
                        _evidences_to_json(finding.evidences),
                    ),
                )
            self._connection.commit()
        except sqlite3.Error as exc:
            raise StorageError(_("échec de sauvegarde des findings")) from exc

    def save_relations(self, relations: list[Relation]) -> None:
        try:
            for relation in relations:
                self._connection.execute(
                    """
                    INSERT INTO relations
                        (id, track_run_id, source_entity_ref, target_entity_ref,
                         relation_type, confidence, evidences_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        confidence = excluded.confidence,
                        evidences_json = excluded.evidences_json
                    """,
                    (
                        relation.id,
                        relation.track_run_id,
                        relation.source_entity_ref,
                        relation.target_entity_ref,
                        relation.relation_type.value,
                        relation.confidence.value,
                        _evidences_to_json(relation.evidences),
                    ),
                )
            self._connection.commit()
        except sqlite3.Error as exc:
            raise StorageError(_("échec de sauvegarde des relations")) from exc

    def list_findings_for_run(self, track_run_id: TrackRunId) -> list[Finding]:
        rows = self._connection.execute(
            "SELECT * FROM findings WHERE track_run_id = ? ORDER BY collected_at", (track_run_id,)
        ).fetchall()
        return [self._row_to_finding(row) for row in rows]

    def list_relations_for_run(self, track_run_id: TrackRunId) -> list[Relation]:
        rows = self._connection.execute(
            "SELECT * FROM relations WHERE track_run_id = ?", (track_run_id,)
        ).fetchall()
        return [self._row_to_relation(row) for row in rows]

    def delete_for_run(self, track_run_id: TrackRunId) -> None:
        try:
            self._connection.execute("DELETE FROM findings WHERE track_run_id = ?", (track_run_id,))
            self._connection.execute("DELETE FROM relations WHERE track_run_id = ?", (track_run_id,))
            self._connection.commit()
        except sqlite3.Error as exc:
            raise StorageError(_("échec de suppression des findings/relations")) from exc

    @staticmethod
    def _row_to_finding(row: sqlite3.Row) -> Finding:
        return Finding(
            id=FindingId(row["id"]),
            track_run_id=TrackRunId(row["track_run_id"]),
            module_run_id=ModuleRunId(row["module_run_id"]),
            finding_type=row["finding_type"],
            payload=json.loads(row["payload_json"]),
            confidence=ConfidenceLevel(row["confidence"]),
            collection_mode=CollectionMode(row["collection_mode"]),
            source_name=row["source_name"],
            observed_at=datetime.fromisoformat(row["observed_at"]),
            collected_at=datetime.fromisoformat(row["collected_at"]),
            evidences=_evidences_from_json(row["evidences_json"]),
        )

    @staticmethod
    def _row_to_relation(row: sqlite3.Row) -> Relation:
        return Relation(
            id=RelationId(row["id"]),
            track_run_id=TrackRunId(row["track_run_id"]),
            source_entity_ref=row["source_entity_ref"],
            target_entity_ref=row["target_entity_ref"],
            relation_type=RelationType(row["relation_type"]),
            confidence=ConfidenceLevel(row["confidence"]),
            evidences=_evidences_from_json(row["evidences_json"]),
        )
