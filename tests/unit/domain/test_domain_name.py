# Copyright (c) 2026 kraynux - Licence MIT
import pytest

from omega_track.domain.exceptions.target import InvalidTargetValueError
from omega_track.domain.value_objects.domain_name import DomainName


def test_parses_simple_ascii_domain() -> None:
    d = DomainName.parse("Example.COM")
    assert d.ascii_form == "example.com"
    assert d.display_form == "example.com"


def test_strips_trailing_dot() -> None:
    d = DomainName.parse("example.com.")
    assert d.ascii_form == "example.com"


def test_idna_unicode_domain_normalized_to_punycode() -> None:
    d = DomainName.parse("café.fr")
    assert d.ascii_form == "xn--caf-dma.fr"
    assert d.display_form == "café.fr"


def test_empty_domain_rejected() -> None:
    with pytest.raises(InvalidTargetValueError):
        DomainName.parse("")


def test_empty_label_rejected() -> None:
    with pytest.raises(InvalidTargetValueError):
        DomainName.parse("example..com")


def test_label_too_long_rejected() -> None:
    with pytest.raises(InvalidTargetValueError):
        DomainName.parse("a" * 64 + ".com")


def test_label_with_leading_hyphen_rejected() -> None:
    with pytest.raises(InvalidTargetValueError):
        DomainName.parse("-example.com")


def test_str_returns_ascii_form() -> None:
    assert str(DomainName.parse("Example.com")) == "example.com"
