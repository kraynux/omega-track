# Copyright (c) 2026 kraynux - Licence MIT
"""Garde d'autorisation (D-010, angle mort 1) - meme mecanisme que
SCAN/DEEP : une cible epinglee (`Target.is_authorized()`) est deja
autorisee, sinon une confirmation explicite (`--authorize` CLI/case a
cocher TUI) est requise. Applique en tout premier par `start_track.py`/
`replay_track.py`, avant toute I/O reseau - jamais un simple
avertissement ignorable (plan de dev §9 "Criteres de sortie").

`TargetNotAuthorizedError` vit dans domain/exceptions/track.py (Phase 2,
deja anticipe pour ce garde) : c'est le vocabulaire du bounded context
track, pas un detail d'interface - le domaine ne connait pas la notion
de confirmation CLI/TUI, mais le TYPE d'erreur reste dans son
vocabulaire."""
from __future__ import annotations

from omega_track.domain.entities.target import Target
from omega_track.domain.exceptions.track import TargetNotAuthorizedError
from omega_track.shared.i18n import _


def ensure_target_authorized(target: Target, *, explicit_authorization: bool) -> None:
    if target.is_authorized() or explicit_authorization:
        return
    raise TargetNotAuthorizedError(_("cible non autorisée : {value} (épinglez-la ou passez "
                                     "--authorize)").format(value=target.value))
