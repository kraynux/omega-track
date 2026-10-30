# Copyright (c) 2026 kraynux - Licence MIT
"""Implementation reelle de ArchiveCollector (Phase 10) via l'API CDX
publique de la Wayback Machine (`web.archive.org/cdx/search/cdx`). Meme
prudence de robustesse que crt.sh (docs/DATA_SOURCES.md : "rate-limiting
informel... meme traitement de robustesse") - seule une indisponibilite
totale leve CollectorUnavailableError.

Format CDX ("output=json") : la PREMIERE ligne du tableau est un en-tete
de colonnes (`["urlkey","timestamp","original",...]`), pas une entree -
piege reel de ce format, gere explicitement ici plutot que suppose."""
from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any

import httpx

from omega_track.application.exceptions import CollectorUnavailableError
from omega_track.core.enums import ConfidenceLevel
from omega_track.domain.entities.findings.history import HistoryFindingType
from omega_track.domain.value_objects.collected_record import CollectedRecord
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.shared.i18n import _

SOURCE_NAME = "wayback"
_CDX_URL = "https://web.archive.org/cdx/search/cdx"
_MAX_SNAPSHOTS = 50
"""Limite raisonnable par domaine - la Wayback Machine peut porter des
milliers de snapshots pour un domaine populaire, non pertinent au-dela
d'un echantillon pour une timeline (plan de dev §8 point 3 "carte de
chemin"/timeline, pas un miroir complet)."""


class WaybackCollector:
    """Implemente ports/collectors/archive_collector.py::ArchiveCollector."""

    def __init__(self, *, http_client: httpx.Client, now: Callable[[], datetime]) -> None:
        self._http_client = http_client
        self._now = now

    def collect_snapshots(self, domain: DomainName) -> list[CollectedRecord]:
        rows = self._fetch(domain)
        if not rows:
            return []

        header, *data_rows = rows
        try:
            timestamp_index = header.index("timestamp")
            original_index = header.index("original")
            status_index = header.index("statuscode")
        except ValueError as exc:
            raise CollectorUnavailableError(SOURCE_NAME, _("en-tête CDX inattendu")) from exc

        now = self._now()
        records = []
        for row in data_rows[:_MAX_SNAPSHOTS]:
            records.append(
                CollectedRecord(
                    finding_type=HistoryFindingType.ARCHIVE_SNAPSHOT.value,
                    payload={
                        "timestamp": row[timestamp_index],
                        "original_url": row[original_index],
                        "status_code": row[status_index],
                    },
                    confidence=ConfidenceLevel.DECLARED,
                    source_name=SOURCE_NAME,
                    observed_at=now,
                )
            )
        return records

    def _fetch(self, domain: DomainName) -> list[list[str]]:
        params = {"url": str(domain), "output": "json", "collapse": "timestamp:8", "limit": str(_MAX_SNAPSHOTS)}
        try:
            response = self._http_client.get(_CDX_URL, params=params)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise CollectorUnavailableError(SOURCE_NAME, str(exc)) from exc

        if not response.content:
            return []

        try:
            payload: Any = response.json()
        except ValueError as exc:
            raise CollectorUnavailableError(SOURCE_NAME, _("réponse JSON invalide")) from exc

        if not isinstance(payload, list):
            raise CollectorUnavailableError(SOURCE_NAME, _("forme de réponse inattendue"))
        return payload
