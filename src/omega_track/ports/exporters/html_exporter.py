# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat d'export HTML (plan de dev, Phase 3/8). Le graphe de relations
Mermaid doit etre embarque inline (D-009 - lecon deja tiree pour
OMEGA-DEEP, un export detache sous-livre "visualisation du graphe") -
regle d'implementation, pas visible dans ce contrat."""
from __future__ import annotations

from typing import Protocol

from omega_track.domain.entities.identity_report import IdentityReport
from omega_track.domain.value_objects.export_options import ExportOptions


class HtmlExporter(Protocol):
    def export(self, report: IdentityReport, options: ExportOptions) -> bytes: ...
