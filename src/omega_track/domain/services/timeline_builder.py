# Copyright (c) 2026 kraynux - Licence MIT
"""Construction de la timeline de changements entre deux TrackRun de la
meme cible (D-013 : `track replay`, plan de dev §5.2 "comparaison d'un
TrackRun avec le precedent"). Pur - compare deux jeux de findings deja
en memoire, ne lit jamais la base lui-meme."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from omega_track.domain.entities.findings.base import Finding


@dataclass(frozen=True, slots=True)
class FieldChange:
    finding_type: str
    previous_payload: dict[str, Any] | None
    current_payload: dict[str, Any] | None

    @property
    def is_addition(self) -> bool:
        return self.previous_payload is None and self.current_payload is not None

    @property
    def is_removal(self) -> bool:
        return self.previous_payload is not None and self.current_payload is None


def build_field_changes(previous: list[Finding], current: list[Finding]) -> list[FieldChange]:
    """Compare par `finding_type` - une conversion naive, un meme type
    present plusieurs fois (ex. plusieurs enregistrements A) n'est comparee
    qu'au niveau agrege des payloads presents, pas champ par champ a
    l'interieur d'un type (suffisant pour le MVP de comparaison, a affiner
    seulement si un besoin reel de diff plus fin apparait)."""
    previous_by_type: dict[str, dict[str, Any]] = {f.finding_type: f.payload for f in previous}
    current_by_type: dict[str, dict[str, Any]] = {f.finding_type: f.payload for f in current}

    changes = []
    for finding_type in sorted(set(previous_by_type) | set(current_by_type)):
        previous_payload = previous_by_type.get(finding_type)
        current_payload = current_by_type.get(finding_type)
        if previous_payload != current_payload:
            changes.append(FieldChange(finding_type, previous_payload, current_payload))
    return changes
