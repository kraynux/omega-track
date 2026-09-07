# Copyright (c) 2026 kraynux - Licence MIT
"""Mecanique PTR partagee entre dnspython_collector.py (PTR de la cible,
persiste en Finding) et reverse_dns_collector.py (PTR d'un hop NeoTrace,
jamais persiste independamment) - prive (meme convention que
infrastructure/repositories/sqlite/_profile_serde.py)."""
from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import Any

import dns.exception
import dns.resolver
import dns.reversename

from omega_track.application.exceptions import CollectorUnavailableError
from omega_track.domain.value_objects.ip_address import IPAddress

ResolveFn = Callable[[str, str], Iterable[Any]]


def lookup_ptr(ip: IPAddress, *, resolve_fn: ResolveFn) -> str | None:
    reverse_name = str(dns.reversename.from_address(str(ip)))
    try:
        answer = resolve_fn(reverse_name, "PTR")
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        return None
    except (dns.exception.Timeout, dns.resolver.NoNameservers) as exc:
        raise CollectorUnavailableError("dns", str(exc)) from exc
    for rdata in answer:
        return str(rdata).rstrip(".")
    return None
