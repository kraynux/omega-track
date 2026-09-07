# Copyright (c) 2026 kraynux - Licence MIT
from datetime import datetime, timezone

import pytest

from omega_track.domain.entities.track_profile import TrackProfile
from omega_track.domain.exceptions.profile import UnknownModuleError
from omega_track.domain.value_objects.identifiers import TrackProfileId

_NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def test_valid_modules_accepted() -> None:
    profile = TrackProfile(
        id=TrackProfileId("p1"), name="default", modules={"dns", "rdap"},
        created_at=_NOW, updated_at=_NOW,
    )
    assert profile.enabled_mvp_modules() == {"dns", "rdap"}


def test_unknown_module_rejected() -> None:
    with pytest.raises(UnknownModuleError):
        TrackProfile(
            id=TrackProfileId("p1"), name="default", modules={"not-a-real-module"},
            created_at=_NOW, updated_at=_NOW,
        )


def test_extended_modules_split_from_mvp() -> None:
    profile = TrackProfile(
        id=TrackProfileId("p1"), name="full", modules={"dns", "certificate_transparency"},
        created_at=_NOW, updated_at=_NOW,
    )
    assert profile.enabled_mvp_modules() == {"dns"}
    assert profile.enabled_extended_modules() == {"certificate_transparency"}


def test_default_neotrace_and_limits_applied() -> None:
    profile = TrackProfile(
        id=TrackProfileId("p1"), name="default", modules=set(), created_at=_NOW, updated_at=_NOW,
    )
    assert profile.neotrace.protocol == "icmp"
    assert profile.limits.max_ipv4_enriched == 5
    assert profile.limits.max_neotrace_ips == 3
