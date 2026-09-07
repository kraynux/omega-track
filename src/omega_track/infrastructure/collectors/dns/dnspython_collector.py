# Copyright (c) 2026 kraynux - Licence MIT
"""Implementation reelle de DnsCollector (Phase 6) - resolveur systeme
par defaut (D-014, angle mort 5) : `dns.resolver.resolve` utilise le
resolveur global par defaut de dnspython, qui lit lui-meme
/etc/resolv.conf (Linux) ou le registre (Windows) - aucun resolveur
public code en dur ici.

`resolve_fn` est injectable (meme convention que clock/id_factory,
MmdbReader.opener en Phase 5) : les tests passent des fixtures simples
(de simples chaines, puisque `str(rdata)` est tout ce que ce module lit -
voir docstrings des extracteurs), jamais un vrai resolveur reseau."""
from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import datetime
from typing import Any

import dns.exception
import dns.resolver

from omega_track.application.exceptions import CollectorUnavailableError
from omega_track.core.enums import ConfidenceLevel
from omega_track.domain.entities.findings.dns import DnsFindingType
from omega_track.domain.value_objects.collected_record import CollectedRecord
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.domain.value_objects.ip_address import IPAddress
from omega_track.infrastructure.collectors.dns._ptr_lookup import lookup_ptr

ResolveFn = Callable[[str, str], Iterable[Any]]

SOURCE_NAME = "dns"


def _default_resolve(qname: str, rdtype: str) -> Iterable[Any]:
    return dns.resolver.resolve(qname, rdtype)


class DnsPythonCollector:
    """Implemente ports/collectors/dns_collector.py::DnsCollector."""

    def __init__(
        self,
        *,
        now: Callable[[], datetime],
        resolve_fn: ResolveFn = _default_resolve,
    ) -> None:
        self._now = now
        self._resolve_fn = resolve_fn

    def resolve(self, domain: DomainName) -> list[CollectedRecord]:
        name = str(domain)
        records: list[CollectedRecord] = []
        records += self._query(name, "A", DnsFindingType.A_RECORD, lambda text: {"address": text})
        records += self._query(name, "AAAA", DnsFindingType.AAAA_RECORD, lambda text: {"address": text})
        records += self._query(
            name, "CNAME", DnsFindingType.CNAME_RECORD, lambda text: {"target": text.rstrip(".")}
        )
        records += self._query(name, "MX", DnsFindingType.MX_RECORD, _parse_mx)
        records += self._query(name, "TXT", DnsFindingType.TXT_RECORD, _parse_txt)
        records += self._query(name, "CAA", DnsFindingType.CAA_RECORD, _parse_caa)
        records += self._query_dnssec(name)
        return records

    def reverse_lookup(self, ip: IPAddress) -> CollectedRecord | None:
        hostname = lookup_ptr(ip, resolve_fn=self._resolve_fn)
        if hostname is None:
            return None
        return CollectedRecord(
            finding_type=DnsFindingType.PTR_RECORD.value,
            payload={"hostname": hostname},
            confidence=ConfidenceLevel.VERIFIED,
            source_name=SOURCE_NAME,
            observed_at=self._now(),
        )

    def _query(
        self,
        name: str,
        rdtype: str,
        finding_type: DnsFindingType,
        to_payload: Callable[[str], dict[str, Any]],
    ) -> list[CollectedRecord]:
        try:
            answer = self._resolve_fn(name, rdtype)
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            return []
        except (dns.exception.Timeout, dns.resolver.NoNameservers) as exc:
            raise CollectorUnavailableError(SOURCE_NAME, str(exc)) from exc
        now = self._now()
        return [
            CollectedRecord(
                finding_type=finding_type.value,
                payload=to_payload(str(rdata)),
                confidence=ConfidenceLevel.VERIFIED,
                source_name=SOURCE_NAME,
                observed_at=now,
            )
            for rdata in answer
        ]

    def _query_dnssec(self, name: str) -> list[CollectedRecord]:
        try:
            answer = self._resolve_fn(name, "DNSKEY")
        except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
            return []
        except (dns.exception.Timeout, dns.resolver.NoNameservers) as exc:
            raise CollectorUnavailableError(SOURCE_NAME, str(exc)) from exc
        if not list(answer):
            return []
        return [
            CollectedRecord(
                finding_type=DnsFindingType.DNSSEC.value,
                payload={"enabled": True},
                confidence=ConfidenceLevel.VERIFIED,
                source_name=SOURCE_NAME,
                observed_at=self._now(),
            )
        ]


def _parse_mx(text: str) -> dict[str, Any]:
    preference, _, exchange = text.partition(" ")
    return {"preference": int(preference), "exchange": exchange.rstrip(".")}


def _parse_txt(text: str) -> dict[str, Any]:
    stripped = text[1:-1] if text.startswith('"') and text.endswith('"') else text
    return {"text": stripped}


def _parse_caa(text: str) -> dict[str, Any]:
    flags, _, remainder = text.partition(" ")
    tag, _, value = remainder.partition(" ")
    return {"flags": int(flags), "tag": tag, "value": value.strip('"')}
