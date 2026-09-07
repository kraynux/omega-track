# Copyright (c) 2026 kraynux - Licence MIT
"""Exceptions du bounded context profil de track."""
from __future__ import annotations


class ProfileError(Exception):
    """Base commune, jamais levee directement."""


class UnknownModuleError(ProfileError):
    """Le profil reference un module inconnu du registre (voir
    domain/entities/track_profile.py::KNOWN_MODULES)."""
