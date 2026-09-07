# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from omega_track.application.guards.authorization_guard import ensure_target_authorized
from omega_track.domain.entities.target import Target
from omega_track.domain.exceptions.track import TargetNotAuthorizedError
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.domain.value_objects.identifiers import TargetId

_NOW = datetime(2026, 9, 6, tzinfo=timezone.utc)


def _target(*, pinned: bool) -> Target:
    target = Target(id=TargetId("t1"), value=DomainName.parse("example.com"), created_at=_NOW, updated_at=_NOW)
    if pinned:
        target.pin(now=_NOW)
    return target


def test_pinned_target_is_authorized_without_explicit_flag() -> None:
    ensure_target_authorized(_target(pinned=True), explicit_authorization=False)


def test_unpinned_target_authorized_with_explicit_flag() -> None:
    ensure_target_authorized(_target(pinned=False), explicit_authorization=True)


def test_unpinned_target_without_flag_raises() -> None:
    with pytest.raises(TargetNotAuthorizedError):
        ensure_target_authorized(_target(pinned=False), explicit_authorization=False)
