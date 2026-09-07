# Copyright (c) 2026 kraynux - Licence MIT
"""Contrat d'export Markdown (plan de dev, Phase 3/8)."""
from __future__ import annotations

from typing import Protocol

from omega_track.domain.entities.identity_report import IdentityReport
from omega_track.domain.value_objects.export_options import ExportOptions


class MarkdownExporter(Protocol):
    def export(self, report: IdentityReport, options: ExportOptions) -> bytes: ...
