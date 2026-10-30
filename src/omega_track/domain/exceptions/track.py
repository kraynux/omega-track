# Copyright (c) 2026 kraynux - Licence MIT
"""Exceptions du bounded context TrackRun."""
from __future__ import annotations

from omega_track.shared.i18n import _


class TrackError(Exception):
    """Base commune, jamais levee directement."""


class InvalidTrackTransitionError(TrackError):
    """Transition d'etat non autorisee (voir domain/value_objects/statuses.py
    ::is_valid_transition, Phase 7 §"Etats attendus")."""

    def __init__(self, current: str, attempted: str) -> None:
        super().__init__(_("transition {current!r} -> {attempted!r} non autorisée").format(current=current, attempted=attempted))
        self.current = current
        self.attempted = attempted


class TargetNotAuthorizedError(TrackError):
    """D-010 : aucun TrackRun ne demarre sur une cible non epinglee-
    autorisee sans confirmation explicite. Levee par le garde applicatif
    (Phase 3+9), pas par le domaine lui-meme (le domaine ne connait pas la
    notion de confirmation CLI/TUI) - conservee ici car c'est le vocabulaire
    du bounded context track, pas un detail d'interface."""
