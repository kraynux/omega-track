# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from omega_track.infrastructure.collectors.network.traceroute_parser import (
    parse_traceroute_ipv4,
    parse_traceroute_ipv6,
)

_IPV4_OUTPUT = """\
traceroute to example.com (93.184.216.34), 30 hops max, 60 byte packets
 1  gateway (192.168.1.1)  1.234 ms  1.111 ms  1.098 ms
 2  * * *
 3  10.20.30.1 (10.20.30.1)  5.678 ms  5.432 ms  5.321 ms
 4  93.184.216.34 (93.184.216.34)  20.123 ms  19.876 ms  19.654 ms
"""

_IPV6_OUTPUT = """\
traceroute to example.com (2606:2800:220:1:248:1893:25c8:1946), 30 hops max
 1  gw6 (2001:db8::1)  1.234 ms  1.111 ms  1.098 ms
 2  * * *
 3  2606:2800:220:1:248:1893:25c8:1946 (2606:2800:220:1:248:1893:25c8:1946)  20.1 ms  19.9 ms  19.6 ms
"""


def test_ipv4_parses_responding_hops_with_hostname_and_rtt() -> None:
    hops = parse_traceroute_ipv4(_IPV4_OUTPUT)
    assert len(hops) == 4
    first = hops[0]
    assert first.sequence == 1
    assert str(first.ip) == "192.168.1.1"
    assert first.hostname == "gateway"
    assert first.rtt_ms == 1.234


def test_ipv4_parses_non_responding_hop_as_none_ip() -> None:
    hops = parse_traceroute_ipv4(_IPV4_OUTPUT)
    assert hops[1].ip is None
    assert not hops[1].is_responding


def test_ipv4_hop_without_reverse_dns_has_no_hostname() -> None:
    hops = parse_traceroute_ipv4(_IPV4_OUTPUT)
    last = hops[-1]
    assert str(last.ip) == "93.184.216.34"
    assert last.hostname is None


def test_ipv6_parses_responding_and_non_responding_hops() -> None:
    hops = parse_traceroute_ipv6(_IPV6_OUTPUT)
    assert len(hops) == 3
    assert str(hops[0].ip) == "2001:db8::1"
    assert hops[0].hostname == "gw6"
    assert hops[1].ip is None
    assert str(hops[2].ip) == "2606:2800:220:1:248:1893:25c8:1946"
    assert hops[2].hostname is None


def test_reached_target_true_when_last_hop_matches() -> None:
    from omega_track.domain.entities.findings.path import NetworkPath
    from omega_track.domain.value_objects.ip_address import IPAddress

    hops = parse_traceroute_ipv4(_IPV4_OUTPUT)
    path = NetworkPath(target_ip=IPAddress.parse("93.184.216.34"), protocol="icmp", hops=hops)
    assert path.reached_target
    assert path.non_responding_count == 1
