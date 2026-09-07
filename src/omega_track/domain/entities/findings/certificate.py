# Copyright (c) 2026 kraynux - Licence MIT
"""Famille de findings 'certificate' (plan de dev §4.3) : certificats,
SAN, issuer, fenetres de validite, observations CT."""
from __future__ import annotations

from enum import Enum


class CertificateFindingType(str, Enum):
    CERTIFICATE_OBSERVED = "certificate.observed"
    """Un certificat vu dans un log CT (crt.sh, Phase 10) - jamais une
    connexion TLS live faite par TRACK lui-meme (hors perimetre)."""
    SUBJECT_ALTERNATIVE_NAME = "certificate.san"
