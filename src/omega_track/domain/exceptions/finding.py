# Copyright (c) 2026 kraynux - Licence MIT
"""Exceptions du bounded context finding."""
from __future__ import annotations


class FindingError(Exception):
    """Base commune, jamais levee directement."""


class InvalidFindingPayloadError(FindingError):
    """Le payload d'un finding ne correspond pas au schema attendu pour
    son `finding_type` (voir domain/entities/findings/base.py)."""
