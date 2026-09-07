# Copyright (c) 2026 kraynux - Licence MIT
"""Implementation reelle de MermaidExporter (Phase 8) - delegue a
`application/orchestrators/mermaid_graph_builder.py::build_mermaid_graph`
(Phase 11 : deplacee hors de ce fichier pour que interfaces/tui/screens/
results.py, tier 2 comme ce module, puisse produire le meme graphe sans
importer infrastructure/ - voir le docstring de mermaid_graph_builder.py).
Reutilisee telle quelle par l'export HTML (D-009 : le graphe doit etre
embarque inline dans le rapport HTML, pas seulement livre comme fichier
`.mmd` separe - lecon tiree d'OMEGA-DEEP, voir jinja2_html_exporter.py)."""
from __future__ import annotations

from omega_track.application.orchestrators.mermaid_graph_builder import build_mermaid_graph
from omega_track.domain.entities.identity_report import IdentityReport
from omega_track.domain.value_objects.export_options import ExportOptions

__all__ = ["MermaidFileExporter", "build_mermaid_graph"]


class MermaidFileExporter:
    """Implemente ports/exporters/mermaid_exporter.py::MermaidExporter."""

    def export(self, report: IdentityReport, options: ExportOptions) -> bytes:
        return build_mermaid_graph(report).encode("utf-8")
