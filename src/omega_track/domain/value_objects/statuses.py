# Copyright (c) 2026 kraynux - Licence MIT
"""Statuts et machines a etats de TrackRun/module (plan de dev §4.2,
Phase 7 "Etats attendus") + politique de redaction (§4.2)."""
from __future__ import annotations

from enum import Enum


class TrackStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    PARTIAL = "partial"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ModuleStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    PARTIAL = "partial"
    SKIPPED = "skipped"
    FAILED = "failed"
    CANCELLED = "cancelled"


class RedactionPolicy(str, Enum):
    NONE = "none"
    CONTACTS_ONLY = "contacts_only"
    SENSITIVE_ONLY = "sensitive_only"
    STRICT = "strict"


_TRACK_TRANSITIONS: dict[TrackStatus, frozenset[TrackStatus]] = {
    TrackStatus.QUEUED: frozenset({TrackStatus.RUNNING, TrackStatus.CANCELLED}),
    TrackStatus.RUNNING: frozenset(
        {TrackStatus.COMPLETED, TrackStatus.PARTIAL, TrackStatus.FAILED, TrackStatus.CANCELLED}
    ),
    TrackStatus.PARTIAL: frozenset(),
    TrackStatus.COMPLETED: frozenset(),
    TrackStatus.FAILED: frozenset(),
    TrackStatus.CANCELLED: frozenset(),
}

_MODULE_TRANSITIONS: dict[ModuleStatus, frozenset[ModuleStatus]] = {
    ModuleStatus.PENDING: frozenset({ModuleStatus.RUNNING, ModuleStatus.SKIPPED}),
    ModuleStatus.RUNNING: frozenset(
        {ModuleStatus.COMPLETED, ModuleStatus.PARTIAL, ModuleStatus.FAILED, ModuleStatus.CANCELLED}
    ),
    ModuleStatus.COMPLETED: frozenset(),
    ModuleStatus.PARTIAL: frozenset(),
    ModuleStatus.SKIPPED: frozenset(),
    ModuleStatus.FAILED: frozenset(),
    ModuleStatus.CANCELLED: frozenset(),
}


def is_valid_track_transition(current: TrackStatus, attempted: TrackStatus) -> bool:
    return attempted in _TRACK_TRANSITIONS[current]


def is_terminal_track_status(status: TrackStatus) -> bool:
    return not _TRACK_TRANSITIONS[status]


def is_valid_module_transition(current: ModuleStatus, attempted: ModuleStatus) -> bool:
    return attempted in _MODULE_TRANSITIONS[current]


def is_terminal_module_status(status: ModuleStatus) -> bool:
    return not _MODULE_TRANSITIONS[status]
