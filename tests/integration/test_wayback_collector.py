# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from datetime import datetime, timezone

import httpx
import pytest

from omega_track.application.exceptions import CollectorUnavailableError
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.infrastructure.collectors.archives.wayback_collector import WaybackCollector

_NOW = datetime(2026, 9, 6, tzinfo=timezone.utc)

_CDX_ROWS = [
    ["urlkey", "timestamp", "original", "mimetype", "statuscode", "digest", "length"],
    ["com,example)/", "20200101000000", "http://example.com/", "text/html", "200", "ABC123", "1024"],
    ["com,example)/", "20210601000000", "http://example.com/", "text/html", "200", "DEF456", "2048"],
]


def _client(handler: httpx.MockTransport) -> httpx.Client:
    return httpx.Client(transport=handler)


def test_collect_snapshots_skips_header_row() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert "web.archive.org" in str(request.url)
        return httpx.Response(200, json=_CDX_ROWS)

    collector = WaybackCollector(http_client=_client(httpx.MockTransport(handler)), now=lambda: _NOW)
    records = collector.collect_snapshots(DomainName.parse("example.com"))

    assert len(records) == 2
    assert all(r.finding_type == "history.archive_snapshot" for r in records)
    assert records[0].payload == {
        "timestamp": "20200101000000", "original_url": "http://example.com/", "status_code": "200"
    }


def test_no_snapshots_returns_empty_on_empty_body() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"")

    collector = WaybackCollector(http_client=_client(httpx.MockTransport(handler)), now=lambda: _NOW)
    assert collector.collect_snapshots(DomainName.parse("example.com")) == []


def test_only_header_row_returns_empty() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=[_CDX_ROWS[0]])

    collector = WaybackCollector(http_client=_client(httpx.MockTransport(handler)), now=lambda: _NOW)
    assert collector.collect_snapshots(DomainName.parse("example.com")) == []


def test_network_failure_raises_collector_unavailable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("boom")

    collector = WaybackCollector(http_client=_client(httpx.MockTransport(handler)), now=lambda: _NOW)
    with pytest.raises(CollectorUnavailableError):
        collector.collect_snapshots(DomainName.parse("example.com"))


def test_server_error_raises_collector_unavailable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(503)

    collector = WaybackCollector(http_client=_client(httpx.MockTransport(handler)), now=lambda: _NOW)
    with pytest.raises(CollectorUnavailableError):
        collector.collect_snapshots(DomainName.parse("example.com"))


def test_invalid_json_raises_collector_unavailable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"not json")

    collector = WaybackCollector(http_client=_client(httpx.MockTransport(handler)), now=lambda: _NOW)
    with pytest.raises(CollectorUnavailableError):
        collector.collect_snapshots(DomainName.parse("example.com"))


def test_caps_snapshots_at_max_limit() -> None:
    rows = [_CDX_ROWS[0]] + [
        ["com,example)/", f"2020010{i}000000", "http://example.com/", "text/html", "200", f"HASH{i}", "1024"]
        for i in range(60)
    ]

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=rows)

    collector = WaybackCollector(http_client=_client(httpx.MockTransport(handler)), now=lambda: _NOW)
    records = collector.collect_snapshots(DomainName.parse("example.com"))
    assert len(records) == 50
