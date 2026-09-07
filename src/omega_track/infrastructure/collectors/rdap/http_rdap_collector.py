# Copyright (c) 2026 kraynux - Licence MIT
"""Implementation reelle de RdapCollector (Phase 6) via le redirecteur
public rdap.org (resout vers le serveur RDAP faisant autorite pour la
cible - evite d'implementer nous-memes le bootstrap IANA complet).
URL/schema verifies a l'ecriture de ce module (2026-09) - a revalider
avant la v1.0 si rdap.org change de comportement, meme prudence que
docs/DATA_SOURCES.md.

Un champ RDAP individuel absent n'est jamais une erreur (D-015) : chaque
extracteur renvoie simplement moins de CollectedRecord plutot que lever.
Seule une indisponibilite totale de la source (reseau, 429, 5xx, JSON
invalide) leve CollectorUnavailableError."""
from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from typing import Any

import httpx

from omega_track.application.exceptions import CollectorUnavailableError
from omega_track.core.enums import ConfidenceLevel
from omega_track.domain.entities.findings.identity import IdentityFindingType
from omega_track.domain.entities.findings.network import NetworkFindingType
from omega_track.domain.value_objects.collected_record import CollectedRecord
from omega_track.domain.value_objects.domain_name import DomainName
from omega_track.domain.value_objects.ip_address import IPAddress

SOURCE_NAME = "rdap"

_EVENT_TO_FINDING_TYPE = {
    "registration": IdentityFindingType.CREATION_DATE,
    "expiration": IdentityFindingType.EXPIRATION_DATE,
    "last changed": IdentityFindingType.UPDATED_DATE,
}


class HttpRdapCollector:
    """Implemente ports/collectors/rdap_collector.py::RdapCollector."""

    def __init__(
        self,
        *,
        http_client: httpx.Client,
        now: Callable[[], datetime],
        timeout_seconds: float | None = None,
    ) -> None:
        """`timeout_seconds` (Phase 7, `ExecutionLimits.module_timeout_seconds`) -
        transmis tel quel a httpx par requete ; None conserve le timeout
        par defaut du `http_client` fourni, jamais impose de force."""
        self._http_client = http_client
        self._now = now
        self._timeout_seconds = timeout_seconds

    def collect_domain_registration(self, domain: DomainName) -> list[CollectedRecord]:
        data = self._fetch(f"https://rdap.org/domain/{domain}")
        if data is None:
            return []
        return (
            _extract_events(data, now=self._now())
            + _extract_nameservers(data, now=self._now())
            + _extract_entity_records(data, now=self._now())
        )

    def collect_ip_registration(self, ip: IPAddress) -> list[CollectedRecord]:
        data = self._fetch(f"https://rdap.org/ip/{ip}")
        if data is None:
            return []
        return (
            _extract_events(data, now=self._now())
            + _extract_netblock(data, now=self._now())
            + _extract_entity_records(data, now=self._now())
        )

    def _fetch(self, url: str) -> dict[str, Any] | None:
        try:
            if self._timeout_seconds is None:
                response = self._http_client.get(url)
            else:
                response = self._http_client.get(url, timeout=self._timeout_seconds)
        except httpx.HTTPError as exc:
            raise CollectorUnavailableError(SOURCE_NAME, str(exc)) from exc

        if response.status_code == 404:
            return None
        if response.status_code == 429:
            raise CollectorUnavailableError(SOURCE_NAME, "limite de requetes atteinte (429)")
        if response.status_code >= 500:
            raise CollectorUnavailableError(SOURCE_NAME, f"erreur serveur ({response.status_code})")

        try:
            payload = response.json()
        except ValueError as exc:
            raise CollectorUnavailableError(SOURCE_NAME, "reponse JSON invalide") from exc
        return dict(payload) if isinstance(payload, dict) else None


def _extract_events(data: dict[str, Any], *, now: datetime) -> list[CollectedRecord]:
    records = []
    for event in data.get("events") or []:
        finding_type = _EVENT_TO_FINDING_TYPE.get(event.get("eventAction"))
        date = event.get("eventDate")
        if finding_type is None or not date:
            continue
        records.append(
            CollectedRecord(
                finding_type=finding_type.value,
                payload={"date": date},
                confidence=ConfidenceLevel.DECLARED,
                source_name=SOURCE_NAME,
                observed_at=now,
            )
        )
    return records


def _extract_nameservers(data: dict[str, Any], *, now: datetime) -> list[CollectedRecord]:
    records = []
    for nameserver in data.get("nameservers") or []:
        name = nameserver.get("ldhName")
        if not name:
            continue
        records.append(
            CollectedRecord(
                finding_type=IdentityFindingType.NAMESERVER.value,
                payload={"name": name.rstrip(".").lower()},
                confidence=ConfidenceLevel.DECLARED,
                source_name=SOURCE_NAME,
                observed_at=now,
            )
        )
    return records


def _extract_netblock(data: dict[str, Any], *, now: datetime) -> list[CollectedRecord]:
    handle = data.get("handle")
    start = data.get("startAddress")
    end = data.get("endAddress")
    if not (handle or start or end):
        return []
    payload = {
        key: value
        for key, value in {
            "handle": handle,
            "name": data.get("name"),
            "country": data.get("country"),
            "start_address": start,
            "end_address": end,
        }.items()
        if value is not None
    }
    return [
        CollectedRecord(
            finding_type=NetworkFindingType.NETBLOCK.value,
            payload=payload,
            confidence=ConfidenceLevel.DECLARED,
            source_name=SOURCE_NAME,
            observed_at=now,
        )
    ]


def _extract_entity_records(data: dict[str, Any], *, now: datetime) -> list[CollectedRecord]:
    records = []
    for entity in data.get("entities") or []:
        roles = entity.get("roles") or []
        vcard = entity.get("vcardArray")
        if "registrar" in roles:
            name = _vcard_field(vcard, "fn")
            records.append(
                CollectedRecord(
                    finding_type=IdentityFindingType.REGISTRAR.value,
                    payload={"name": name or entity.get("handle")},
                    confidence=ConfidenceLevel.DECLARED,
                    source_name=SOURCE_NAME,
                    observed_at=now,
                )
            )
        if "registrant" in roles:
            name = _vcard_field(vcard, "fn")
            email = _vcard_field(vcard, "email")
            if name or email:
                payload = {k: v for k, v in {"name": name, "email": email}.items() if v is not None}
                records.append(
                    CollectedRecord(
                        finding_type=IdentityFindingType.REGISTRANT_CONTACT.value,
                        payload=payload,
                        confidence=ConfidenceLevel.DECLARED,
                        source_name=SOURCE_NAME,
                        observed_at=now,
                    )
                )
    return records


def _vcard_field(vcard_array: Any, field_name: str) -> str | None:
    """Format RDAP jCard : `["vcard", [["fn", {}, "text", "John Doe"], ...]]`."""
    if not isinstance(vcard_array, list) or len(vcard_array) < 2:
        return None
    entries = vcard_array[1]
    if not isinstance(entries, list):
        return None
    for entry in entries:
        if isinstance(entry, list) and len(entry) >= 4 and entry[0] == field_name:
            value = entry[3]
            return str(value) if value is not None else None
    return None
