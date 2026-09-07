# Copyright (c) 2026 kraynux - Licence MIT
"""Racine des erreurs OMEGA-TRACK - meme convention que CHECK
(`core/exceptions.py::OmegaCheckError`), nommee `errors.py` ici pour
coller au nom de fichier deja fixe par ARBORESCENCE.md."""
from __future__ import annotations


class OmegaTrackError(Exception):
    """Racine commune - jamais levee directement."""
