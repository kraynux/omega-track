# Copyright (c) 2026 kraynux - Licence MIT
"""Reexport depuis omega_lib (D-005) : implementation de production de
l'horloge, utilisee a la frontiere presentation/application. domain/ et
application/ ne l'appellent jamais elles-memes, elles recoivent toujours
`now` explicitement en parametre (meme convention que CHECK/DEEP/FOLD)."""
from __future__ import annotations

from omega_lib.shared.clock import utc_now

__all__ = ["utc_now"]
