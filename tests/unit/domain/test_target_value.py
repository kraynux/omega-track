# Copyright (c) 2026 kraynux - Licence MIT
import pytest

from omega_track.domain.exceptions.target import InvalidTargetValueError
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.domain.value_objects.ip_address import IPAddress
from omega_track.domain.value_objects.target_value import (
    TargetKind,
    parse_target_value,
    target_kind_of,
)


def test_parses_ipv4_target() -> None:
    value = parse_target_value("203.0.113.10")
    assert isinstance(value, IPAddress)
    assert target_kind_of(value) == TargetKind.IP


def test_parses_ipv6_target() -> None:
    value = parse_target_value("2001:db8::1")
    assert isinstance(value, IPAddress)


def test_parses_domain_target() -> None:
    value = parse_target_value("example.com")
    assert isinstance(value, DomainName)
    assert target_kind_of(value) == TargetKind.DOMAIN


def test_empty_target_rejected() -> None:
    with pytest.raises(InvalidTargetValueError):
        parse_target_value("   ")


def test_invalid_target_rejected() -> None:
    with pytest.raises(InvalidTargetValueError):
        parse_target_value("not a valid target !!")
