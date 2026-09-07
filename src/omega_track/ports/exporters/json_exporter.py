# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat d'export JSON (plan de dev, Phase 3/8). Tous les exporteurs
partagent la meme forme de signature (IdentityReport + ExportOptions ->
bytes) - un fichier par format (pas un seul port generique) pour que le
container puisse cabler/remplacer chaque format independamment (Phase 8)."""
from __future__ import annotations

from typing import Protocol

from omega_track.domain.entities.identity_report import IdentityReport
from omega_track.domain.value_objects.export_options import ExportOptions


class JsonExporter(Protocol):
    def export(self, report: IdentityReport, options: ExportOptions) -> bytes: ...
