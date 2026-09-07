# Copyright (c) 2026 kraynux - Licence MIT
"""ExportOrchestrator (plan de dev §8) - construit un IdentityReport
(report_builder.py), applique la redaction (docs/PRIVACY.md §3) AVANT de
le transmettre a l'exporteur choisi (les exporteurs eux-memes ne
connaissent jamais RedactionPolicy autrement que pour l'afficher dans
l'en-tete - toute la logique de redaction vit ici, une seule fois),
ecrit le resultat a un chemin deterministe et persiste un
ExportArtifact (checksum inclus).

Nom de fichier horodate ET lisible (`{YYYYMMDDTHHMMSS}_{cible}_{id-court}.
{ext}`, Phase 12, retour utilisateur "les noms de fichiers de sortie sont
trop compliques") - timestamp en prefixe pour un tri chronologique
naturel dans un explorateur de fichiers (ordre alphabetique = ordre
chronologique) ; le TrackRunId complet (UUID hex 32 caracteres, illisible
tel quel) est tronque a 8 caracteres, suffisant pour distinguer deux
exports visuellement sans viser l'unicite garantie a lui seul - l'export
repete au meme format pour le meme run a la meme seconde reste possible
en theorie (options de redaction/theme differentes) mais rarissime en
pratique ; le nom complet reste de toute facon retrouvable via
`ExportArtifact.track_run_id`, jamais perdu."""
from __future__ import annotations

import hashlib
import re
from collections.abc import Callable
from dataclasses import replace
from datetime import datetime
from pathlib import Path
from typing import Protocol

from omega_track.application.exceptions import UnknownExportFormatError
from omega_track.application.orchestrators.report_builder import build_identity_report
from omega_track.domain.entities.export_artifact import ExportArtifact
from omega_track.domain.entities.identity_report import IdentityReport
from omega_track.domain.services.redaction_service import redact_findings
from omega_track.domain.value_objects.export_options import ExportOptions
from omega_track.domain.value_objects.identifiers import ExportId, TrackRunId
from omega_track.ports.repositories.export_repository import ExportRepository
from omega_track.ports.repositories.finding_repository import FindingRepository
from omega_track.ports.repositories.target_repository import TargetRepository
from omega_track.ports.repositories.track_run_repository import TrackRunRepository
from omega_track.shared.typing import IdFactory

_FORMAT_EXTENSIONS: dict[str, str] = {
    "json": "json",
    "markdown": "md",
    "html": "html",
    "csv": "zip",
    "dot": "dot",
    "mermaid": "mmd",
}

_UNSAFE_FILENAME_CHARS = re.compile(r"[^A-Za-z0-9.\-]+")


def _filename_slug(target_value: object, *, max_length: int = 40) -> str:
    """Cible -> fragment de nom de fichier lisible (domaines/IPv4 restent
    quasi inchanges, IPv6 perd ses ':' - invalides sur certains systemes
    de fichiers - remplaces par '-')."""
    slug = _UNSAFE_FILENAME_CHARS.sub("-", str(target_value)).strip("-")
    return slug[:max_length] or "cible"


class Exporter(Protocol):
    def export(self, report: IdentityReport, options: ExportOptions) -> bytes: ...


class ExportOrchestrator:
    def __init__(
        self,
        *,
        track_run_repository: TrackRunRepository,
        target_repository: TargetRepository,
        finding_repository: FindingRepository,
        export_repository: ExportRepository,
        exporters: dict[str, Exporter],
        id_factory: IdFactory,
        now: Callable[[], datetime],
    ) -> None:
        self._track_run_repository = track_run_repository
        self._target_repository = target_repository
        self._finding_repository = finding_repository
        self._export_repository = export_repository
        self._exporters = exporters
        self._id_factory = id_factory
        self._now = now

    def export(
        self,
        *,
        track_run_id: TrackRunId,
        export_format: str,
        output_dir: Path,
        options: ExportOptions | None = None,
    ) -> ExportArtifact:
        if export_format not in self._exporters:
            raise UnknownExportFormatError(export_format)
        effective_options = options if options is not None else ExportOptions()

        report = build_identity_report(
            track_run_id=track_run_id,
            track_run_repository=self._track_run_repository,
            target_repository=self._target_repository,
            finding_repository=self._finding_repository,
            now=self._now,
        )
        redacted_report = replace(
            report, findings=redact_findings(report.findings, effective_options.redaction_policy)
        )

        content = self._exporters[export_format].export(redacted_report, effective_options)

        output_dir.mkdir(parents=True, exist_ok=True)
        extension = _FORMAT_EXTENSIONS[export_format]
        timestamp = self._now().strftime("%Y%m%dT%H%M%S")
        slug = _filename_slug(report.target_value)
        short_id = str(track_run_id)[:8]
        output_path = output_dir / f"{timestamp}_{slug}_{short_id}.{extension}"
        output_path.write_bytes(content)

        artifact = ExportArtifact(
            id=ExportId(self._id_factory()),
            track_run_id=track_run_id,
            format=export_format,
            output_path=str(output_path),
            checksum=hashlib.sha256(content).hexdigest(),
            redaction_policy=effective_options.redaction_policy,
            created_at=self._now(),
        )
        self._export_repository.save(artifact)
        return artifact
