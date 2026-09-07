# Copyright (c) 2026 kraynux - Licence MIT
"""Reexport depuis omega_lib (D-005/D-006) : identifiant opaque UUID4,
utilise pour TargetId/TrackRunId/FindingId/ExportId - jamais un
auto-increment local (condition de la fusion Phase Suite)."""
from __future__ import annotations

from omega_lib.shared.ids import new_id

__all__ = ["new_id"]
