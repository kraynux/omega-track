# Copyright (c) 2026 kraynux - Licence MIT
"""CRUD cible complet (critere de sortie Phase 4)."""
import sqlite3
from datetime import datetime, timezone

from omega_track.domain.entities.target import Target
from omega_track.domain.value_objects.identifiers import TargetId
from omega_track.domain.value_objects.target_value import parse_target_value
from omega_track.infrastructure.repositories.sqlite.target_repository import SqliteTargetRepository

_NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)
_LATER = datetime(2026, 1, 2, tzinfo=timezone.utc)


def _target(**overrides) -> Target:
    defaults = {
        "id": TargetId("t1"),
        "value": parse_target_value("example.com"),
        "created_at": _NOW,
        "updated_at": _NOW,
    }
    defaults.update(overrides)
    return Target(**defaults)


def test_save_and_get_round_trips(connection: sqlite3.Connection) -> None:
    repo = SqliteTargetRepository(connection)
    target = _target(alias="prod", tags={"infra", "web"}, pinned=True)
    repo.save(target)

    fetched = repo.get(TargetId("t1"))
    assert fetched is not None
    assert fetched.alias == "prod"
    assert fetched.tags == {"infra", "web"}
    assert fetched.pinned is True
    assert str(fetched.value) == "example.com"


def test_get_unknown_id_returns_none(connection: sqlite3.Connection) -> None:
    repo = SqliteTargetRepository(connection)
    assert repo.get(TargetId("missing")) is None


def test_find_by_value_locates_existing_target(connection: sqlite3.Connection) -> None:
    repo = SqliteTargetRepository(connection)
    repo.save(_target())
    found = repo.find_by_value(parse_target_value("example.com"))
    assert found is not None
    assert found.id == TargetId("t1")


def test_find_by_value_distinguishes_ip_and_domain(connection: sqlite3.Connection) -> None:
    repo = SqliteTargetRepository(connection)
    repo.save(_target(id=TargetId("t-ip"), value=parse_target_value("203.0.113.10")))
    assert repo.find_by_value(parse_target_value("example.com")) is None


def test_save_twice_updates_rather_than_duplicates(connection: sqlite3.Connection) -> None:
    repo = SqliteTargetRepository(connection)
    repo.save(_target())
    repo.save(_target(alias="renamed", updated_at=_LATER))

    assert len(repo.list_all()) == 1
    assert repo.get(TargetId("t1")).alias == "renamed"  # type: ignore[union-attr]


def test_delete_removes_target(connection: sqlite3.Connection) -> None:
    repo = SqliteTargetRepository(connection)
    repo.save(_target())
    repo.delete(TargetId("t1"))
    assert repo.get(TargetId("t1")) is None


def test_list_all_orders_by_created_at_desc(connection: sqlite3.Connection) -> None:
    repo = SqliteTargetRepository(connection)
    repo.save(_target(id=TargetId("older"), created_at=_NOW))
    repo.save(_target(id=TargetId("newer"), value=parse_target_value("example.net"), created_at=_LATER))

    results = repo.list_all()
    assert [t.id for t in results] == [TargetId("newer"), TargetId("older")]
