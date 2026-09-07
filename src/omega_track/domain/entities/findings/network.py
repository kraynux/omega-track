# Copyright (c) 2026 kraynux - Licence MIT
"""Famille de findings 'network' (plan de dev §4.3) : IP, ASN, netblock,
hebergeur, BGP, geolocalisation."""
from __future__ import annotations

from enum import Enum


class NetworkFindingType(str, Enum):
    IP_OBSERVED = "network.ip_observed"
    """IP hors budget d'enrichissement (D-012) : finding brut, pas de
    GeoIP/RDAP associe."""
    ASN = "network.asn"
    """ASN commun entre deux IPs : toujours ce finding brut, jamais une
    Relation automatique seul (D-011, angle mort 2)."""
    NETBLOCK = "network.netblock"
    GEOLOCATION = "network.geolocation"
    HOSTING_PROVIDER = "network.hosting_provider"
