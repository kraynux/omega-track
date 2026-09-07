# Copyright (c) 2026 kraynux - Licence MIT
"""Contexte d'execution partage entre track_orchestrator.py et
phases/*.py (Phase 7) - prive (meme convention que
infrastructure/repositories/sqlite/_profile_serde.py) : evite de repeter
les 4 memes parametres (track_run_id/id_factory/now/event_publisher/
cancellation_token) sur chaque fonction de phase."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime

from omega_track.application.orchestrators.cancellation import CancellationToken
from omega_track.domain.entities.findings.base import Finding
from omega_track.domain.entities.track_run import ModuleRun
from omega_track.domain.services.finding_builder import build_finding
from omega_track.domain.value_objects.collected_record import CollectedRecord
from omega_track.domain.value_objects.collection_mode import CollectionMode
from omega_track.domain.value_objects.identifiers import ModuleRunId, TrackRunId
from omega_track.domain.value_objects.statuses import ModuleStatus
from omega_track.ports.services.event_publisher import EventPublisher
from omega_track.shared.typing import IdFactory


@dataclass(frozen=True, slots=True)
class PhaseContext:
    track_run_id: TrackRunId
    id_factory: IdFactory
    now: Callable[[], datetime]
    event_publisher: EventPublisher
    cancellation_token: CancellationToken


def publish_module_status(context: PhaseContext, module_run: ModuleRun) -> None:
    context.event_publisher.publish_module_status(context.track_run_id, module_run.module_name, module_run.status)


def skip_module(module_run: ModuleRun, context: PhaseContext, *, reason: str) -> None:
    module_run.transition_to(ModuleStatus.SKIPPED, now=context.now())
    module_run.error_detail = reason
    publish_module_status(context, module_run)


def build_findings(
    records: list[CollectedRecord],
    *,
    context: PhaseContext,
    module_run_id: ModuleRunId,
    collection_mode: CollectionMode,
) -> list[Finding]:
    return [
        build_finding(
            record,
            track_run_id=context.track_run_id,
            module_run_id=module_run_id,
            collection_mode=collection_mode,
            id_factory=context.id_factory,
            now=context.now,
        )
        for record in records
    ]
