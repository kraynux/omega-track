# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone

import pytest

from omega_track.application.commands.targets.create_target import create_target
from omega_track.application.commands.targets.delete_targets import delete_targets
from omega_track.application.commands.targets.pin_target import pin_target
from omega_track.application.commands.targets.update_target import update_target
from omega_track.application.exceptions import TargetNotFoundError
from omega_track.domain.entities.target import Target
from omega_track.domain.exceptions.target import DuplicateTargetError
from omega_track.domain.value_objects.identifiers import TargetId
from omega_track.domain.value_objects.target_value import TargetValue

_NOW = datetime(2026, 9, 6, tzinfo=timezone.utc)


class _FakeTargetRepository:
    def __init__(self) -> None:
        self._targets: dict[TargetId, Target] = {}

    def save(self, target: Target) -> None:
        self._targets[target.id] = target

    def get(self, target_id: TargetId) -> Target | None:
        return self._targets.get(target_id)

    def find_by_value(self, value: TargetValue) -> Target | None:
        return next((t for t in self._targets.values() if t.value == value), None)

    def list_all(self) -> list[Target]:
        return list(self._targets.values())

    def delete(self, target_id: TargetId) -> None:
        self._targets.pop(target_id, None)


def _id_factory() -> Callable[[], str]:
    counter = iter(f"id-{n}" for n in range(1, 1000))
    return counter.__next__


def test_create_target_normalizes_and_persists() -> None:
    repo = _FakeTargetRepository()
    target = create_target(
        target_repository=repo, raw_value="EXAMPLE.com", alias="  Mon Site  ", tags={"Prod"},
        id_factory=_id_factory(), now=lambda: _NOW,
    )
    assert str(target.value) == "example.com"
    assert target.alias == "Mon Site"
    assert target.tags == {"prod"}
    assert repo.get(target.id) is target


def test_create_target_rejects_duplicates() -> None:
    repo = _FakeTargetRepository()
    create_target(target_repository=repo, raw_value="example.com", id_factory=_id_factory(), now=lambda: _NOW)
    with pytest.raises(DuplicateTargetError):
        create_target(target_repository=repo, raw_value="example.com", id_factory=_id_factory(), now=lambda: _NOW)


def test_update_target_changes_alias_and_tags() -> None:
    repo = _FakeTargetRepository()
    target = create_target(target_repository=repo, raw_value="example.com", id_factory=_id_factory(), now=lambda: _NOW)

    updated = update_target(
        target_repository=repo, target_id=target.id, alias="nouveau", add_tags={"important"},
        now=lambda: _NOW,
    )
    assert updated.alias == "nouveau"
    assert "important" in updated.tags


def test_update_target_raises_when_missing() -> None:
    repo = _FakeTargetRepository()
    with pytest.raises(TargetNotFoundError):
        update_target(target_repository=repo, target_id=TargetId("missing"), now=lambda: _NOW)


def test_pin_target_marks_authorized() -> None:
    repo = _FakeTargetRepository()
    target = create_target(target_repository=repo, raw_value="example.com", id_factory=_id_factory(), now=lambda: _NOW)
    assert not target.is_authorized()

    pinned = pin_target(target_repository=repo, target_id=target.id, now=lambda: _NOW)
    assert pinned.is_authorized()


def test_pin_target_raises_when_missing() -> None:
    repo = _FakeTargetRepository()
    with pytest.raises(TargetNotFoundError):
        pin_target(target_repository=repo, target_id=TargetId("missing"), now=lambda: _NOW)


def test_delete_targets_is_idempotent_for_unknown_ids() -> None:
    repo = _FakeTargetRepository()
    target = create_target(target_repository=repo, raw_value="example.com", id_factory=_id_factory(), now=lambda: _NOW)

    delete_targets(target_repository=repo, target_ids=[target.id, TargetId("unknown")])
    assert repo.get(target.id) is None
