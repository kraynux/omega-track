# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from omega_track.application.commands.exports.export_track import export_track
from omega_track.domain.entities.export_artifact import ExportArtifact
from omega_track.domain.value_objects.export_options import ExportOptions
from omega_track.domain.value_objects.identifiers import ExportId, TrackRunId
from omega_track.domain.value_objects.statuses import RedactionPolicy

_NOW = datetime(2026, 9, 6, tzinfo=timezone.utc)


class _FakeExportOrchestrator:
    def __init__(self, artifact: ExportArtifact) -> None:
        self._artifact = artifact
        self.calls: list[dict[str, object]] = []

    def export(
        self, *, track_run_id: TrackRunId, export_format: str, output_dir: Path, options: ExportOptions | None
    ) -> ExportArtifact:
        self.calls.append(
            {"track_run_id": track_run_id, "export_format": export_format, "output_dir": output_dir, "options": options}
        )
        return self._artifact


def test_export_track_delegates_to_the_orchestrator(tmp_path: Path) -> None:
    artifact = ExportArtifact(
        id=ExportId("export-1"), track_run_id=TrackRunId("run-1"), format="json",
        output_path=str(tmp_path / "run-1.json"), checksum="abc", redaction_policy=RedactionPolicy.NONE,
        created_at=_NOW,
    )
    orchestrator = _FakeExportOrchestrator(artifact)

    result = export_track(
        export_orchestrator=orchestrator,
        track_run_id=TrackRunId("run-1"),
        export_format="json",
        output_dir=tmp_path,
    )

    assert result is artifact
    assert orchestrator.calls == [
        {"track_run_id": TrackRunId("run-1"), "export_format": "json", "output_dir": tmp_path, "options": None}
    ]
