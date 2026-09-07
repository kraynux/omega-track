# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from datetime import datetime, timezone

import httpx
import pytest

from omega_track.application.exceptions import CollectorUnavailableError
from omega_track.domain.value_objects.ip_address import IPAddress
from omega_track.infrastructure.collectors.bgp.ripe_stat_collector import RipeStatCollector

_NOW = datetime(2026, 9, 6, tzinfo=timezone.utc)


def _client(handler: httpx.MockTransport) -> httpx.Client:
    return httpx.Client(transport=handler)


def test_collect_announcements_produces_one_asn_finding_per_asn() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert "stat.ripe.net" in str(request.url)
        return httpx.Response(200, json={"status": "ok", "data": {"asns": [13335, 64512], "prefix": "1.1.1.0/24"}})

    collector = RipeStatCollector(http_client=_client(httpx.MockTransport(handler)), now=lambda: _NOW)
    records = collector.collect_announcements(IPAddress.parse("1.1.1.1"))

    assert len(records) == 2
    assert all(r.finding_type == "network.asn" for r in records)
    assert {r.payload["asn"] for r in records} == {13335, 64512}
    assert all(r.payload["prefix"] == "1.1.1.0/24" for r in records)
    assert all(r.confidence.value == "declared" for r in records)


def test_status_not_ok_returns_empty() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"status": "error", "data": None})

    collector = RipeStatCollector(http_client=_client(httpx.MockTransport(handler)), now=lambda: _NOW)
    assert collector.collect_announcements(IPAddress.parse("1.1.1.1")) == []


def test_no_asns_returns_empty() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"status": "ok", "data": {"asns": [], "prefix": None}})

    collector = RipeStatCollector(http_client=_client(httpx.MockTransport(handler)), now=lambda: _NOW)
    assert collector.collect_announcements(IPAddress.parse("1.1.1.1")) == []


def test_network_failure_raises_collector_unavailable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("boom")

    collector = RipeStatCollector(http_client=_client(httpx.MockTransport(handler)), now=lambda: _NOW)
    with pytest.raises(CollectorUnavailableError):
        collector.collect_announcements(IPAddress.parse("1.1.1.1"))


def test_server_error_raises_collector_unavailable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503)

    collector = RipeStatCollector(http_client=_client(httpx.MockTransport(handler)), now=lambda: _NOW)
    with pytest.raises(CollectorUnavailableError):
        collector.collect_announcements(IPAddress.parse("1.1.1.1"))


def test_invalid_json_raises_collector_unavailable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"not json")

    collector = RipeStatCollector(http_client=_client(httpx.MockTransport(handler)), now=lambda: _NOW)
    with pytest.raises(CollectorUnavailableError):
        collector.collect_announcements(IPAddress.parse("1.1.1.1"))


def test_unexpected_response_shape_raises_collector_unavailable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=["not", "a", "dict"])

    collector = RipeStatCollector(http_client=_client(httpx.MockTransport(handler)), now=lambda: _NOW)
    with pytest.raises(CollectorUnavailableError):
        collector.collect_announcements(IPAddress.parse("1.1.1.1"))
