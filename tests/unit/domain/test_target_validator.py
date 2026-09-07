# Copyright (c) 2026 kraynux - Licence MIT
import pytest

from omega_track.domain.exceptions.target import InvalidTargetValueError
from omega_track.domain.services.target_validator import validate_alias, validate_tag


def test_none_alias_passes_through() -> None:
    assert validate_alias(None) is None


def test_empty_alias_becomes_none() -> None:
    assert validate_alias("   ") is None


def test_alias_stripped() -> None:
    assert validate_alias("  prod server  ") == "prod server"


def test_alias_too_long_rejected() -> None:
    with pytest.raises(InvalidTargetValueError):
        validate_alias("a" * 129)


def test_tag_normalized_lowercase() -> None:
    assert validate_tag("  Infra  ") == "infra"


def test_empty_tag_rejected() -> None:
    with pytest.raises(InvalidTargetValueError):
        validate_tag("   ")


def test_tag_too_long_rejected() -> None:
    with pytest.raises(InvalidTargetValueError):
        validate_tag("a" * 65)
