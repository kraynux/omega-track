# Copyright (c) 2026 kraynux - Licence MIT
from __future__ import annotations

from datetime import datetime, timezone

import httpx
import pytest

from omega_track.application.exceptions import CollectorUnavailableError, QuotaExceededError
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.infrastructure.collectors.reputation.virustotal_collector import (
    VirusTotalHttpCollector,
)

_NOW = datetime(2026, 9, 7, tzinfo=timezone.utc)


def _client(handler: httpx.MockTransport) -> httpx.Client:
    return httpx.Client(transport=handler)


def test_collect_domain_reputation_produces_a_verdict_finding() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.headers["x-apikey"] == "secret-key"
        assert "domains/example.com" in str(request.url)
        return httpx.Response(
            200,
            json={
                "data": {
                    "attributes": {
                        "last_analysis_stats": {
                            "malicious": 2, "suspicious": 1, "harmless": 60, "undetected": 5,
                        },
                        "reputation": -3,
                    }
                }
            },
        )

    collector = VirusTotalHttpCollector(
        http_client=_client(httpx.MockTransport(handler)), api_key="secret-key", now=lambda: _NOW
    )
    records = collector.collect_domain_reputation(DomainName.parse("example.com"))

    assert len(records) == 1
    assert records[0].finding_type == "reputation.verdict"
    assert records[0].payload["malicious"] == 2
    assert records[0].payload["reputation_score"] == -3


def test_unknown_domain_returns_empty_not_an_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404)

    collector = VirusTotalHttpCollector(
        http_client=_client(httpx.MockTransport(handler)), api_key="secret-key", now=lambda: _NOW
    )
    assert collector.collect_domain_reputation(DomainName.parse("example.com")) == []


def test_quota_exceeded_raises_quota_exceeded_error() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429)

    collector = VirusTotalHttpCollector(
        http_client=_client(httpx.MockTransport(handler)), api_key="secret-key", now=lambda: _NOW
    )
    with pytest.raises(QuotaExceededError):
        collector.collect_domain_reputation(DomainName.parse("example.com"))


def test_invalid_key_raises_collector_unavailable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401)

    collector = VirusTotalHttpCollector(
        http_client=_client(httpx.MockTransport(handler)), api_key="bad-key", now=lambda: _NOW
    )
    with pytest.raises(CollectorUnavailableError):
        collector.collect_domain_reputation(DomainName.parse("example.com"))


def test_network_failure_raises_collector_unavailable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("boom")

    collector = VirusTotalHttpCollector(
        http_client=_client(httpx.MockTransport(handler)), api_key="secret-key", now=lambda: _NOW
    )
    with pytest.raises(CollectorUnavailableError):
        collector.collect_domain_reputation(DomainName.parse("example.com"))


def test_invalid_json_raises_collector_unavailable() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, content=b"not json")

    collector = VirusTotalHttpCollector(
        http_client=_client(httpx.MockTransport(handler)), api_key="secret-key", now=lambda: _NOW
    )
    with pytest.raises(CollectorUnavailableError):
        collector.collect_domain_reputation(DomainName.parse("example.com"))


def test_missing_analysis_stats_returns_empty() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"data": {"attributes": {}}})

    collector = VirusTotalHttpCollector(
        http_client=_client(httpx.MockTransport(handler)), api_key="secret-key", now=lambda: _NOW
    )
    assert collector.collect_domain_reputation(DomainName.parse("example.com")) == []
