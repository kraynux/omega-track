# Copyright (c) 2026 kraynux - Licence MIT
"""Politique de selection du fournisseur GeoIP actif (Phase 5) - pure,
sans port : replie silencieusement sur 'dbip' (gratuit, sans cle) si le
reglage est absent ou invalide, jamais une erreur bloquante au demarrage."""
from __future__ import annotations

_DEFAULT_PROVIDER = "dbip"
VALID_GEOIP_PROVIDERS = frozenset({"dbip", "maxmind"})


def resolve_active_geoip_provider(configured_provider: str | None) -> str:
    if configured_provider is not None and configured_provider in VALID_GEOIP_PROVIDERS:
        return configured_provider
    return _DEFAULT_PROVIDER
