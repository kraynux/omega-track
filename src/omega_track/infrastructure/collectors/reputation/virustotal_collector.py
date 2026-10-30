# Copyright (c) 2026 kraynux - Licence MIT
"""Implementation reelle de ReputationCollector (Phase 12) via l'API
publique VirusTotal v3 (`GET /api/v3/domains/{domain}`, header
`x-apikey`). Meme discipline D-015 que les collecteurs sans cle : seule
une indisponibilite totale (reseau, JSON invalide, cle refusee) leve
CollectorUnavailableError - un domaine jamais vu par VirusTotal (404)
n'est jamais une erreur, simplement aucune donnee.

429 (quota depasse) leve QuotaExceededError, distinct de
CollectorUnavailableError (plan de dev §12) : la source repond, c'est la
limite d'usage qui est atteinte - application/orchestrators/phases/
reputation_phase.py enregistre un backoff persistant sur cette exception
precise, jamais sur un simple echec generique."""
from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any

import httpx

from omega_track.application.exceptions import CollectorUnavailableError, QuotaExceededError
from omega_track.core.enums import ConfidenceLevel
from omega_track.domain.entities.findings.reputation import ReputationFindingType
from omega_track.domain.value_objects.collected_record import CollectedRecord
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.shared.i18n import _

SOURCE_NAME = "virustotal"

_API_BASE = "https://www.virustotal.com/api/v3"


class VirusTotalHttpCollector:
    """Implemente ports/collectors/reputation_collector.py::ReputationCollector."""

    def __init__(self, *, http_client: httpx.Client, api_key: str, now: Callable[[], datetime]) -> None:
        self._http_client = http_client
        self._api_key = api_key
        self._now = now

    def collect_domain_reputation(self, domain: DomainName) -> list[CollectedRecord]:
        payload = self._fetch(domain)
        if payload is None:
            return []

        attributes = payload.get("data", {}).get("attributes", {})
        stats = attributes.get("last_analysis_stats")
        if not isinstance(stats, dict):
            return []

        return [
            CollectedRecord(
                finding_type=ReputationFindingType.VERDICT.value,
                payload={
                    "source": SOURCE_NAME,
                    "malicious": stats.get("malicious", 0),
                    "suspicious": stats.get("suspicious", 0),
                    "harmless": stats.get("harmless", 0),
                    "undetected": stats.get("undetected", 0),
                    "reputation_score": attributes.get("reputation"),
                },
                confidence=ConfidenceLevel.DECLARED,
                source_name=SOURCE_NAME,
                observed_at=self._now(),
            )
        ]

    def _fetch(self, domain: DomainName) -> dict[str, Any] | None:
        try:
            response = self._http_client.get(
                f"{_API_BASE}/domains/{domain}", headers={"x-apikey": self._api_key}
            )
        except httpx.HTTPError as exc:
            raise CollectorUnavailableError(SOURCE_NAME, str(exc)) from exc

        if response.status_code == 404:
            return None
        if response.status_code == 429:
            raise QuotaExceededError(SOURCE_NAME)
        if response.status_code >= 400:
            raise CollectorUnavailableError(SOURCE_NAME, _("erreur HTTP ({status_code})").format(status_code=response.status_code))

        try:
            payload = response.json()
        except ValueError as exc:
            raise CollectorUnavailableError(SOURCE_NAME, _("réponse JSON invalide")) from exc

        if not isinstance(payload, dict):
            raise CollectorUnavailableError(SOURCE_NAME, _("forme de réponse inattendue"))
        return payload
