# Copyright (c) 2026 kraynux - Licence MIT
"""Creation de profil (critere de sortie Phase 4)."""
import sqlite3
from datetime import datetime, timezone

from omega_track.domain.entities.track_profile import ExecutionLimits, NeoTraceOptions, TrackProfile
from omega_track.domain.value_objects.identifiers import TrackProfileId
from omega_track.infrastructure.repositories.sqlite.track_profile_repository import (
    SqliteTrackProfileRepository,
)

_NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)


def _profile(**overrides) -> TrackProfile:
    defaults = {
        "id": TrackProfileId("p1"),
        "name": "default",
        "modules": {"dns", "rdap", "neotrace"},
        "created_at": _NOW,
        "updated_at": _NOW,
    }
    defaults.update(overrides)
    return TrackProfile(**defaults)


def test_save_and_get_round_trips_modules_and_options(connection: sqlite3.Connection) -> None:
    repo = SqliteTrackProfileRepository(connection)
    profile = _profile(
        neotrace=NeoTraceOptions(protocol="udp", max_hops=20),
        limits=ExecutionLimits(max_ipv4_enriched=3),
        is_default=True,
    )
    repo.save(profile)

    fetched = repo.get(TrackProfileId("p1"))
    assert fetched is not None
    assert fetched.modules == {"dns", "rdap", "neotrace"}
    assert fetched.neotrace.protocol == "udp"
    assert fetched.neotrace.max_hops == 20
    assert fetched.limits.max_ipv4_enriched == 3
    assert fetched.is_default is True


def test_get_default_returns_the_default_profile(connection: sqlite3.Connection) -> None:
    repo = SqliteTrackProfileRepository(connection)
    repo.save(_profile(id=TrackProfileId("p1"), is_default=False))
    repo.save(_profile(id=TrackProfileId("p2"), name="full", is_default=True))

    default = repo.get_default()
    assert default is not None
    assert default.id == TrackProfileId("p2")


def test_get_default_returns_none_when_no_default_set(connection: sqlite3.Connection) -> None:
    repo = SqliteTrackProfileRepository(connection)
    repo.save(_profile())
    assert repo.get_default() is None


def test_list_all_returns_every_profile(connection: sqlite3.Connection) -> None:
    repo = SqliteTrackProfileRepository(connection)
    repo.save(_profile(id=TrackProfileId("p1"), name="a"))
    repo.save(_profile(id=TrackProfileId("p2"), name="b"))
    assert len(repo.list_all()) == 2


def test_delete_removes_profile(connection: sqlite3.Connection) -> None:
    repo = SqliteTrackProfileRepository(connection)
    repo.save(_profile())
    repo.delete(TrackProfileId("p1"))
    assert repo.get(TrackProfileId("p1")) is None
