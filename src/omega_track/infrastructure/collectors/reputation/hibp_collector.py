# Copyright (c) 2026 kraynux - Licence MIT
"""Implementation reelle de ReputationCollector (Phase 12) via l'API
publique HIBP v3 (`GET /api/v3/breacheddomain/{domain}`, headers
`hibp-api-key` + `User-Agent` obligatoire selon la doc HIBP). **Source
payante** depuis le changement de politique HIBP de 2022
(docs/DATA_SOURCES.md) - ce collecteur ne fait aucune hypothese sur la
gratuite, il consomme simplement la cle deja configuree par
l'utilisateur (l'avertissement "payant" est affiche cote configuration,
voir application/queries/get_source_disclosure.py, pas ici).

Meme discipline D-015 que les autres collecteurs : un domaine sans
breach connue (404) n'est jamais une erreur, simplement aucune donnee."""
from __future__ import annotations

from collections.abc import Callable
from datetime import datetime

import httpx

from omega_track.application.exceptions import CollectorUnavailableError, QuotaExceededError
from omega_track.core.enums import ConfidenceLevel
from omega_track.domain.entities.findings.reputation import ReputationFindingType
from omega_track.domain.value_objects.collected_record import CollectedRecord
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.shared.i18n import _

SOURCE_NAME = "hibp"

_API_URL = "https://haveibeenpwned.com/api/v3/breacheddomain"


class HibpHttpCollector:
    """Implemente ports/collectors/reputation_collector.py::ReputationCollector."""

    def __init__(self, *, http_client: httpx.Client, api_key: str, now: Callable[[], datetime]) -> None:
        self._http_client = http_client
        self._api_key = api_key
        self._now = now

    def collect_domain_reputation(self, domain: DomainName) -> list[CollectedRecord]:
        payload = self._fetch(domain)
        if not payload:
            return []

        breach_names = sorted({name for names in payload.values() for name in names})
        return [
            CollectedRecord(
                finding_type=ReputationFindingType.VERDICT.value,
                payload={
                    "source": SOURCE_NAME,
                    "breach_count": len(breach_names),
                    "breaches": breach_names,
                    "affected_aliases": len(payload),
                },
                confidence=ConfidenceLevel.DECLARED,
                source_name=SOURCE_NAME,
                observed_at=self._now(),
            )
        ]

    def _fetch(self, domain: DomainName) -> dict[str, list[str]] | None:
        try:
            response = self._http_client.get(
                f"{_API_URL}/{domain}",
                headers={"hibp-api-key": self._api_key, "User-Agent": "omega-track"},
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
