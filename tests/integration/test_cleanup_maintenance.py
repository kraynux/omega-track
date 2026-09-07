# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

from omega_track.application.commands.maintenance.cleanup_exports import delete_exports_for_runs
from omega_track.application.commands.maintenance.cleanup_history import (
    cleanup_history,
    preview_history_cleanup,
)
from omega_track.domain.entities.export_artifact import ExportArtifact
from omega_track.domain.entities.findings.base import Finding
from omega_track.domain.entities.relation import Relation
from omega_track.domain.entities.track_profile import TrackProfile
from omega_track.domain.entities.track_run import TrackRun
from omega_track.domain.value_objects.identifiers import (
    ExportId,
    TargetId,
    TrackProfileId,
    TrackRunId,
)
from omega_track.domain.value_objects.statuses import RedactionPolicy, TrackStatus

_NOW = datetime(2026, 9, 6, tzinfo=timezone.utc)


class _FakeTrackRunRepository:
    def __init__(self, runs: list[TrackRun]) -> None:
        self._runs = {r.id: r for r in runs}
        self.deleted: list[TrackRunId] = []

    def save(self, run: TrackRun) -> None:
        self._runs[run.id] = run

    def get(self, track_run_id: TrackRunId) -> TrackRun | None:
        return self._runs.get(track_run_id)

    def list_for_target(self, target_id: TargetId) -> list[TrackRun]:
        return []

    def list_recent(self, *, until: datetime | None = None, **kwargs: object) -> list[TrackRun]:
        return [r for r in self._runs.values() if until is None or r.created_at <= until]

    def delete(self, track_run_id: TrackRunId) -> None:
        self.deleted.append(track_run_id)
        self._runs.pop(track_run_id, None)


class _FakeFindingRepository:
    def __init__(self) -> None:
        self.deleted_for_run: list[TrackRunId] = []

    def save_findings(self, findings: list[Finding]) -> None:
        pass

    def save_relations(self, relations: list[Relation]) -> None:
        pass

    def list_findings_for_run(self, track_run_id: TrackRunId) -> list[Finding]:
        return []

    def list_relations_for_run(self, track_run_id: TrackRunId) -> list[Relation]:
        return []

    def delete_for_run(self, track_run_id: TrackRunId) -> None:
        self.deleted_for_run.append(track_run_id)


class _FakeExportRepository:
    def __init__(self, artifacts: dict[TrackRunId, list[ExportArtifact]]) -> None:
        self._artifacts = artifacts
        self.deleted: list[ExportId] = []

    def save(self, artifact: ExportArtifact) -> None:
        pass

    def list_for_run(self, track_run_id: TrackRunId) -> list[ExportArtifact]:
        return self._artifacts.get(track_run_id, [])

    def delete(self, export_id: ExportId) -> None:
        self.deleted.append(export_id)


def _run(run_id: str, *, days_old: int) -> TrackRun:
    profile = TrackProfile(id=TrackProfileId("p1"), name="p", modules=set(), created_at=_NOW, updated_at=_NOW)
    return TrackRun(
        id=TrackRunId(run_id), target_id=TargetId("t1"), profile_snapshot=profile, status=TrackStatus.COMPLETED,
        created_at=_NOW - timedelta(days=days_old),
    )


def _artifact(run_id: str, path: Path) -> ExportArtifact:
    return ExportArtifact(
        id=ExportId(f"export-{run_id}"), track_run_id=TrackRunId(run_id), format="json", output_path=str(path),
        checksum="abc", redaction_policy=RedactionPolicy.NONE, created_at=_NOW,
    )


def test_preview_lists_only_old_runs() -> None:
    repo = _FakeTrackRunRepository([_run("old", days_old=90), _run("recent", days_old=1)])
    preview = preview_history_cleanup(track_run_repository=repo, older_than=timedelta(days=30), now=lambda: _NOW)
    assert preview.track_run_ids == [TrackRunId("old")]
    assert preview.count == 1


def test_cleanup_history_deletes_old_runs_findings_and_exports(tmp_path: Path) -> None:
    export_path = tmp_path / "old.json"
    export_path.write_text("{}", encoding="utf-8")

    run_repo = _FakeTrackRunRepository([_run("old", days_old=90), _run("recent", days_old=1)])
    finding_repo = _FakeFindingRepository()
    export_repo = _FakeExportRepository({TrackRunId("old"): [_artifact("old", export_path)]})

    result = cleanup_history(
        track_run_repository=run_repo, finding_repository=finding_repo, export_repository=export_repo,
        older_than=timedelta(days=30), now=lambda: _NOW,
    )

    assert result.track_run_ids == [TrackRunId("old")]
    assert run_repo.deleted == [TrackRunId("old")]
    assert finding_repo.deleted_for_run == [TrackRunId("old")]
    assert export_repo.deleted == [ExportId("export-old")]
    assert not export_path.exists()
    assert run_repo.get(TrackRunId("recent")) is not None


def test_delete_exports_for_runs_removes_file_and_row(tmp_path: Path) -> None:
    export_path = tmp_path / "a.json"
    export_path.write_text("{}", encoding="utf-8")
    export_repo = _FakeExportRepository({TrackRunId("r1"): [_artifact("r1", export_path)]})

    deleted = delete_exports_for_runs(export_repository=export_repo, track_run_ids=[TrackRunId("r1")])

    assert deleted == 1
    assert not export_path.exists()
    assert export_repo.deleted == [ExportId("export-r1")]


def test_delete_exports_for_runs_is_safe_when_file_already_missing(tmp_path: Path) -> None:
    missing_path = tmp_path / "missing.json"
    export_repo = _FakeExportRepository({TrackRunId("r1"): [_artifact("r1", missing_path)]})

    deleted = delete_exports_for_runs(export_repository=export_repo, track_run_ids=[TrackRunId("r1")])
    assert deleted == 1
