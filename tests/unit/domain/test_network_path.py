# Copyright (c) 2026 kraynux - Licence MIT
from omega_track.domain.entities.findings.path import NetworkHop, NetworkPath
from omega_track.domain.value_objects.ip_address import IPAddress


def test_non_responding_hop_has_no_ip() -> None:
    hop = NetworkHop(sequence=1, ip=None)
    assert not hop.is_responding


def test_responding_hop_has_ip() -> None:
    hop = NetworkHop(sequence=1, ip=IPAddress.parse("203.0.113.1"))
    assert hop.is_responding


def test_reached_target_when_last_hop_matches() -> None:
    target = IPAddress.parse("203.0.113.10")
    path = NetworkPath(
        target_ip=target, protocol="icmp",
        hops=[NetworkHop(sequence=1, ip=IPAddress.parse("203.0.113.1")), NetworkHop(sequence=2, ip=target)],
    )
    assert path.reached_target


def test_not_reached_when_last_hop_differs() -> None:
    path = NetworkPath(
        target_ip=IPAddress.parse("203.0.113.10"), protocol="icmp",
        hops=[NetworkHop(sequence=1, ip=IPAddress.parse("203.0.113.1"))],
    )
    assert not path.reached_target


def test_non_responding_count() -> None:
    path = NetworkPath(
        target_ip=IPAddress.parse("203.0.113.10"), protocol="icmp",
        hops=[NetworkHop(sequence=1, ip=None), NetworkHop(sequence=2, ip=None), NetworkHop(sequence=3, ip=IPAddress.parse("203.0.113.10"))],
    )
    assert path.non_responding_count == 2


def test_average_rtt_ignores_non_responding_hops() -> None:
    path = NetworkPath(
        target_ip=IPAddress.parse("203.0.113.10"), protocol="icmp",
        hops=[
            NetworkHop(sequence=1, ip=None, rtt_ms=None),
            NetworkHop(sequence=2, ip=IPAddress.parse("203.0.113.1"), rtt_ms=10.0),
            NetworkHop(sequence=3, ip=IPAddress.parse("203.0.113.10"), rtt_ms=20.0),
        ],
    )
    assert path.average_rtt_ms == 15.0


def test_average_rtt_none_when_no_measurements() -> None:
    path = NetworkPath(target_ip=IPAddress.parse("203.0.113.10"), protocol="icmp", hops=[NetworkHop(sequence=1, ip=None)])
    assert path.average_rtt_ms is None
