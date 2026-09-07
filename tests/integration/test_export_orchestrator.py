# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from pathlib import Path

import pytest

from omega_track.application.exceptions import UnknownExportFormatError
from omega_track.application.orchestrators.export_orchestrator import ExportOrchestrator
from omega_track.core.enums import ConfidenceLevel
from omega_track.domain.entities.export_artifact import ExportArtifact
from omega_track.domain.entities.findings.base import Finding
from omega_track.domain.entities.identity_report import IdentityReport
from omega_track.domain.entities.relation import Relation
from omega_track.domain.entities.target import Target
from omega_track.domain.entities.track_profile import TrackProfile
from omega_track.domain.entities.track_run import TrackRun
from omega_track.domain.value_objects.collection_mode import CollectionMode
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.domain.value_objects.export_options import ExportOptions
from omega_track.domain.value_objects.identifiers import (
    ExportId,
    FindingId,
    ModuleRunId,
    TargetId,
    TrackProfileId,
    TrackRunId,
)
from omega_track.domain.value_objects.statuses import RedactionPolicy, TrackStatus

_NOW = datetime(2026, 9, 6, tzinfo=timezone.utc)
_RUN_ID = TrackRunId("run-1")
_TARGET_ID = TargetId("target-1")


class _FakeTrackRunRepository:
    def __init__(self, run: TrackRun | None) -> None:
        self._run = run

    def save(self, run: TrackRun) -> None:
        self._run = run

    def get(self, track_run_id: TrackRunId) -> TrackRun | None:
        return self._run

    def list_for_target(self, target_id: TargetId) -> list[TrackRun]:
        return []

    def list_recent(self, **kwargs: object) -> list[TrackRun]:
        return []

    def delete(self, track_run_id: TrackRunId) -> None:
        pass


class _FakeTargetRepository:
    def __init__(self, target: Target | None) -> None:
        self._target = target

    def save(self, target: Target) -> None:
        self._target = target

    def get(self, target_id: TargetId) -> Target | None:
        return self._target

    def find_by_value(self, value: object) -> Target | None:
        return self._target

    def list_all(self) -> list[Target]:
        return []

    def delete(self, target_id: TargetId) -> None:
        pass


class _FakeFindingRepository:
    def __init__(self, findings: list[Finding]) -> None:
        self._findings = findings

    def save_findings(self, findings: list[Finding]) -> None:
        pass

    def save_relations(self, relations: list[Relation]) -> None:
        pass

    def list_findings_for_run(self, track_run_id: TrackRunId) -> list[Finding]:
        return self._findings

    def list_relations_for_run(self, track_run_id: TrackRunId) -> list[Relation]:
        return []

    def delete_for_run(self, track_run_id: TrackRunId) -> None:
        pass


class _FakeExportRepository:
    def __init__(self) -> None:
        self.saved: list[ExportArtifact] = []

    def save(self, artifact: ExportArtifact) -> None:
        self.saved.append(artifact)

    def list_for_run(self, track_run_id: TrackRunId) -> list[ExportArtifact]:
        return list(self.saved)

    def delete(self, export_id: ExportId) -> None:
        pass


class _RecordingExporter:
    def __init__(self) -> None:
        self.calls: list[tuple[IdentityReport, ExportOptions]] = []

    def export(self, report: IdentityReport, options: ExportOptions) -> bytes:
        self.calls.append((report, options))
        return b"contenu-simule"


def _profile() -> TrackProfile:
    return TrackProfile(
        id=TrackProfileId("profile-1"), name="default", modules={"dns"}, created_at=_NOW, updated_at=_NOW
    )


def _track_run() -> TrackRun:
    return TrackRun(
        id=_RUN_ID, target_id=_TARGET_ID, profile_snapshot=_profile(), status=TrackStatus.COMPLETED, created_at=_NOW
    )


def _target() -> Target:
    return Target(id=_TARGET_ID, value=DomainName.parse("example.com"), created_at=_NOW, updated_at=_NOW)


def _contact_finding() -> Finding:
    return Finding(
        id=FindingId("f1"), track_run_id=_RUN_ID, module_run_id=ModuleRunId("mr-1"),
        finding_type="identity.registrant_contact", payload={"email": "john@example.com"},
        confidence=ConfidenceLevel.DECLARED, collection_mode=CollectionMode.PASSIVE_PUBLIC,
        source_name="rdap", observed_at=_NOW, collected_at=_NOW,
    )


def _orchestrator(
    *,
    exporter: _RecordingExporter,
    findings: list[Finding] | None = None,
    target: Target | None = None,
    track_run: TrackRun | None = None,
) -> tuple[ExportOrchestrator, _FakeExportRepository]:
    export_repo = _FakeExportRepository()
    orchestrator = ExportOrchestrator(
        track_run_repository=_FakeTrackRunRepository(track_run or _track_run()),
        target_repository=_FakeTargetRepository(target or _target()),
        finding_repository=_FakeFindingRepository(findings or []),
        export_repository=export_repo,
        exporters={"json": exporter},
        id_factory=lambda: "export-1",
        now=lambda: _NOW,
    )
    return orchestrator, export_repo


