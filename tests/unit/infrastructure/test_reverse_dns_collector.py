# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

import dns.resolver

from omega_track.domain.value_objects.ip_address import IPAddress
from omega_track.infrastructure.collectors.dns.reverse_dns_collector import (
    DnsPythonReverseDnsResolver,
)

_IP = IPAddress.parse("93.184.216.34")


def test_resolve_ptr_returns_hostname_without_trailing_dot() -> None:
    def resolve_fn(name: str, rdtype: str) -> list[str]:
        assert rdtype == "PTR"
        return ["host.example.com."]

    resolver = DnsPythonReverseDnsResolver(resolve_fn=resolve_fn)
    assert resolver.resolve_ptr(_IP) == "host.example.com"


def test_resolve_ptr_returns_none_when_absent() -> None:
    def resolve_fn(name: str, rdtype: str) -> list[str]:
        raise dns.resolver.NXDOMAIN()

    resolver = DnsPythonReverseDnsResolver(resolve_fn=resolve_fn)
    assert resolver.resolve_ptr(_IP) is None
