# Copyright (c) 2026 kraynux - Licence MIT
"""Implementation reelle de GraphvizExporter (Phase 8) - fichier `.dot`
autonome du graphe de relations (noeuds = entites distinctes observees
dans les relations, aretes = relations avec leur type/confiance)."""
from __future__ import annotations

from omega_track.domain.entities.identity_report import IdentityReport
from omega_track.domain.value_objects.export_options import ExportOptions


class GraphvizDotExporter:
    """Implemente ports/exporters/graphviz_exporter.py::GraphvizExporter."""

    def export(self, report: IdentityReport, options: ExportOptions) -> bytes:
        lines = ["digraph omega_track {"]
        nodes = sorted({relation.source_entity_ref for relation in report.relations}
                       | {relation.target_entity_ref for relation in report.relations})
        for node in nodes:
            lines.append(f'  "{node}";')
        for relation in report.relations:
            label = f"{relation.relation_type.value} ({relation.confidence.value})"
            lines.append(
                f'  "{relation.source_entity_ref}" -> "{relation.target_entity_ref}" [label="{label}"];'
            )
        lines.append("}")
        return ("\n".join(lines) + "\n").encode("utf-8")
