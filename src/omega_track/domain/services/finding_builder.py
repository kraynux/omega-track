# Copyright (c) 2026 kraynux - Licence MIT
"""Conversion CollectedRecord -> Finding (Phase 6) - pure, sans I/O
(`id_factory`/`now` sont de simples callables injectes, meme convention
que domain/services/correlation_engine.py::infer_resolution_relation).

Un collecteur (ports/collectors/) ne connait ni le TrackRunId ni le
ModuleRunId (voir domain/value_objects/collected_record.py) : cette
fonction ajoute le contexte d'execution manquant. Necessaire des la
Phase 6 pour prouver que les collecteurs reels produisent un rapport
persistant (critere de sortie) - le collected_record.py de la Phase 3
anticipait ce cablage pour la Phase 7 (TrackOrchestrator), mais rien
dans cette conversion elle-meme ne depend de progression/annulation/
parallelisme (les apports reels de la Phase 7) : TrackOrchestrator
reutilisera cette fonction telle quelle plutot que de la redefinir."""
from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

from omega_track.domain.entities.findings.base import Finding
from omega_track.domain.value_objects.collected_record import CollectedRecord
from omega_track.domain.value_objects.collection_mode import CollectionMode
from omega_track.domain.value_objects.evidence import Evidence
from omega_track.domain.value_objects.identifiers import FindingId, ModuleRunId, TrackRunId
from omega_track.shared.typing import IdFactory


def build_finding(
    record: CollectedRecord,
    *,
    track_run_id: TrackRunId,
    module_run_id: ModuleRunId,
    collection_mode: CollectionMode,
    id_factory: IdFactory,
    now: Callable[[], datetime],
) -> Finding:
    finding = Finding(
        id=FindingId(id_factory()),
        track_run_id=track_run_id,
        module_run_id=module_run_id,
        finding_type=record.finding_type,
        payload=record.payload,
        confidence=record.confidence,
        collection_mode=collection_mode,
        source_name=record.source_name,
        observed_at=record.observed_at,
        collected_at=now(),
    )
    finding.add_evidence(
        Evidence(
            source=record.source_name,
            collected_at=finding.collected_at,
            reference=record.evidence_reference,
        )
    )
    return finding
