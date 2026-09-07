# Copyright (c) 2026 kraynux - Licence MIT
"""Score de confiance global d'un ensemble de findings - une aide de
lecture, jamais un verdict de securite (plan de dev §4.4, principe
explicite : "le score global est une aide de lecture, jamais un verdict
de securite")."""
from __future__ import annotations

from omega_track.core.enums import ConfidenceLevel, confidence_strength
from omega_track.domain.entities.findings.base import Finding

_MAX_STRENGTH = confidence_strength(ConfidenceLevel.VERIFIED)


def score_findings(findings: list[Finding]) -> float:
    """0.0-1.0. Findings vides -> 0.0 (pas de division par zero, pas une
    absence de score interpretee comme "parfaitement confiant")."""
    if not findings:
        return 0.0
    total = sum(confidence_strength(f.confidence) for f in findings)
    return total / (len(findings) * _MAX_STRENGTH)
