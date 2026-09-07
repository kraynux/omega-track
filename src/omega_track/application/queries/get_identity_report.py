# Copyright (c) 2026 kraynux - Licence MIT
"""Use case GetIdentityReport (plan de dev §9 `track show <run-id>`) -
delegue a report_builder.py (Phase 8), meme discipline "wrapper fin"
que export_track.py autour de export_orchestrator.py."""
from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from omega_track.application.orchestrators.report_builder import build_identity_report
from omega_track.domain.entities.identity_report import IdentityReport
from omega_track.domain.value_objects.identifiers import TrackRunId
from omega_track.ports.repositories.finding_repository import FindingRepository
from omega_track.ports.repositories.target_repository import TargetRepository
from omega_track.ports.repositories.track_run_repository import TrackRunRepository


def get_identity_report(
    *,
    track_run_id: TrackRunId,
    track_run_repository: TrackRunRepository,
    target_repository: TargetRepository,
    finding_repository: FindingRepository,
    now: Callable[[], datetime],
) -> IdentityReport:
    return build_identity_report(
        track_run_id=track_run_id,
        track_run_repository=track_run_repository,
        target_repository=target_repository,
        finding_repository=finding_repository,
        now=now,
    )
