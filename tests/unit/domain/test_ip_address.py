# Copyright (c) 2026 kraynux - Licence MIT
import pytest

from omega_track.domain.exceptions.target import InvalidTargetValueError
from omega_track.domain.value_objects.ip_address import IPAddress


def test_parses_ipv4() -> None:
    ip = IPAddress.parse("203.0.113.10")
    assert ip.version == 4
    assert str(ip) == "203.0.113.10"


def test_parses_ipv6() -> None:
    ip = IPAddress.parse("2001:db8::1")
    assert ip.version == 6


def test_strips_whitespace() -> None:
    assert IPAddress.parse("  203.0.113.10  ").version == 4


def test_invalid_ip_raises() -> None:
    with pytest.raises(InvalidTargetValueError):
        IPAddress.parse("not-an-ip")


def test_private_ip_detected() -> None:
    assert IPAddress.parse("192.168.1.1").is_private
    assert not IPAddress.parse("192.168.1.1").is_public


def test_loopback_detected() -> None:
    assert IPAddress.parse("127.0.0.1").is_loopback
    assert not IPAddress.parse("127.0.0.1").is_public


def test_link_local_detected() -> None:
    assert IPAddress.parse("169.254.1.1").is_link_local


def test_public_ip_detected() -> None:
    # 203.0.113.0/24 est le bloc RFC 5737 reserve a la documentation - la
    # stdlib `ipaddress` le classe lui-meme comme is_private=True (non
    # routable globalement), donc inutilisable ici comme exemple d'IP
    # publique malgre son usage frequent ailleurs dans ce projet comme IP
    # "generique" de test. 1.1.1.1 est une vraie IP publique routee.
    ip = IPAddress.parse("1.1.1.1")
    assert ip.is_public
    assert not ip.is_private


def test_documentation_range_is_not_public() -> None:
    """RFC 5737 (TEST-NET-3) : reserve a la documentation, jamais
    globalement routable - la stdlib le classe is_private=True."""
    ip = IPAddress.parse("203.0.113.10")
    assert not ip.is_public
    assert ip.is_private


def test_equality_and_hash() -> None:
    a = IPAddress.parse("203.0.113.10")
    b = IPAddress.parse("203.0.113.10")
    assert a == b
    assert hash(a) == hash(b)
