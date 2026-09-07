# Copyright (c) 2026 kraynux - Licence MIT
"""Use case : choisir et persister le theme actif (Phase 11, meme
convention que CHECK/DEEP/FOLD - D-008)."""
from __future__ import annotations

from omega_lib.theme.policies import TUI_THEMES

from omega_track.application.exceptions import UnknownThemeError
from omega_track.ports.repositories.settings_repository import SettingsRepository

_THEME_KEY = "theme"


def select_theme(*, settings_repository: SettingsRepository, theme_name: str) -> None:
    if theme_name not in TUI_THEMES:
        raise UnknownThemeError(theme_name)
    settings_repository.set(_THEME_KEY, theme_name)
