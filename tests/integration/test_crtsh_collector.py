# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from datetime import datetime, timezone

import httpx
import pytest

from omega_track.application.exceptions import CollectorUnavailableError
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.infrastructure.collectors.certificates.crtsh_collector import CrtShCollector

_NOW = datetime(2026, 9, 6, tzinfo=timezone.utc)

_ENTRIES = [
    {
        "id": 1,
        "serial_number": "abc123",
        "issuer_name": "Let's Encrypt",
        "not_before": "2026-01-01T00:00:00",
        "not_after": "2026-04-01T00:00:00",
        "entry_timestamp": "2026-01-02T00:00:00",
        "name_value": "example.com\nwww.example.com",
    },
    {
        "id": 2,
        "serial_number": "abc123",
        "issuer_name": "Let's Encrypt",
        "not_before": "2026-01-01T00:00:00",
        "not_after": "2026-04-01T00:00:00",
        "entry_timestamp": "2026-01-03T00:00:00",
        "name_value": "example.com\nwww.example.com",
    },
]


def _client(handler: httpx.MockTransport) -> httpx.Client:
    return httpx.Client(transport=handler)


def test_collect_certificates_produces_observed_and_san_findings() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert "crt.sh" in str(request.url)
        return httpx.Response(200, json=_ENTRIES)

    collector = CrtShCollector(http_client=_client(httpx.MockTransport(handler)), now=lambda: _NOW)
    records = collector.collect_certificates(DomainName.parse("example.com"))

    by_type: dict[str, list[dict]] = {}
    for record in records:
        by_type.setdefault(record.finding_type, []).append(record.payload)

    assert by_type["certificate.observed"] == [
        {"serial_number": "abc123", "issuer_name": "Let's Encrypt", "not_before": "2026-01-01T00:00:00", "not_after": "2026-04-01T00:00:00"}
    ]
    assert {"name": "example.com", "certificate_serial": "abc123"} in by_type["certificate.san"]
    assert {"name": "www.example.com", "certificate_serial": "abc123"} in by_type["certificate.san"]


def test_collect_certificates_flags_subdomains_as_passive_subdomains() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=_ENTRIES)

    collector = CrtShCollector(http_client=_client(httpx.MockTransport(handler)), now=lambda: _NOW)
    records = collector.collect_certificates(DomainName.parse("example.com"))

    passive_subdomains = [r.payload["name"] for r in records if r.finding_type == "dns.passive_subdomain"]
    assert passive_subdomains == ["www.example.com"]


def test_distinct_log_count_counts_entries_sharing_the_latest_serial() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=_ENTRIES)

    collector = CrtShCollector(http_client=_client(httpx.MockTransport(handler)), now=lambda: _NOW)
    assert collector.distinct_log_count(DomainName.parse("example.com")) == 2


def test_no_certificates_returns_empty() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=[])

    collector = CrtShCollector(http_client=_client(httpx.MockTransport(handler)), now=lambda: _NOW)
    assert collector.collect_certificates(DomainName.parse("example.com")) == []
    assert collector.distinct_log_count(DomainName.parse("example.com")) == 0


def test_404_returns_empty_not_an_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404)

    collector = CrtShCollector(http_client=_client(httpx.MockTransport(handler)), now=lambda: _NOW)
    assert collector.collect_certificates(DomainName.parse("example.com")) == []


def test_network_failure_raises_collector_unavailable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("boom")

    collector = CrtShCollector(http_client=_client(httpx.MockTransport(handler)), now=lambda: _NOW)
    with pytest.raises(CollectorUnavailableError):
        collector.collect_certificates(DomainName.parse("example.com"))


def test_invalid_json_raises_collector_unavailable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"not json")

    collector = CrtShCollector(http_client=_client(httpx.MockTransport(handler)), now=lambda: _NOW)
    with pytest.raises(CollectorUnavailableError):
        collector.collect_certificates(DomainName.parse("example.com"))


def test_unexpected_response_shape_raises_collector_unavailable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"unexpected": "shape"})

    collector = CrtShCollector(http_client=_client(httpx.MockTransport(handler)), now=lambda: _NOW)
    with pytest.raises(CollectorUnavailableError):
        collector.collect_certificates(DomainName.parse("example.com"))
