# Copyright (c) 2026 kraynux - Licence MIT
"""Famille de findings 'identity' (plan de dev §4.3) : RDAP/WHOIS,
registrar, dates, contacts, nameservers."""
from __future__ import annotations

from enum import Enum


class IdentityFindingType(str, Enum):
    REGISTRAR = "identity.registrar"
    REGISTRANT_CONTACT = "identity.registrant_contact"
    CREATION_DATE = "identity.creation_date"
    EXPIRATION_DATE = "identity.expiration_date"
    UPDATED_DATE = "identity.updated_date"
    NAMESERVER = "identity.nameserver"
