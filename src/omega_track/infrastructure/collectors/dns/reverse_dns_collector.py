# Copyright (c) 2026 kraynux - Licence MIT
"""Implementation reelle de ReverseDnsResolver (Phase 6) - annotation
legere des hops NeoTrace, jamais persistee independamment (voir
ports/services/reverse_dns_resolver.py). Resolveur systeme par defaut
(D-014), meme mecanique PTR que dnspython_collector.py::reverse_lookup
mais un port different (voir _ptr_lookup.py)."""
from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

import dns.resolver

from omega_track.domain.value_objects.ip_address import IPAddress
from omega_track.infrastructure.collectors.dns._ptr_lookup import lookup_ptr

ResolveFn = Callable[[str, str], Iterable[Any]]


def _default_resolve(qname: str, rdtype: str) -> Iterable[Any]:
    return dns.resolver.resolve(qname, rdtype)


class DnsPythonReverseDnsResolver:
    """Implemente ports/services/reverse_dns_resolver.py::ReverseDnsResolver."""

    def __init__(self, *, resolve_fn: ResolveFn = _default_resolve) -> None:
        self._resolve_fn = resolve_fn

    def resolve_ptr(self, ip: IPAddress) -> str | None:
        return lookup_ptr(ip, resolve_fn=self._resolve_fn)
