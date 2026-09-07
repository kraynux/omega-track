# Copyright (c) 2026 kraynux - Licence MIT
"""Affichage humain, un objet a la fois (plan de dev §9) - utilise quand
`--json` n'est pas demande."""
from __future__ import annotations

import sys

from omega_track.application.commands.maintenance.cleanup_history import HistoryCleanupPreview
from omega_track.application.queries.diagnostics import DiagnosticsReport
from omega_track.domain.entities.export_artifact import ExportArtifact
from omega_track.domain.entities.target import Target
from omega_track.domain.entities.track_run import TrackRun


def print_error(message: str) -> None:
    print(f"erreur : {message}", file=sys.stderr)


def print_target(target: Target) -> None:
    print(f"{target.id}  {target.value}  ({target.kind.value})")
    print(f"  alias    : {target.alias or '-'}")
    print(f"  tags     : {', '.join(sorted(target.tags)) or '-'}")
    print(f"  epinglee : {'oui' if target.pinned else 'non'}")
    print(f"  dernier track : {target.last_status or '-'} ({target.last_track_at or '-'})")


def print_track_run(run: TrackRun) -> None:
    print(f"{run.id}  cible={run.target_id}  statut={run.status.value}  progression={run.progress:.0%}")
    if run.error_summary:
        print(f"  resume erreur : {run.error_summary}")
    for name, module_run in run.module_runs.items():
        detail = f" ({module_run.error_detail})" if module_run.error_detail else ""
        print(f"  module {name} : {module_run.status.value}{detail}")


def print_export_artifact(artifact: ExportArtifact) -> None:
    print(f"export {artifact.id} ({artifact.format}) -> {artifact.output_path}")
    print(f"  checksum : {artifact.checksum}")
    print(f"  redaction : {artifact.redaction_policy.value}")


def print_cleanup_preview(preview: HistoryCleanupPreview) -> None:
    print(f"{preview.count} execution(s) seraient supprimees :")
    for track_run_id in preview.track_run_ids:
        print(f"  - {track_run_id}")


def print_diagnostics(report: DiagnosticsReport) -> None:
    print(f"omega-track {report.app_version} (schema d'export v{report.schema_version})")
    print(f"repertoire de donnees : {report.var_dir}")
    print(f"traceroute disponible : {'oui' if report.traceroute_available else 'non'}")
    geoip = report.geoip_status
    if geoip.status is None:
        print("base GeoIP : absente")
    else:
        stale = " (perimee)" if geoip.is_stale else ""
        print(f"base GeoIP : {geoip.status.provider} {geoip.status.edition} - {geoip.status.status}{stale}")
