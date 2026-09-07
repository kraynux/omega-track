# Copyright (c) 2026 kraynux - Licence MIT
from datetime import datetime, timezone

from omega_track.domain.entities.target import Target
from omega_track.domain.value_objects.identifiers import TargetId
from omega_track.domain.value_objects.target_value import TargetKind, parse_target_value

_NOW = datetime(2026, 1, 1, tzinfo=timezone.utc)
_LATER = datetime(2026, 1, 2, tzinfo=timezone.utc)


def _target(**overrides) -> Target:
    defaults = {
        "id": TargetId("target-1"),
        "value": parse_target_value("example.com"),
        "created_at": _NOW,
        "updated_at": _NOW,
    }
    defaults.update(overrides)
    return Target(**defaults)


def test_kind_reflects_target_value() -> None:
    assert _target().kind == TargetKind.DOMAIN
    assert _target(value=parse_target_value("203.0.113.10")).kind == TargetKind.IP


def test_not_authorized_by_default() -> None:
    assert not _target().is_authorized()


def test_pin_authorizes_and_updates_timestamp() -> None:
    target = _target()
    target.pin(now=_LATER)
    assert target.is_authorized()
    assert target.updated_at == _LATER


def test_unpin_revokes_authorization() -> None:
    target = _target(pinned=True)
    target.unpin(now=_LATER)
    assert not target.is_authorized()


def test_add_and_remove_tag() -> None:
    target = _target()
    target.add_tag("infra", now=_LATER)
    assert "infra" in target.tags
    target.remove_tag("infra", now=_LATER)
    assert "infra" not in target.tags


def test_record_track_updates_last_status() -> None:
    target = _target()
    target.record_track(status="completed", now=_LATER)
    assert target.last_status == "completed"
    assert target.last_track_at == _LATER
