# Copyright (c) 2026 kraynux - Licence MIT
"""DOT et Mermaid partagent le meme jeu de donnees (le graphe de
relations) - un seul fichier de test pour les deux formats, meme
convention que le partage de mermaid_file_exporter.py::build_mermaid_graph
par l'export HTML."""
from __future__ import annotations

from datetime import datetime, timezone

from omega_track.core.enums import ConfidenceLevel
from omega_track.domain.entities.identity_report import IdentityReport
from omega_track.domain.entities.relation import Relation, RelationType
from omega_track.domain.entities.track_profile import TrackProfile
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.domain.value_objects.export_options import ExportOptions
from omega_track.domain.value_objects.identifiers import (
    RelationId,
    TargetId,
    TrackProfileId,
    TrackRunId,
)
from omega_track.infrastructure.exporters.graphviz_dot_exporter import GraphvizDotExporter
from omega_track.infrastructure.exporters.mermaid_file_exporter import (
    MermaidFileExporter,
    build_mermaid_graph,
)

_NOW = datetime(2026, 9, 6, tzinfo=timezone.utc)


def _report(relations: list[Relation]) -> IdentityReport:
    profile = TrackProfile(
        id=TrackProfileId("profile-1"), name="default", modules={"dns"}, created_at=_NOW, updated_at=_NOW
    )
    return IdentityReport(
        track_run_id=TrackRunId("run-1"), target_id=TargetId("target-1"),
        target_value=DomainName.parse("example.com"), profile_snapshot=profile, generated_at=_NOW,
        relations=relations,
    )


def _relation() -> Relation:
    return Relation(
        id=RelationId("rel-1"), track_run_id=TrackRunId("run-1"), source_entity_ref="example.com",
        target_entity_ref="1.1.1.1", relation_type=RelationType.RESOLVES_TO, confidence=ConfidenceLevel.VERIFIED,
    )


def test_dot_export_contains_nodes_and_labeled_edge() -> None:
    dot = GraphvizDotExporter().export(_report([_relation()]), ExportOptions()).decode("utf-8")
    assert dot.startswith("digraph omega_track {")
    assert '"example.com";' in dot
    assert '"1.1.1.1";' in dot
    assert '"example.com" -> "1.1.1.1" [label="resolves_to (verified)"];' in dot
    assert dot.strip().endswith("}")


def test_dot_export_with_no_relations_has_no_edges() -> None:
    dot = GraphvizDotExporter().export(_report([]), ExportOptions()).decode("utf-8")
    assert "->" not in dot


def test_mermaid_graph_uses_sequential_node_ids() -> None:
    graph = build_mermaid_graph(_report([_relation()]))
    assert graph.startswith("graph TD")
    # ordre alphabetique des refs : "1.1.1.1" < "example.com"
    assert 'n0["1.1.1.1"]' in graph
    assert 'n1["example.com"]' in graph
    # regression Phase 12 : le label d'arete doit etre entoure de
    # guillemets ("...") des qu'il contient des parentheses, sinon mermaid.js
    # 10.9.8 refuse de parser le graphe ("Syntax error in text")
    assert 'n1 -->|"resolves_to (verified)"| n0' in graph


def test_mermaid_exporter_matches_build_mermaid_graph() -> None:
    report = _report([_relation()])
    exported = MermaidFileExporter().export(report, ExportOptions()).decode("utf-8")
    assert exported == build_mermaid_graph(report)
