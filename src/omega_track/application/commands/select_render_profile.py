# Copyright (c) 2026 kraynux - Licence MIT
"""Use case : surcharger (ou remettre en automatique) le profil de rendu
(Phase 11, meme convention que CHECK/DEEP/FOLD - D-008)."""
from __future__ import annotations

from omega_lib.terminal.models import RenderProfile

from omega_track.ports.repositories.settings_repository import SettingsRepository

_RENDER_PROFILE_OVERRIDE_KEY = "render_profile_override"


def select_render_profile(
    *, settings_repository: SettingsRepository, render_profile: RenderProfile | None
) -> None:
    settings_repository.set(_RENDER_PROFILE_OVERRIDE_KEY, render_profile.value if render_profile else "")
