# Copyright (c) 2026 kraynux - Licence MIT
"""Implementation reelle de BgpCollector (Phase 10) via l'API publique
RIPEstat (`stat.ripe.net/data/network-info`) : ASN(s) annoncant le
prefixe couvrant une IP donnee. Produit toujours un Finding brut
(`network.asn`) - **jamais une Relation automatique** (D-011, angle mort
2) : un ASN commun entre deux IPs reste une simple donnee observee ici,
la promotion en Relation (si corroboree par un second signal) est
l'exclusivite de domain/services/correlation_engine.py, jamais de ce
collecteur."""
from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any

import httpx

from omega_track.application.exceptions import CollectorUnavailableError
from omega_track.core.enums import ConfidenceLevel
from omega_track.domain.entities.findings.network import NetworkFindingType
from omega_track.domain.value_objects.collected_record import CollectedRecord
from omega_track.domain.value_objects.ip_address import IPAddress
from omega_track.shared.i18n import _

SOURCE_NAME = "ripestat"
_NETWORK_INFO_URL = "https://stat.ripe.net/data/network-info/data.json"


class RipeStatCollector:
    """Implemente ports/collectors/bgp_collector.py::BgpCollector."""

    def __init__(self, *, http_client: httpx.Client, now: Callable[[], datetime]) -> None:
        self._http_client = http_client
        self._now = now

    def collect_announcements(self, ip: IPAddress) -> list[CollectedRecord]:
        data = self._fetch(ip)
        if data is None:
            return []

        asns = data.get("asns") or []
        prefix = data.get("prefix")
        now = self._now()
        return [
            CollectedRecord(
                finding_type=NetworkFindingType.ASN.value,
                payload={"asn": asn, "prefix": prefix},
                confidence=ConfidenceLevel.DECLARED,
                source_name=SOURCE_NAME,
                observed_at=now,
            )
            for asn in asns
        ]

    def _fetch(self, ip: IPAddress) -> dict[str, Any] | None:
        try:
            response = self._http_client.get(_NETWORK_INFO_URL, params={"resource": str(ip)})
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise CollectorUnavailableError(SOURCE_NAME, str(exc)) from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise CollectorUnavailableError(SOURCE_NAME, _("réponse JSON invalide")) from exc

        if not isinstance(payload, dict):
            raise CollectorUnavailableError(SOURCE_NAME, _("forme de réponse inattendue"))

        status = payload.get("status")
        if status != "ok":
            return None
        data = payload.get("data")
        return data if isinstance(data, dict) else None
