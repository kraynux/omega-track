# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from datetime import datetime, timezone

from omega_track.application.queries.get_identity_report import get_identity_report
from omega_track.domain.entities.target import Target
from omega_track.domain.entities.track_profile import TrackProfile
from omega_track.domain.entities.track_run import TrackRun
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.domain.value_objects.identifiers import TargetId, TrackProfileId, TrackRunId
from omega_track.domain.value_objects.statuses import TrackStatus

_NOW = datetime(2026, 9, 6, tzinfo=timezone.utc)
_RUN_ID = TrackRunId("run-1")
_TARGET_ID = TargetId("target-1")


class _FakeTrackRunRepository:
    def get(self, track_run_id: TrackRunId) -> TrackRun | None:
        profile = TrackProfile(
            id=TrackProfileId("p1"), name="p", modules=set(), created_at=_NOW, updated_at=_NOW
        )
        return TrackRun(
            id=_RUN_ID, target_id=_TARGET_ID, profile_snapshot=profile, status=TrackStatus.COMPLETED,
            created_at=_NOW,
        )

    def save(self, run: TrackRun) -> None:
        pass

    def list_for_target(self, target_id: TargetId) -> list[TrackRun]:
        return []

    def list_recent(self, **kwargs: object) -> list[TrackRun]:
        return []

    def delete(self, track_run_id: TrackRunId) -> None:
        pass


class _FakeTargetRepository:
    def get(self, target_id: TargetId) -> Target | None:
        return Target(id=_TARGET_ID, value=DomainName.parse("example.com"), created_at=_NOW, updated_at=_NOW)

    def save(self, target: Target) -> None:
        pass

    def find_by_value(self, value: object) -> Target | None:
        return None

    def list_all(self) -> list[Target]:
        return []

    def delete(self, target_id: TargetId) -> None:
        pass


class _FakeFindingRepository:
    def save_findings(self, findings: list) -> None:
        pass

    def save_relations(self, relations: list) -> None:
        pass

    def list_findings_for_run(self, track_run_id: TrackRunId) -> list:
        return []

    def list_relations_for_run(self, track_run_id: TrackRunId) -> list:
        return []

    def delete_for_run(self, track_run_id: TrackRunId) -> None:
        pass


def test_get_identity_report_delegates_to_report_builder() -> None:
    report = get_identity_report(
        track_run_id=_RUN_ID,
        track_run_repository=_FakeTrackRunRepository(),
        target_repository=_FakeTargetRepository(),
        finding_repository=_FakeFindingRepository(),
        now=lambda: _NOW,
    )
    assert report.track_run_id == _RUN_ID
    assert report.target_value == DomainName.parse("example.com")
