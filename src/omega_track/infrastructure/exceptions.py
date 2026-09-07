# Copyright (c) 2026 kraynux - Licence MIT
"""Racine des erreurs de la couche infrastructure (adaptateurs concrets),
meme convention que CHECK."""
from __future__ import annotations

from omega_track.core.errors import OmegaTrackError


class InfrastructureError(OmegaTrackError):
    """Racine des erreurs techniques d'infrastructure. Toute exception
    specifique a une technologie (sqlite3.Error, OSError...) est traduite
    vers un sous-type de celle-ci par l'adaptateur concerne, jamais
    laissee franchir la frontiere d'un port brute."""


class StorageError(InfrastructureError):
    """Erreur de persistance, traduite depuis sqlite3.Error ou une
    erreur d'ecriture de fichier."""