def test_writes_file_and_persists_artifact(tmp_path: Path) -> None:
    exporter = _RecordingExporter()
    orchestrator, export_repo = _orchestrator(exporter=exporter)

    artifact = orchestrator.export(track_run_id=_RUN_ID, export_format="json", output_dir=tmp_path)

    expected_path = tmp_path / f"{_NOW.strftime('%Y%m%dT%H%M%S')}_example.com_{str(_RUN_ID)[:8]}.json"
    assert expected_path.read_bytes() == b"contenu-simule"
    assert artifact.output_path == str(expected_path)
    assert artifact.format == "json"
    assert artifact.checksum  # sha256 hex non vide
    assert export_repo.saved == [artifact]


def test_filename_is_readable_timestamp_first_not_a_bare_uuid(tmp_path: Path) -> None:
    """Regression Phase 12 : "les noms de fichiers de sortie sont trop
    compliques" - timestamp en prefixe (tri chronologique naturel), cible
    lisible, identifiant tronque a 8 caracteres plutot que l'UUID hex
    complet (32 caracteres, illisible)."""
    orchestrator, _ = _orchestrator(exporter=_RecordingExporter())
    artifact = orchestrator.export(track_run_id=_RUN_ID, export_format="json", output_dir=tmp_path)

    filename = Path(artifact.output_path).name
    assert filename.startswith(_NOW.strftime("%Y%m%dT%H%M%S"))
    assert "example.com" in filename


def test_filename_truncates_a_real_uuid_style_run_id_to_8_characters(tmp_path: Path) -> None:
    from omega_lib.shared.ids import new_id

    long_run_id = TrackRunId(new_id())
    orchestrator, _ = _orchestrator(
        exporter=_RecordingExporter(),
        track_run=TrackRun(
            id=long_run_id, target_id=_TARGET_ID, profile_snapshot=_profile(),
            status=TrackStatus.COMPLETED, created_at=_NOW,
        ),
    )
    artifact = orchestrator.export(track_run_id=long_run_id, export_format="json", output_dir=tmp_path)

    filename = Path(artifact.output_path).name
    assert str(long_run_id) not in filename
    stem_suffix = filename.rsplit("_", 1)[-1].split(".", 1)[0]
    assert stem_suffix == str(long_run_id)[:8]


def test_ipv6_target_produces_a_filesystem_safe_slug(tmp_path: Path) -> None:
    """Une IPv6 contient des ':' - invalides dans un nom de fichier sur
    certains systemes - doivent etre remplaces, jamais laisses tels quels."""
    from omega_track.domain.value_objects.ip_address import IPAddress

    ipv6_target = Target(id=_TARGET_ID, value=IPAddress.parse("2001:db8::1"), created_at=_NOW, updated_at=_NOW)
    orchestrator, _ = _orchestrator(exporter=_RecordingExporter(), target=ipv6_target)
    artifact = orchestrator.export(track_run_id=_RUN_ID, export_format="json", output_dir=tmp_path)

    filename = Path(artifact.output_path).name
    assert ":" not in filename
    assert Path(artifact.output_path).exists()


def test_unknown_format_raises() -> None:
    orchestrator, _ = _orchestrator(exporter=_RecordingExporter())
    with pytest.raises(UnknownExportFormatError):
        orchestrator.export(track_run_id=_RUN_ID, export_format="bogus", output_dir=Path("/tmp"))


def test_redaction_is_applied_before_reaching_the_exporter(tmp_path: Path) -> None:
    exporter = _RecordingExporter()
    orchestrator, _ = _orchestrator(exporter=exporter, findings=[_contact_finding()])

    orchestrator.export(
        track_run_id=_RUN_ID, export_format="json", output_dir=tmp_path,
        options=ExportOptions(redaction_policy=RedactionPolicy.CONTACTS_ONLY),
    )

    report_seen_by_exporter, _ = exporter.calls[0]
    assert report_seen_by_exporter.findings[0].payload == {"email": "[redacted]"}


def test_no_redaction_by_default(tmp_path: Path) -> None:
    exporter = _RecordingExporter()
    orchestrator, _ = _orchestrator(exporter=exporter, findings=[_contact_finding()])

    orchestrator.export(track_run_id=_RUN_ID, export_format="json", output_dir=tmp_path)

    report_seen_by_exporter, _ = exporter.calls[0]
    assert report_seen_by_exporter.findings[0].payload == {"email": "john@example.com"}


def test_checksum_matches_real_sha256(tmp_path: Path) -> None:
    orchestrator, _ = _orchestrator(exporter=_RecordingExporter())
    artifact = orchestrator.export(track_run_id=_RUN_ID, export_format="json", output_dir=tmp_path)
    assert artifact.checksum == hashlib.sha256(b"contenu-simule").hexdigest()
