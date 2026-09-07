# Copyright (c) 2026 kraynux - Licence MIT
"""Famille de findings 'dns' (plan de dev §4.3) : enregistrements DNS,
PTR, DNSSEC, CAA, observations passives."""
from __future__ import annotations

from enum import Enum


class DnsFindingType(str, Enum):
    A_RECORD = "dns.a_record"
    AAAA_RECORD = "dns.aaaa_record"
    PTR_RECORD = "dns.ptr_record"
    CNAME_RECORD = "dns.cname_record"
    MX_RECORD = "dns.mx_record"
    TXT_RECORD = "dns.txt_record"
    DNSSEC = "dns.dnssec"
    CAA_RECORD = "dns.caa_record"
    PASSIVE_SUBDOMAIN = "dns.passive_subdomain"
    """Sous-domaine observe passivement via CT logs (Phase 10) - jamais
    via brute-force (hors perimetre, §1.2)."""
