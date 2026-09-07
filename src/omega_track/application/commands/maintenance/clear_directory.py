# Copyright (c) 2026 kraynux - Licence MIT
"""Vide un dossier de fichiers non references en base (captures d'ecran,
exports) - plan de dev §9 "nettoyage", retour utilisateur Phase 12
("rajouter un bouton... supprimer les screenshots et a cote supprimer
les exports"). Suppression FICHIER uniquement : pour les exports, la
ligne `exports` (Phase 4) correspondante en base n'est pas retiree
(contrairement a cleanup_exports.py::delete_exports_for_runs, qui purge
les deux ensemble pour d'anciens runs precis) - ce bouton est un
nettoyage global "je veux liberer l'espace disque", pas un nettoyage
cible par run ; la table `exports` ne sert que de journal, aucun code ne
verifie que `output_path` existe encore avant de l'utiliser."""
from __future__ import annotations

from pathlib import Path


def clear_directory(directory: Path) -> int:
    if not directory.exists():
        return 0
    deleted = 0
    for entry in directory.iterdir():
        if entry.is_file():
            entry.unlink()
            deleted += 1
    return deleted
