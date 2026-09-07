# Copyright (c) 2026 kraynux - Licence MIT
"""Implementation reelle de CsvExporter (Phase 8) - un fichier CSV par
"table metier" (famille de finding, deduite du prefixe `finding_type`,
plus un fichier `relations.csv`) regroupes dans un ZIP unique : le plan
laisse le choix entre "un fichier par table" et "ZIP multi-fichiers",
le ZIP evite d'imposer a l'appelant de gerer plusieurs chemins de sortie
pour un seul export CSV."""
from __future__ import annotations

import csv
import io
import zipfile
from collections import defaultdict

from omega_track.domain.entities.findings.base import Finding
from omega_track.domain.entities.identity_report import IdentityReport
from omega_track.domain.entities.relation import Relation
from omega_track.domain.value_objects.export_options import ExportOptions


class CsvFileExporter:
    """Implemente ports/exporters/csv_exporter.py::CsvExporter."""

    def export(self, report: IdentityReport, options: ExportOptions) -> bytes:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, mode="w", compression=zipfile.ZIP_DEFLATED) as archive:
            by_family: dict[str, list[Finding]] = defaultdict(list)
            for finding in report.findings:
                by_family[finding.finding_type.split(".", 1)[0]].append(finding)

            for family in sorted(by_family):
                archive.writestr(f"findings_{family}.csv", _findings_csv(by_family[family]))

            if report.relations:
                archive.writestr("relations.csv", _relations_csv(report.relations))

        return buffer.getvalue()


def _findings_csv(findings: list[Finding]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["finding_type", "payload", "confidence", "collection_mode", "source_name", "observed_at"])
    for finding in findings:
        writer.writerow(
            [
                finding.finding_type,
                finding.payload,
                finding.confidence.value,
                finding.collection_mode.value,
                finding.source_name,
                finding.observed_at.isoformat(),
            ]
        )
    return output.getvalue()


def _relations_csv(relations: list[Relation]) -> str:
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["source", "target", "relation_type", "confidence"])
    for relation in relations:
        writer.writerow(
            [relation.source_entity_ref, relation.target_entity_ref, relation.relation_type.value, relation.confidence.value]
        )
    return output.getvalue()
