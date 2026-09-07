# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from omega_track.application.exceptions import TargetNotFoundError
from omega_track.application.queries.get_target import get_target
from omega_track.application.queries.list_targets import list_targets
from omega_track.domain.entities.target import Target
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.domain.value_objects.identifiers import TargetId
from omega_track.domain.value_objects.target_value import TargetValue

_NOW = datetime(2026, 9, 6, tzinfo=timezone.utc)


class _FakeTargetRepository:
    def __init__(self, targets: list[Target]) -> None:
        self._targets = {t.id: t for t in targets}

    def save(self, target: Target) -> None:
        self._targets[target.id] = target

    def get(self, target_id: TargetId) -> Target | None:
        return self._targets.get(target_id)

    def find_by_value(self, value: TargetValue) -> Target | None:
        return None

    def list_all(self) -> list[Target]:
        return list(self._targets.values())

    def delete(self, target_id: TargetId) -> None:
        pass


def _target(target_id: str) -> Target:
    return Target(id=TargetId(target_id), value=DomainName.parse("example.com"), created_at=_NOW, updated_at=_NOW)


def test_list_targets_returns_all() -> None:
    repo = _FakeTargetRepository([_target("t1"), _target("t2")])
    assert {t.id for t in list_targets(target_repository=repo)} == {TargetId("t1"), TargetId("t2")}


def test_get_target_returns_existing() -> None:
    repo = _FakeTargetRepository([_target("t1")])
    assert get_target(target_repository=repo, target_id=TargetId("t1")).id == TargetId("t1")


def test_get_target_raises_when_missing() -> None:
    repo = _FakeTargetRepository([])
    with pytest.raises(TargetNotFoundError):
        get_target(target_repository=repo, target_id=TargetId("missing"))
