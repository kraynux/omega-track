# Copyright (c) 2026 kraynux - Licence MIT
"""Exceptions du bounded context cible - jamais une exception stdlib nue
(ValueError) qui obligerait l'appelant a deviner d'ou vient l'erreur."""
from __future__ import annotations


class TargetError(Exception):
    """Base commune, jamais levee directement."""


class InvalidTargetValueError(TargetError):
    """La chaine fournie n'est ni une IP (v4/v6) ni un nom de domaine
    valide (IDNA)."""


class DuplicateTargetError(TargetError):
    """Une cible avec la meme (normalized_value, target_kind) existe deja."""
