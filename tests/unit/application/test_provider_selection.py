# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from omega_track.application.policies.provider_selection import resolve_active_geoip_provider


def test_defaults_to_dbip_when_unset() -> None:
    assert resolve_active_geoip_provider(None) == "dbip"


def test_defaults_to_dbip_when_invalid() -> None:
    assert resolve_active_geoip_provider("bogus") == "dbip"


def test_keeps_valid_configured_provider() -> None:
    assert resolve_active_geoip_provider("maxmind") == "maxmind"
    assert resolve_active_geoip_provider("dbip") == "dbip"
