# Copyright (c) 2026 kraynux - Licence MIT
"""Reexport depuis omega_lib (D-008) : contrat deja identique a ce
qu'exige settings.json (point 3, tranche) - jamais redefini localement,
meme convention que ports/terminal_detector.py."""
from __future__ import annotations

from omega_lib.ports.settings_store import SettingsStore as SettingsRepository

__all__ = ["SettingsRepository"]
