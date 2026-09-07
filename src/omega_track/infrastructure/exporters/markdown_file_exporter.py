# Copyright (c) 2026 kraynux - Licence MIT
"""Implementation reelle de MarkdownExporter (Phase 8) - genere depuis le
meme modele de rapport que JsonFileExporter (`_report_view.py`), pas une
extraction ad hoc separee (plan de dev §8 point 2 : "genere depuis le
meme modele de rapport")."""
from __future__ import annotations

from collections import defaultdict

from omega_track.domain.entities.identity_report import IdentityReport
from omega_track.domain.value_objects.export_options import ExportOptions
from omega_track.infrastructure.exporters._report_view import build_header, path_to_dict


class MarkdownFileExporter:
    """Implemente ports/exporters/markdown_exporter.py::MarkdownExporter."""

    def export(self, report: IdentityReport, options: ExportOptions) -> bytes:
        header = build_header(report, options)
        lines: list[str] = []

        lines.append(f"# Rapport OMEGA-TRACK - {header['target']}")
        lines.append("")
        lines.append(f"- Genere le {header['generated_at']}")
        lines.append(f"- Profil : {header['profile']} (modules : {', '.join(header['modules']) or 'aucun'})")
        lines.append(f"- Sources consultees : {', '.join(header['sources']) or 'aucune'}")
        lines.append(f"- Politique de redaction : {header['redaction_policy']}")
        lines.append(
            f"- Schema d'export v{header['schema_version']} - omega-track {header['app_version']}"
        )
        lines.append("")

        summary = report.summarize()
        lines.append("## Resume")
        lines.append("")
        lines.append("| Niveau de confiance | Nombre |")
        lines.append("| --- | --- |")
        for level, count in summary.items():
            lines.append(f"| {level} | {count} |")
        lines.append("")

        by_family: dict[str, list] = defaultdict(list)
        for finding in report.findings:
            family = finding.finding_type.split(".", 1)[0]
            by_family[family].append(finding)

        for family in sorted(by_family):
            lines.append(f"## {family.capitalize()}")
            lines.append("")
            lines.append("| Type | Donnees | Confiance | Source |")
            lines.append("| --- | --- | --- | --- |")
            for finding in by_family[family]:
                lines.append(
                    f"| {finding.finding_type} | {finding.payload} | {finding.confidence.value} | {finding.source_name} |"
                )
            lines.append("")

        if report.relations:
            lines.append("## Relations")
            lines.append("")
            lines.append("| Source | Cible | Type | Confiance |")
            lines.append("| --- | --- | --- | --- |")
            for relation in report.relations:
                lines.append(
                    f"| {relation.source_entity_ref} | {relation.target_entity_ref} | "
                    f"{relation.relation_type.value} | {relation.confidence.value} |"
                )
            lines.append("")

        if report.clusters:
            lines.append("## Clusters")
            lines.append("")
            for cluster in report.clusters:
                lines.append(f"- {cluster.label or cluster.id} : {', '.join(sorted(cluster.member_refs))}")
            lines.append("")

        if report.paths:
            lines.append("## Chemin reseau (NeoTrace)")
            lines.append("")
            for path in report.paths:
                path_view = path_to_dict(path)
                lines.append(
                    f"### Vers {path_view['target_ip']} ({path_view['protocol']}) - "
                    f"{'atteinte' if path_view['reached_target'] else 'non atteinte'}"
                )
                lines.append("")
                lines.append("| # | IP | Hote | RTT (ms) | ASN | Pays |")
                lines.append("| --- | --- | --- | --- | --- | --- |")
                for hop in path_view["hops"]:
                    ip_text = hop["ip"] if hop["ip"] is not None else "*"
                    lines.append(
                        f"| {hop['sequence']} | {ip_text} | {hop['hostname'] or ''} | "
                        f"{hop['rtt_ms'] if hop['rtt_ms'] is not None else ''} | "
                        f"{hop['asn'] or ''} | {hop['geo_country'] or ''} |"
                    )
                lines.append("")

        return "\n".join(lines).encode("utf-8")
