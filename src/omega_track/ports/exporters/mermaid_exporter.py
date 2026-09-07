# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat d'export Mermaid (plan de dev, Phase 3/8) - reutilise pour le
graphe embarque dans l'export HTML (D-009), pas seulement pour un
fichier `.mmd` autonome."""
from __future__ import annotations

from typing import Protocol

from omega_track.domain.entities.identity_report import IdentityReport
from omega_track.domain.value_objects.export_options import ExportOptions


class MermaidExporter(Protocol):
    def export(self, report: IdentityReport, options: ExportOptions) -> bytes: ...
