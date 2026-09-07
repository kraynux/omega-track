# Copyright (c) 2026 kraynux - Licence MIT
"""Implementation reelle de JsonExporter (Phase 8) - JSON canonique
(cles triees, indente) et versionne (plan de dev §8 point 1)."""
from __future__ import annotations

import json

from omega_track.domain.entities.identity_report import IdentityReport
from omega_track.domain.value_objects.export_options import ExportOptions
from omega_track.infrastructure.exporters._report_view import (
    build_header,
    cluster_to_dict,
    finding_to_dict,
    path_to_dict,
    relation_to_dict,
)


class JsonFileExporter:
    """Implemente ports/exporters/json_exporter.py::JsonExporter."""

    def export(self, report: IdentityReport, options: ExportOptions) -> bytes:
        payload = {
            "header": build_header(report, options),
            "summary": report.summarize(),
            "findings": [finding_to_dict(f) for f in report.findings],
            "relations": [relation_to_dict(r) for r in report.relations],
            "clusters": [cluster_to_dict(c) for c in report.clusters],
            "paths": [path_to_dict(p) for p in report.paths],
        }
        return json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False).encode("utf-8")
