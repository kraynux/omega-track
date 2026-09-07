# Copyright (c) 2026 kraynux - Licence MIT
"""Trace d'un export genere (plan de dev §4.1)."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from omega_track.domain.value_objects.identifiers import ExportId, TrackRunId
from omega_track.domain.value_objects.statuses import RedactionPolicy


@dataclass(frozen=True, slots=True)
class ExportArtifact:
    id: ExportId
    track_run_id: TrackRunId
    format: str
    """'json'|'md'|'html'|'csv'|'dot'|'mermaid' (Phase 8)."""
    output_path: str
    checksum: str
    redaction_policy: RedactionPolicy
    created_at: datetime
