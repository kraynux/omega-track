# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from datetime import datetime, timezone

import httpx
import pytest

from omega_track.application.exceptions import CollectorUnavailableError
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.domain.value_objects.ip_address import IPAddress
from omega_track.infrastructure.collectors.rdap.http_rdap_collector import HttpRdapCollector

_NOW = datetime(2026, 9, 6, tzinfo=timezone.utc)

_DOMAIN_RESPONSE = {
    "ldhName": "EXAMPLE.COM",
    "events": [
        {"eventAction": "registration", "eventDate": "2020-01-01T00:00:00Z"},
        {"eventAction": "expiration", "eventDate": "2030-01-01T00:00:00Z"},
        {"eventAction": "last changed", "eventDate": "2025-06-01T00:00:00Z"},
        {"eventAction": "transfer", "eventDate": "2024-01-01T00:00:00Z"},
    ],
    "nameservers": [{"ldhName": "NS1.EXAMPLE.COM."}, {"ldhName": "NS2.EXAMPLE.COM."}],
    "entities": [
        {
            "roles": ["registrar"],
            "handle": "REGISTRAR-1",
            "vcardArray": ["vcard", [["version", {}, "text", "4.0"], ["fn", {}, "text", "Example Registrar"]]],
        },
        {
            "roles": ["registrant"],
            "vcardArray": [
                "vcard",
                [
                    ["fn", {}, "text", "John Doe"],
                    ["email", {}, "text", "john@example.com"],
                ],
            ],
        },
    ],
}

_IP_RESPONSE = {
    "handle": "NET-93-184-216-0-1",
    "name": "EXAMPLE-NET",
    "country": "US",
    "startAddress": "93.184.216.0",
    "endAddress": "93.184.216.255",
    "events": [{"eventAction": "last changed", "eventDate": "2022-01-01T00:00:00Z"}],
}


def _client(handler: httpx.MockTransport) -> httpx.Client:
    return httpx.Client(transport=handler)


def test_collect_domain_registration_extracts_events_nameservers_and_entities() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == "https://rdap.org/domain/example.com"
        return httpx.Response(200, json=_DOMAIN_RESPONSE)

    collector = HttpRdapCollector(http_client=_client(httpx.MockTransport(handler)), now=lambda: _NOW)
    records = collector.collect_domain_registration(DomainName.parse("example.com"))

    by_type: dict[str, list[dict]] = {}
    for record in records:
        by_type.setdefault(record.finding_type, []).append(record.payload)

    assert by_type["identity.creation_date"] == [{"date": "2020-01-01T00:00:00Z"}]
    assert by_type["identity.expiration_date"] == [{"date": "2030-01-01T00:00:00Z"}]
    assert by_type["identity.updated_date"] == [{"date": "2025-06-01T00:00:00Z"}]
    assert "identity.transfer_date" not in by_type
    assert {"name": "ns1.example.com"} in by_type["identity.nameserver"]
    assert {"name": "ns2.example.com"} in by_type["identity.nameserver"]
    assert by_type["identity.registrar"] == [{"name": "Example Registrar"}]
    assert by_type["identity.registrant_contact"] == [{"name": "John Doe", "email": "john@example.com"}]


def test_collect_ip_registration_extracts_netblock_and_events() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == "https://rdap.org/ip/93.184.216.34"
        return httpx.Response(200, json=_IP_RESPONSE)

    collector = HttpRdapCollector(http_client=_client(httpx.MockTransport(handler)), now=lambda: _NOW)
    records = collector.collect_ip_registration(IPAddress.parse("93.184.216.34"))

    by_type = {r.finding_type: r.payload for r in records}
    assert by_type["network.netblock"] == {
        "handle": "NET-93-184-216-0-1",
        "name": "EXAMPLE-NET",
        "country": "US",
        "start_address": "93.184.216.0",
        "end_address": "93.184.216.255",
    }
    assert by_type["identity.updated_date"] == {"date": "2022-01-01T00:00:00Z"}


def test_missing_individual_fields_never_raise_and_are_simply_omitted() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"ldhName": "EXAMPLE.COM"})

    collector = HttpRdapCollector(http_client=_client(httpx.MockTransport(handler)), now=lambda: _NOW)
    records = collector.collect_domain_registration(DomainName.parse("example.com"))
    assert records == []


def test_404_means_no_data_not_an_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404)

    collector = HttpRdapCollector(http_client=_client(httpx.MockTransport(handler)), now=lambda: _NOW)
    assert collector.collect_domain_registration(DomainName.parse("example.com")) == []


def test_429_raises_collector_unavailable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429)

    collector = HttpRdapCollector(http_client=_client(httpx.MockTransport(handler)), now=lambda: _NOW)
    with pytest.raises(CollectorUnavailableError):
        collector.collect_domain_registration(DomainName.parse("example.com"))


def test_server_error_raises_collector_unavailable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503)

    collector = HttpRdapCollector(http_client=_client(httpx.MockTransport(handler)), now=lambda: _NOW)
    with pytest.raises(CollectorUnavailableError):
        collector.collect_ip_registration(IPAddress.parse("93.184.216.34"))


def test_network_failure_raises_collector_unavailable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("boom")

    collector = HttpRdapCollector(http_client=_client(httpx.MockTransport(handler)), now=lambda: _NOW)
    with pytest.raises(CollectorUnavailableError):
        collector.collect_domain_registration(DomainName.parse("example.com"))


def test_invalid_json_raises_collector_unavailable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"not json")

    collector = HttpRdapCollector(http_client=_client(httpx.MockTransport(handler)), now=lambda: _NOW)
    with pytest.raises(CollectorUnavailableError):
        collector.collect_domain_registration(DomainName.parse("example.com"))


def test_timeout_seconds_is_forwarded_to_the_http_client() -> None:
    seen_timeouts: list[object] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen_timeouts.append(request.extensions.get("timeout"))
        return httpx.Response(200, json={"ldhName": "EXAMPLE.COM"})

    collector = HttpRdapCollector(
        http_client=_client(httpx.MockTransport(handler)), now=lambda: _NOW, timeout_seconds=5.0
    )
    collector.collect_domain_registration(DomainName.parse("example.com"))

    assert seen_timeouts == [{"connect": 5.0, "read": 5.0, "write": 5.0, "pool": 5.0}]


def test_no_timeout_override_when_timeout_seconds_is_none() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"ldhName": "EXAMPLE.COM"})

    collector = HttpRdapCollector(http_client=_client(httpx.MockTransport(handler)), now=lambda: _NOW)
    # ne doit pas lever - simple non-regression du chemin par defaut
    collector.collect_domain_registration(DomainName.parse("example.com"))
