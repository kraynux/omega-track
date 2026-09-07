# Copyright (c) 2026 kraynux - Licence MIT
import pytest

from omega_track.domain.exceptions.target import InvalidTargetValueError
from omega_track.domain.value_objects.asn import Asn


def test_valid_asn() -> None:
    asn = Asn(number=64512, organization="Example Org")
    assert str(asn) == "AS64512"


def test_negative_asn_rejected() -> None:
    with pytest.raises(InvalidTargetValueError):
        Asn(number=-1)


def test_asn_above_32bit_range_rejected() -> None:
    with pytest.raises(InvalidTargetValueError):
        Asn(number=4_294_967_296)


def test_max_32bit_asn_accepted() -> None:
    Asn(number=4_294_967_295)
