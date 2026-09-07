# Copyright (c) 2026 kraynux - Licence MIT
"""Famille de findings 'organization' (plan de dev §4.3, Phase 13) :
emails publics, domaines associes, depots publics, comptes officiels.

`observed` et `inferred` ne sont jamais confondus (Phase 13) - un email
trouve tel quel (`PUBLIC_EMAIL_OBSERVED`) et un email deduit d'un pattern
(`PUBLIC_EMAIL_INFERRED`) sont deux types distincts, pas juste une
metadonnee sur le meme type."""
from __future__ import annotations

from enum import Enum


class OrganizationFindingType(str, Enum):
    PUBLIC_EMAIL_OBSERVED = "organization.public_email_observed"
    PUBLIC_EMAIL_INFERRED = "organization.public_email_inferred"
    REPOSITORY = "organization.repository"
    OFFICIAL_ACCOUNT = "organization.official_account"
    """Exige une preuve de relation explicite (Phase 13) - jamais une
    simple ressemblance de nom."""
    JOB_POSTING = "organization.job_posting"
