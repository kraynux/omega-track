# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from datetime import datetime, timezone

import dns.exception
import dns.resolver
import pytest

from omega_track.application.exceptions import CollectorUnavailableError
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.domain.value_objects.ip_address import IPAddress
from omega_track.infrastructure.collectors.dns.dnspython_collector import DnsPythonCollector

_NOW = datetime(2026, 9, 6, tzinfo=timezone.utc)
_DOMAIN = DomainName.parse("example.com")


class _FakeResolveFn:
    """Repond selon rdtype - imite `str(rdata)` de dnspython (voir
    docstring de dnspython_collector.py) : de simples chaines suffisent
    puisque le collecteur ne lit jamais que `str(x)`."""

    def __init__(self, answers: dict[str, list[str]]) -> None:
        self._answers = answers

    def __call__(self, name: str, rdtype: str) -> list[str]:
        if rdtype not in self._answers:
            raise dns.resolver.NoAnswer()
        return self._answers[rdtype]


def test_resolve_returns_records_for_every_available_type() -> None:
    resolve_fn = _FakeResolveFn(
        {
            "A": ["93.184.216.34"],
            "AAAA": ["2606:2800:220:1:248:1893:25c8:1946"],
            "MX": ["10 mail.example.com."],
            "TXT": ['"v=spf1 -all"'],
            "CAA": ['0 issue "letsencrypt.org"'],
        }
    )
    collector = DnsPythonCollector(now=lambda: _NOW, resolve_fn=resolve_fn)

    records = collector.resolve(_DOMAIN)

    by_type = {r.finding_type: r for r in records}
    assert by_type["dns.a_record"].payload == {"address": "93.184.216.34"}
    assert by_type["dns.aaaa_record"].payload == {"address": "2606:2800:220:1:248:1893:25c8:1946"}
    assert by_type["dns.mx_record"].payload == {"preference": 10, "exchange": "mail.example.com"}
    assert by_type["dns.txt_record"].payload == {"text": "v=spf1 -all"}
    assert by_type["dns.caa_record"].payload == {"flags": 0, "tag": "issue", "value": "letsencrypt.org"}
    assert "dns.cname_record" not in by_type
    assert "dns.dnssec" not in by_type


def test_resolve_returns_dnssec_when_dnskey_present() -> None:
    resolve_fn = _FakeResolveFn({"A": ["93.184.216.34"], "DNSKEY": ["257 3 8 AwEAA..."]})
    collector = DnsPythonCollector(now=lambda: _NOW, resolve_fn=resolve_fn)
    records = collector.resolve(_DOMAIN)
    dnssec = [r for r in records if r.finding_type == "dns.dnssec"]
    assert len(dnssec) == 1
    assert dnssec[0].payload == {"enabled": True}


def test_resolve_raises_collector_unavailable_on_timeout() -> None:
    def resolve_fn(name: str, rdtype: str) -> list[str]:
        raise dns.exception.Timeout()

    collector = DnsPythonCollector(now=lambda: _NOW, resolve_fn=resolve_fn)
    with pytest.raises(CollectorUnavailableError):
        collector.resolve(_DOMAIN)


def test_reverse_lookup_returns_hostname_without_trailing_dot() -> None:
    def resolve_fn(name: str, rdtype: str) -> list[str]:
        assert rdtype == "PTR"
        return ["host.example.com."]

    collector = DnsPythonCollector(now=lambda: _NOW, resolve_fn=resolve_fn)
    record = collector.reverse_lookup(IPAddress.parse("93.184.216.34"))
    assert record is not None
    assert record.payload == {"hostname": "host.example.com"}
    assert record.finding_type == "dns.ptr_record"


def test_reverse_lookup_returns_none_when_no_ptr() -> None:
    def resolve_fn(name: str, rdtype: str) -> list[str]:
        raise dns.resolver.NXDOMAIN()

    collector = DnsPythonCollector(now=lambda: _NOW, resolve_fn=resolve_fn)
    assert collector.reverse_lookup(IPAddress.parse("93.184.216.34")) is None


def test_all_records_share_verified_confidence() -> None:
    resolve_fn = _FakeResolveFn({"A": ["93.184.216.34"]})
    collector = DnsPythonCollector(now=lambda: _NOW, resolve_fn=resolve_fn)
    records = collector.resolve(_DOMAIN)
    assert all(r.confidence.value == "verified" for r in records)
    assert all(r.source_name == "dns" for r in records)
