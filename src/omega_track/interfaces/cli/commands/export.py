# Copyright (c) 2026 kraynux - Licence MIT
"""Commande `export <run-id> --format json|md|html|csv|dot|mermaid`
(plan de dev §9) - `--format` invalide leve UnknownExportFormatError
(code de sortie 1), distinct d'un run introuvable (TrackRunNotFoundError,
code 3) : les deux sont geres centralement par interfaces/cli/main.py,
ce module se contente de traduire le nom CLI ("md") vers le nom interne
des exporteurs ("markdown", app/bootstrap.py::exporters)."""
from __future__ import annotations

import argparse
from typing import TYPE_CHECKING

from omega_track.application.commands.exports.export_track import export_track
from omega_track.application.exceptions import UnknownExportFormatError
from omega_track.core.export_theme import DEFAULT_EXPORT_THEME, EXPORT_PALETTES
from omega_track.domain.value_objects.export_options import ExportOptions
from omega_track.domain.value_objects.identifiers import TrackRunId
from omega_track.domain.value_objects.statuses import RedactionPolicy
from omega_track.interfaces.cli.presenters.console_presenter import print_export_artifact
from omega_track.interfaces.cli.presenters.json_presenter import print_json

if TYPE_CHECKING:
    from omega_track.app.container import DependencyContainer

_CLI_FORMAT_TO_INTERNAL: dict[str, str] = {
    "json": "json",
    "md": "markdown",
    "html": "html",
    "csv": "csv",
    "dot": "dot",
    "mermaid": "mermaid",
}


def add_subparser(subparsers: argparse._SubParsersAction) -> None:
    parser = subparsers.add_parser("export", help="exporter un TrackRun termine")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("run_id")
    parser.add_argument("--format", required=True, choices=sorted(_CLI_FORMAT_TO_INTERNAL))
    parser.add_argument(
        "--redact", choices=[policy.value for policy in RedactionPolicy], default=RedactionPolicy.NONE.value
    )
    parser.add_argument(
        "--theme",
        choices=sorted(EXPORT_PALETTES),
        default=DEFAULT_EXPORT_THEME,
        help="theme de couleurs du rapport HTML (sans effet sur les autres formats)",
    )
    parser.set_defaults(handler=_handle)


def _handle(container: DependencyContainer, args: argparse.Namespace) -> int:
    internal_format = _CLI_FORMAT_TO_INTERNAL.get(args.format)
    if internal_format is None:
        raise UnknownExportFormatError(args.format)

    artifact = export_track(
        export_orchestrator=container.export_orchestrator,
        track_run_id=TrackRunId(args.run_id),
        export_format=internal_format,
        output_dir=container.default_exports_dir,
        options=ExportOptions(redaction_policy=RedactionPolicy(args.redact), export_theme=args.theme),
    )
    if args.json:
        print_json(
            {
                "id": str(artifact.id),
                "format": artifact.format,
                "output_path": artifact.output_path,
                "checksum": artifact.checksum,
                "redaction_policy": artifact.redaction_policy.value,
            }
        )
    else:
        print_export_artifact(artifact)
    return 0
